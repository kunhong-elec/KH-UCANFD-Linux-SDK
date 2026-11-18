#!/usr/bin/env python3
#
# KCAN Auto Firmware Upgrade Script (Python Version)
# 
# This script automatically upgrades KCAN device firmware by:
# 1. Entering bootloader mode (device becomes USB mass storage)
# 2. Identifying the USB mass storage device
# 3. Copying firmware file to the device
# 4. Waiting for device to restart
# 5. Verifying the upgraded firmware version
#
# Usage: kcan_auto_upgrade.py <can_interface> <firmware_file> [options]
#
# Copyright (C) 2022-2026 Chengdu Kunhong Electronic Technology Co., Ltd

import os
import sys
import time
import subprocess
import shutil
import argparse
import stat
import re
import json
import tempfile

from kcan_firmware_release import (download_release, cached_release, default_cache_dir,
                                   list_cached_releases, ReleaseConnectionError, version_tuple, FIRMWARE_TYPES)
from pathlib import Path

# Color output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
FW_UPDATER = SCRIPT_DIR / "kcan_fw_tool"
MOUNT_POINT = Path("/tmp/kcan_upgrade_mount")
TIMEOUT_WAIT_USB = 30          # Wait up to 30 seconds for USB device to appear
TIMEOUT_WAIT_RESTART = 60      # Wait up to 60 seconds for device to restart
TIMEOUT_CHECK_INTERVAL = 2     # Check interval in seconds

# KCAN OTA USB device identification (sysfs + /dev/disk/by-id)
USB_VENDORS = ("34cc", "395e")
USB_ID_PRODUCT = "ffff"
ACTIVE_FIRMWARE = "kcan-x4"
NET_ROOT = Path("/sys/class/net")
USB_SERIES = {
    ("395e", "0020"): "kcan-x4", ("34cc", "0020"): "kcan-x4",
    ("0c72", "0011"): "pcanfd", ("0c72", "0012"): "pcanfd",
    ("0c72", "0014"): "pcanfd",
    ("0bfd", "0108"): "kvaser-fd", ("0bfd", "0114"): "kvaser-fd",
    ("1d50", "606f"): "gs-usb",
}


def updater_command(interface, command, *options):
    result = [str(FW_UPDATER)]
    if ACTIVE_FIRMWARE != "kcan-x4":
        result += ["--factory-timing", "modern"]
    return result + list(options) + [interface, command]

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")

def log_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}", file=sys.stderr)

def log_debug(msg, verbose=False):
    if verbose:
        print(f"{Colors.BLUE}[DEBUG]{Colors.NC} {msg}")

def run_cmd(cmd, check=True, capture_output=True, verbose=False):
    """Run shell command and return result"""
    log_debug(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}", verbose)
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else cmd.split(),
            check=check,
            capture_output=capture_output,
            text=True,
            timeout=30
        )
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        log_error(f"Command failed: {e}")
        if e.stdout:
            log_debug(f"stdout: {e.stdout}", verbose)
        if e.stderr:
            log_debug(f"stderr: {e.stderr}", verbose)
        raise
    except subprocess.TimeoutExpired:
        log_error("Command timed out")
        raise

def _read_usb_ids_from_sysfs(dev_name):
    """Walk up from /sys/block/sdX/device to find idVendor, idProduct."""
    device_path = Path(f"/sys/block/{dev_name}/device")
    if not device_path.exists() or not device_path.is_symlink():
        return None
    try:
        real = device_path.resolve()
        p = real
        while p != Path("/") and p.parts:
            v = p / "idVendor"
            pid = p / "idProduct"
            if v.exists() and pid.exists():
                vendor = v.read_text().strip()
                product = pid.read_text().strip()
                return (vendor, product)
            p = p.parent
    except Exception:
        pass
    return None

def find_upgrade_device(verbose=False):
    """Only accept a uniquely identified Kunhong OTA disk; never an arbitrary sdX."""
    matches = []
    for block in Path("/sys/block").glob("sd*"):
        ids = _read_usb_ids_from_sysfs(block.name)
        if ids and ids[0].lower() in USB_VENDORS and ids[1].lower() == USB_ID_PRODUCT:
            matches.append(Path("/dev") / block.name)
    if len(matches) > 1:
        raise RuntimeError("Multiple Kunhong OTA disks found; connect only the target device")
    return matches[0] if matches else None


def verify_ota_target(device, target):
    """Do not write another board's uniquely enumerated OTA disk."""
    path = (Path('/sys/block') / device.name / 'device').resolve()
    if runtime_targets():
        raise RuntimeError('A running CAN adapter is still present during OTA; refusing ambiguous target')
    if not any(str(parent) == target['path'] for parent in (path, *path.parents)):
        # VMware allocates a different virtual port to a changed USB identity.
        # The caller enforced a sole runtime adapter, no pre-existing OTA disk,
        # its disappearance, and exactly one new Kunhong OTA disk.
        log_warning('USB port changed during OTA enumeration; using the exclusive single-device transition')


def check_upgrade_dependencies():
    missing = [name for name in ("mount", "umount", "mountpoint", "sync") if not shutil.which(name)]
    if missing:
        raise RuntimeError("Missing required upgrade tools: " + ", ".join(missing))


def wait_for_usb_device(verbose=False):
    log_info(f"Waiting for the Kunhong OTA disk (timeout: {TIMEOUT_WAIT_USB}s)...")
    deadline = time.monotonic() + TIMEOUT_WAIT_USB
    udevadm = shutil.which("udevadm")
    if not udevadm:
        log_warning("udevadm is unavailable; polling sysfs and device nodes directly")
    while time.monotonic() < deadline:
        if udevadm:
            try:
                result = subprocess.run([udevadm, "settle", "--timeout=1"],
                                        capture_output=True, text=True, check=False,
                                        timeout=min(2.0, max(0.001, deadline - time.monotonic())))
                if result.returncode:
                    log_warning(f"udevadm settle returned {result.returncode}; continuing with sysfs polling")
                    log_debug(result.stderr.strip(), verbose)
                    udevadm = None
            except (OSError, subprocess.TimeoutExpired) as error:
                log_warning(f"udevadm settle is unavailable or timed out; continuing with sysfs polling: {error}")
                udevadm = None
        if time.monotonic() >= deadline:
            break
        device = find_upgrade_device(verbose)
        if device and device.exists():
            log_success(f"Found OTA disk: {device}")
            return device
        time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))
    raise RuntimeError("Timeout waiting for a uniquely identified Kunhong OTA disk")


def identify_interface(can_interface):
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,15}", can_interface):
        raise ValueError("Invalid CAN interface name")
    device = NET_ROOT / can_interface / "device"
    if not device.exists():
        raise ValueError(f"CAN interface not found: {can_interface}")
    current = device.resolve()
    while current != current.parent:
        if (current / "idVendor").exists() and (current / "idProduct").exists():
            vendor = (current / "idVendor").read_text().strip().lower()
            product = (current / "idProduct").read_text().strip().lower()
            firmware = USB_SERIES.get((vendor, product))
            if firmware is None:
                raise ValueError("Unsupported USB CAN interface")
            product_name = (current / "product").read_text().strip() if (current / "product").exists() else ""
            if firmware == "gs-usb" and not product_name.startswith("CANmeleon GS USB"):
                raise ValueError("GS USB device is not a CANmeleon device")
            serial = (current / "serial").read_text().strip() if (current / "serial").exists() else ""
            devnum = (current / "devnum").read_text().strip() if (current / "devnum").exists() else ""
            return {"path": str(current), "serial": serial, "devnum": devnum, "fw_type": firmware}
        current = current.parent
    raise ValueError("Cannot identify the USB device for " + can_interface)


def runtime_targets():
    targets = {}
    for net in NET_ROOT.iterdir():
        try:
            info = identify_interface(net.name)
            targets.setdefault(info['path'], []).append((int((net/'ifindex').read_text()), net.name, info))
        except (OSError, ValueError):
            continue
    return targets


def validate_online_target(can_interface):
    info = identify_interface(can_interface)
    if len(runtime_targets()) != 1:
        raise ValueError('Connect only the target USB CAN adapter before installation')
    return info


def verify_factory_identity(interface, verbose=False):
    """Public USB IDs identify a protocol, not a Kunhong board."""
    output = run_cmd(updater_command(interface, "sc"), verbose=verbose)
    if not re.search(r"\bSC:U1,C1\b", output):
        raise ValueError("KH factory identity/boot integrity check failed; refusing to enter OTA")


def find_restarted_interface(target, firmware):
    devices = runtime_targets()
    if len(devices) > 1:
        raise RuntimeError('Multiple USB CAN adapters appeared after installation')
    if not devices:
        return None
    _, interface, candidate = min(next(iter(devices.values())))
    if firmware is not None and candidate['fw_type'] != firmware:
        return None
    if target.get('devnum') and candidate['path'] == target['path'] and candidate['devnum'] == target['devnum']:
        return None
    return interface


def wait_for_target_restart(target, firmware, verbose=False):
    global ACTIVE_FIRMWARE
    if firmware is not None:
        ACTIVE_FIRMWARE = firmware
    deadline = time.monotonic() + TIMEOUT_WAIT_RESTART
    while time.monotonic() < deadline:
        interface = find_restarted_interface(target, firmware)
        if interface:
            try:
                # Local .enc/.kpcfg images have no release metadata. Select the
                # protocol from the re-enumerated device before any factory I/O.
                if firmware is None:
                    ACTIVE_FIRMWARE = identify_interface(interface)['fw_type']
                query_current_versions(interface, verbose)
                verify_factory_identity(interface, verbose)
                log_success(f"Target {ACTIVE_FIRMWARE} restarted on {interface}")
                return interface
            except (OSError, ValueError, subprocess.SubprocessError):
                pass
        time.sleep(TIMEOUT_CHECK_INTERVAL)
    raise RuntimeError("Timeout waiting for the selected device to restart with the target firmware")


def mount_upgrade_device(device, verbose=False):
    """Mount USB device"""
    log_info(f"Mounting device {device} to {MOUNT_POINT}...")
    
    # Create mount point
    MOUNT_POINT.mkdir(parents=True, exist_ok=True)
    
    # Unmount if already mounted
    try:
        run_cmd(["umount", str(MOUNT_POINT)], check=False, verbose=False)
    except:
        pass
    
    # Mount device
    try:
        uid = os.getuid()
        gid = os.getgid()
        run_cmd([
            "mount", "-t", "vfat", str(device), str(MOUNT_POINT),
            "-o", f"rw,nosuid,nodev,noexec,uid={uid},gid={gid}"
        ], verbose=verbose)
        log_success("Device mounted successfully")
        return True
    except Exception as e:
        log_error(f"Failed to mount device {device}: {e}")
        return False

def unmount_upgrade_device(verbose=False):
    def mounted():
        status = subprocess.run(["mountpoint", "-q", str(MOUNT_POINT)], capture_output=True).returncode
        # util-linux mountpoint: 0 = mounted, 32 = not a mount point,
        # 1 = invocation/permission/system error. Never treat an unknown state
        # as safe to remove or as a successful unmount.
        if status not in (0, 32):
            raise RuntimeError(f"Cannot determine OTA mount state (mountpoint exit {status})")
        return status == 0
    try:
        if not mounted():
            return True
        detail = ""
        for attempt in range(3):
            try:
                result = subprocess.run(["umount", str(MOUNT_POINT)], capture_output=True, text=True, timeout=30)
                detail = result.stderr.strip()
            except (OSError, subprocess.TimeoutExpired) as error:
                detail = str(error)
            # The OTA device may reboot during umount. A nonzero umount exit
            # alone does not prove the volume is still mounted; recheck it.
            if not mounted():
                log_debug("OTA volume is unmounted (device may already have restarted)", verbose)
                return True
            if attempt < 2:
                time.sleep(0.25)
        log_error(f"OTA volume remains mounted at {MOUNT_POINT}: {detail}")
        return False
    except Exception as error:
        log_error(f"Failed to unmount OTA disk: {error}")
        return False


def enter_bootloader_mode(can_interface, verbose=False):
    """Enter bootloader mode"""
    log_info(f"Entering bootloader mode on {can_interface}...")
    
    if not FW_UPDATER.exists():
        log_error(f"Firmware updater not found: {FW_UPDATER}")
        log_error(f"Please build it first: cd {FW_UPDATER.parent} && make")
        return False
    
    try:
        # Use non-interactive mode by passing -y to skip confirmation.
        # Options precede positionals, including with POSIXLY_CORRECT or musl.
        process = subprocess.run(
            updater_command(can_interface, "bl", "-y"),
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=15,
        )
        stdout, stderr = process.stdout, process.stderr
        if process.returncode == 0:
            log_success("Bootloader command sent, device should reset...")
            return True

        log_error("Bootloader command failed to trigger reset.")
        if verbose:
            log_error(f"stdout: {stdout}")
            log_error(f"stderr: {stderr}")
        else:
            log_debug(f"stdout: {stdout}", verbose)
            log_debug(f"stderr: {stderr}", verbose)
        return False
    except Exception as e:
        log_error(f"Failed to enter bootloader mode: {e}")
        return False

def copy_firmware(firmware_file, verbose=False):
    """Copy firmware file to device"""
    firmware_path = Path(firmware_file)
    dest_file = MOUNT_POINT / firmware_path.name
    
    log_info("Copying firmware file...")
    log_debug(f"Source: {firmware_path}", verbose)
    log_debug(f"Destination: {dest_file}", verbose)
    
    if not firmware_path.exists():
        log_error(f"Firmware file not found: {firmware_path}")
        return False
    
    try:
        # Copy file
        with firmware_path.open("rb") as source, dest_file.open("wb") as target:
            shutil.copyfileobj(source, target)
            target.flush()
            os.fsync(target.fileno())
        log_success("Firmware file copied successfully")
        
        # Sync to ensure data is written
        run_cmd(["sync"], verbose=False)
        log_debug("File system synced", verbose)

        # OTA upgrade media is write-only from the device point of view.
        # The device may reboot immediately, so the destination file may disappear.
        # Do not attempt to stat/verify dest_file.
        return True
    except Exception as e:
        log_error(f"Failed to copy firmware file: {e}")
        return False

def wait_for_device_restart(can_interface, verbose=False):
    """Wait for device to restart and CAN interface to reappear"""
    log_info("Waiting for device to restart and CAN interface to reappear...")
    log_info(f"This may take up to {TIMEOUT_WAIT_RESTART} seconds...")
    
    # The caller has already unmounted the OTA disk and removed its temporary
    # directory. Only wait for the device reset; do not inspect that path again.
    time.sleep(3)
    
    elapsed = 0
    while elapsed < TIMEOUT_WAIT_RESTART:
        # Check if CAN interface exists and is up
        try:
            run_cmd(["ip", "link", "show", can_interface], check=False, verbose=False)
            
            # Try to get version to verify device is ready
            query_current_versions(can_interface)
            verify_factory_identity(can_interface)
            log_success("Device restarted and CAN interface is ready")
            return True
        except:
            pass
        
        time.sleep(TIMEOUT_CHECK_INTERVAL)
        elapsed += TIMEOUT_CHECK_INTERVAL
        
        if elapsed % 10 == 0:
            log_info(f"Still waiting... ({elapsed}s/{TIMEOUT_WAIT_RESTART}s)")
    
    log_error("Timeout waiting for device restart")
    return False

def get_firmware_version(can_interface, verbose=False):
    """Get firmware version"""
    log_info("Getting firmware version...")
    
    try:
        output = run_cmd(updater_command(can_interface, "version"), verbose=verbose)
        print(output)
        return True
    except Exception as e:
        log_error(f"Failed to get firmware version: {e}")
        return False

def _parse_kcan_fw_tool_versions(version_output):
    """
    Parse `kcan_fw_tool <if> version` output.
    Expected output sections:
      === Firmware Version ===
        Version: X.Y.Z
      === BL Version ===
        Version: A.B.C.D
    """
    fw_m = re.search(
        r"===\s*Firmware Version\s*===.*?Version:\s*([0-9]+)\.([0-9]+)\.([0-9]+)",
        version_output,
        flags=re.S,
    )
    bl_m = re.search(
        r"===\s*BL Version\s*===.*?Version:\s*([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)",
        version_output,
        flags=re.S,
    )
    if not fw_m:
        raise ValueError("Failed to parse firmware version from kcan_fw_tool output")

    fw_ver = (int(fw_m.group(1)), int(fw_m.group(2)), int(fw_m.group(3)))
    if bl_m:
        bl_ver = (int(bl_m.group(1)), int(bl_m.group(2)), int(bl_m.group(3)), int(bl_m.group(4)))
        return fw_ver, bl_ver

    # Boot version is optional (older firmware may not implement GET_BOOT_VER).
    return fw_ver, None

def query_current_versions(can_interface, verbose=False):
    """Return (fw_ver_3_tuple, bl_ver_4_tuple)."""
    out = run_cmd(updater_command(can_interface, "version"), verbose=verbose)
    return _parse_kcan_fw_tool_versions(out)

def resolve_firmware_token(firmware_token, search_dir=None):
    """Resolve an explicit local file, or a unique filename/glob in a selected cache."""
    token = str(firmware_token).strip()
    path = Path(token)
    if path.is_file():
        return path.resolve()
    if search_dir is None or "/" in token:
        raise FileNotFoundError(f"Firmware file not found: {token}; provide an existing local file path")
    matches = sorted(path for path in Path(search_dir).glob(token.replace("**", "*")) if path.is_file())
    if not matches:
        raise FileNotFoundError(f"Firmware '{token}' not found under {search_dir}")
    if len(matches) != 1:
        names = ", ".join(path.name for path in matches)
        raise RuntimeError(f"Multiple firmware matched '{token}'. Please specify exact filename. Matches: {names}")
    return matches[0].resolve()


def select_install_release(args):
    try:
        return download_release(args.cache_dir, args.info_url, args.release_url, version=args.version, firmware=args.firmware)
    except ReleaseConnectionError as error:
        if args.version:
            cached = cached_release(args.cache_dir, version=args.version, firmware=args.firmware)
        else:
            cached = next(iter(list_cached_releases(args.cache_dir, firmware=args.firmware)), None)
        if cached is None:
            raise RuntimeError(f"Firmware download failed ({error}); no matching firmware cached in {args.cache_dir}") from error
        log_warning(f"Network unavailable ({error}); using cached firmware {cached.version}: {cached.image}")
        return cached


def main():
    global MOUNT_POINT, ACTIVE_FIRMWARE
    ACTIVE_FIRMWARE = "kcan-x4"
    parser = argparse.ArgumentParser(description="Download and install stable KH CAN firmware")
    parser.add_argument("arguments", nargs="*", metavar="COMMAND_OR_FILE")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-s", "--skip-version", action="store_true", help="Skip final firmware version comparison")
    parser.add_argument("-b", "--skip-bootloader", action="store_true", help="Recovery: target is already an OTA disk; original model/version and downgrade policy cannot be verified")
    parser.add_argument("--force", action="store_true", help="Allow reinstalling the same online version; never downgrade")
    parser.add_argument("--version", help="Download/install this exact stable firmware release (X.Y.Z)")
    parser.add_argument("--firmware", choices=tuple(FIRMWARE_TYPES),
                        help="Target firmware series (default: kcan-x4); lsfw without --version lists all series by default")
    parser.add_argument("--allow-downgrade", action="store_true", help="Allow downgrade only with an explicit --version")
    parser.add_argument("--json", action="store_true", help="Machine-readable download/lsfw metadata")
    parser.add_argument("--expected-sha256", help="Require these exact bytes when installing an explicit --version")
    parser.add_argument("--cache-dir", type=Path, default=default_cache_dir())
    parser.add_argument("--info-url", help="Override HTTPS firmware metadata URL")
    parser.add_argument("--release-url", help="HTTPS release ZIP URL; overrides the URL in metadata")
    parser.epilog = "Run with sudo or as root. Examples: sudo kcan_fw_upgrade download; sudo kcan_fw_upgrade lsfw; sudo kcan_fw_upgrade kcan0 latest"
    args = parser.parse_intermixed_args()
    firmware_filter = args.firmware
    args.firmware = firmware_filter or "kcan-x4"
    try:
        if os.geteuid() != 0:
            raise PermissionError("This command requires root; run it with sudo")
        words = args.arguments
        command = words[0].lower() if words else ""
        if args.version is not None:
            version_tuple(args.version)
            if args.skip_bootloader:
                raise ValueError("--version requires the normal online path, without --skip-bootloader")
        if args.allow_downgrade and (not args.version or command in ("download", "fetch", "lsfw", "ls-fw", "resolvefw", "resolve-fw", "resolve")):
            raise ValueError("--allow-downgrade requires installation with an explicit --version")
        if args.json and command not in ("download", "fetch", "lsfw", "ls-fw"):
            raise ValueError("--json is only supported for download and lsfw")
        if args.expected_sha256 and (not args.version or not re.fullmatch(r"[0-9a-fA-F]{64}", args.expected_sha256) or command in ("download", "fetch", "lsfw", "ls-fw", "resolvefw", "resolve-fw", "resolve")):
            raise ValueError("--expected-sha256 requires installation with an explicit --version and a SHA-256 digest")
        if command in ("download", "fetch"):
            if len(words) != 1:
                parser.error("download takes no positional arguments")
            release = download_release(args.cache_dir, args.info_url, args.release_url, version=args.version, firmware=args.firmware)
            if args.json:
                print(json.dumps({"version": release.version, "image": str(release.image.resolve()), "sha256": release.sha256, "fw_type": release.fw_type}))
            else:
                print(f"Downloaded {release.fw_type} firmware {release.version} (SHA-256 {release.sha256})")
                print(release.image)
            return 0
        if command in ("lsfw", "ls-fw"):
            if args.version:
                single = cached_release(args.cache_dir, version=args.version, firmware=args.firmware)
                releases = [single] if single else []
            else:
                series = (firmware_filter,) if firmware_filter else FIRMWARE_TYPES
                releases = [item for firmware in series
                            for item in list_cached_releases(args.cache_dir, firmware=firmware)]
            if args.json:
                records = [{"version": item.version, "image": str(item.image.resolve()), "sha256": item.sha256, "fw_type": item.fw_type}
                           for item in releases]
                print(json.dumps((records[0] if records else None) if args.version else records))
                return 0
            print(f"Downloaded firmware (dir: {args.cache_dir})")
            if not args.version and not firmware_filter:
                print("Supported firmware series: " + ", ".join(FIRMWARE_TYPES))
            for item in releases:
                print(f"- {item.image.name}\n  fw_type: {item.fw_type}\n  fw_version: {item.version}\n  sha256: {item.sha256}\n  path: {item.image.resolve()}")
            if not releases:
                print("  (no downloaded firmware; run sudo kcan_fw_upgrade download)")
            return 0
        if command in ("resolvefw", "resolve-fw", "resolve"):
            if len(words) != 2:
                parser.error("resolvefw requires a filename or glob")
            release = cached_release(args.cache_dir, version=args.version, firmware=args.firmware)
            print(resolve_firmware_token(words[1], release.image.parent if release else None))
            return 0
        if args.skip_bootloader:
            if not 1 <= len(words) <= 2:
                parser.error("expected FIRMWARE [CAN_INTERFACE] with --skip-bootloader")
            token, interface = words[0], words[1] if len(words) == 2 else None
        else:
            if not 1 <= len(words) <= 2:
                parser.error("expected CAN_INTERFACE [latest|auto|FIRMWARE_FILE]")
            interface, token = words[0], words[1] if len(words) == 2 else "latest"
        if args.version and token.lower() not in ("auto", "latest"):
            raise ValueError("--version cannot be combined with a local firmware filename")
        if not interface and not args.skip_version:
            raise ValueError("Recovery without a CAN interface requires explicit --skip-version")
        # Fail while the normal device is still running, not after switching it
        # into OTA. udevadm is optional and deliberately not required here.
        check_upgrade_dependencies()
        if args.skip_bootloader:
            log_warning("Recovery mode: the original device model and firmware version cannot be confirmed; target compatibility and downgrade prevention are not guaranteed")
            ACTIVE_FIRMWARE = args.firmware
        expected_version = None
        target = None
        if token.lower() in ("auto", "latest"):
            # Validate downloaded or cached firmware before any bootloader or disk-write command.
            release = select_install_release(args)
            image, expected_version = release.image, version_tuple(release.version)
            if args.expected_sha256 and release.sha256.lower() != args.expected_sha256.lower():
                raise ValueError("Firmware SHA-256 differs from the pinned CI artifact")
            if interface and not args.skip_bootloader:
                target = validate_online_target(interface)
                ACTIVE_FIRMWARE = target["fw_type"]
                current, _ = query_current_versions(interface, args.verbose)
                verify_factory_identity(interface, args.verbose)
                if expected_version < current:
                    if not args.allow_downgrade:
                        raise ValueError("Refusing to downgrade online firmware; select --version and --allow-downgrade explicitly")
                    log_warning("Explicit firmware downgrade: " + ".".join(map(str, current)) + " -> " + release.version)
                if expected_version == current and ACTIVE_FIRMWARE == args.firmware and not args.force:
                    log_success(f"Already up-to-date: {release.version}; use --force to reinstall")
                    return 0
        else:
            image = resolve_firmware_token(token)
            if interface and not args.skip_bootloader:
                target = validate_online_target(interface)
                ACTIVE_FIRMWARE = target["fw_type"]
                verify_factory_identity(interface, args.verbose)
        if not args.skip_bootloader:
            if find_upgrade_device(args.verbose):
                raise RuntimeError("An OTA disk is already connected; disconnect it before starting another upgrade")
            if not enter_bootloader_mode(interface, args.verbose):
                raise RuntimeError("Failed to enter bootloader mode")
        device = wait_for_usb_device(args.verbose)
        if target:
            verify_ota_target(device, target)
        MOUNT_POINT = Path(tempfile.mkdtemp(prefix="kcan-upgrade-"))
        try:
            if not mount_upgrade_device(device, args.verbose):
                raise RuntimeError("Failed to mount the OTA disk")
            try:
                if not copy_firmware(image, args.verbose):
                    raise RuntimeError("Failed to write firmware")
            finally:
                if not unmount_upgrade_device(args.verbose):
                    raise RuntimeError(f"OTA disk is still mounted at {MOUNT_POINT}; unmount it manually")
        finally:
            # Never recursively clean a directory that may still be a mounted OTA volume.
            try:
                MOUNT_POINT.rmdir()
            except OSError:
                pass
        if interface:
            interface = wait_for_target_restart(
                target or {}, args.firmware if expected_version is not None else None, args.verbose)
            if not args.skip_version:
                actual, _ = query_current_versions(interface, args.verbose)
                if expected_version is not None and actual != expected_version:
                    raise RuntimeError(f"Firmware verification failed: expected {expected_version}, got {actual}")
                label = "Firmware version verified: " if expected_version is not None else "Firmware version read back: "
                log_success(label + ".".join(map(str, actual)))
        if args.skip_version:
            if args.skip_bootloader and not interface:
                log_warning("Recovery image copied; device startup and firmware version were not verified")
            elif args.skip_bootloader:
                log_warning("Recovery image copied; device restart observed, final firmware version comparison was explicitly skipped")
            else:
                log_warning("Firmware copied; final version verification was explicitly skipped")
        else:
            log_success("Firmware upgrade completed successfully")
        return 0
    except KeyboardInterrupt:
        log_error("Upgrade interrupted")
        return 1
    except Exception as error:
        log_error(str(error))
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
