"""Download and validate the stable KCAN firmware published for CANmeleon.

Only the selected single KCAN image is cached; archives are never extracted.
Uses the Python standard library and normal HTTPS certificate verification.
"""
import errno
import hashlib
import http.client
import json
import logging
import os
from pathlib import Path, PurePosixPath
import re
import socket
import ssl
import stat
import struct
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass

RELEASE_ROOT = "https://gitee.com/sysmax/kpcfg4-canmeleon/releases/download/"
RELEASE_BASE = RELEASE_ROOT + "latest/"
DEFAULT_INFO_URL = RELEASE_BASE + "KH-UCANFD-G2-latest.json"
DEFAULT_RELEASE_URL = RELEASE_BASE + "KH-UCANFD-G2.zip"
MAX_JSON = 2 * 1024 * 1024
MAX_ARCHIVE = 64 * 1024 * 1024
MAX_IMAGE = 16 * 1024 * 1024
FIRMWARE_TYPES = {"kcan-x4": 11, "pcanfd": 1, "kvaser-fd": 4, "gs-usb": 12}


def firmware_cache(cache_dir, firmware):
    if firmware not in FIRMWARE_TYPES:
        raise ValueError("Unsupported firmware series: " + firmware)
    root = Path(cache_dir) if cache_dir else default_cache_dir()
    # Keep the historical KCAN cache and indexes readable without migration.
    return root if firmware == "kcan-x4" else root / firmware


def version_tuple(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError("Invalid firmware version: %r" % value)
    result = tuple(map(int, value.split(".")))
    if any(part > 255 for part in result):
        raise ValueError("Firmware version component exceeds 255")
    return result


def default_cache_dir():
    return Path("/var/cache/kcan/firmware")


def _https_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Firmware downloads require an HTTPS URL without credentials")
    return url


class _HTTPSRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _https_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class ReleaseConnectionError(OSError):
    """The firmware host could not be reached or the connection was interrupted."""


def _network_call(operation, *args, **kwargs):
    try:
        return operation(*args, **kwargs)
    except (OSError, http.client.IncompleteRead) as error:
        reason = error.reason if isinstance(error, urllib.error.URLError) else error
        if isinstance(error, urllib.error.HTTPError) or isinstance(reason, ssl.SSLError):
            raise
        if isinstance(reason, (ConnectionError, TimeoutError, socket.gaierror, socket.herror,
                               http.client.IncompleteRead)) or getattr(reason, "errno", None) in (
                                   errno.ENETDOWN, errno.ENETUNREACH, errno.ENETRESET,
                                   errno.EHOSTDOWN, errno.EHOSTUNREACH, errno.ETIMEDOUT,
                                   errno.ECONNABORTED, errno.ECONNREFUSED, errno.ECONNRESET,
                                   errno.EPIPE):
            raise ReleaseConnectionError(str(error)) from error
        raise


def _download(url, destination, limit):
    request = urllib.request.Request(_https_url(url), headers={"User-Agent": "KCAN-Linux-SDK/1"})
    opener = urllib.request.build_opener(_HTTPSRedirect())
    with _network_call(opener.open, request, timeout=60) as response, destination.open("wb") as output:
        _https_url(response.geturl())
        count = 0
        while True:
            chunk = _network_call(response.read, 65536)
            if not chunk:
                break
            count += len(chunk)
            if count > limit:
                raise ValueError("Firmware download exceeds size limit")
            output.write(chunk)
        if count == 0:
            raise ValueError("Empty firmware download")


def _json(data):
    value = json.loads(data.decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("Firmware metadata must be a JSON object")
    return value


def _member_name(name):
    # The official release ZIP uses Windows separators, even on Linux.
    name = name.replace("\\", "/")
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or ".." in path.parts or any(":" in p for p in path.parts):
        raise ValueError("Unsafe firmware archive path: " + name)
    return str(path)


def validate_kcan_image(data, version, source_addr=None, firmware="kcan-x4"):
    """Check transport blocks and the single normal KCAN (KHAP type 11) image."""
    if not data or len(data) % 512:
        raise ValueError("Invalid KPCFG block length")
    payload = bytearray()
    identity = None
    for index, offset in enumerate(range(0, len(data), 512)):
        block = data[offset:offset + 512]
        if struct.unpack_from("<II", block) != (0x43444B48, 0x4B484B44):
            raise ValueError("Invalid KPCFG block magic")
        if struct.unpack_from("<I", block, 508)[0] != 0x4B454E44:
            raise ValueError("Invalid KPCFG block trailer")
        stamp, total, seq, length = struct.unpack_from("<IIII", block, 12)
        current = (block[8], block[9], stamp, total)
        if identity is None:
            identity = current
        if current != identity or seq != index or not 0 < length <= 480:
            raise ValueError("Inconsistent KPCFG blocks")
        payload.extend(block[28:28 + length])
    kind, address, _, total = identity
    transport_addr = address << 12
    if source_addr is not None and transport_addr != source_addr:
        raise ValueError("KPCFG address differs from release metadata")
    if kind & 0x0F or len(payload) != total:
        raise ValueError("KPCFG must contain one normal firmware at the declared address")
    if len(payload) < 4096 or struct.unpack_from("<I", payload)[0] != 0xCD4B4848:
        raise ValueError("Invalid firmware header")
    image_len = struct.unpack_from("<I", payload, 12)[0]
    address_in_header = struct.unpack_from("<I", payload, 92)[0]
    if image_len + 4096 != len(payload) or address_in_header != transport_addr or payload[20] & 0x0F:
        raise ValueError("Invalid single-firmware length, address or type")
    if transport_addr < 0x40000 or transport_addr + len(payload) > 0x100000:
        raise ValueError("Firmware exceeds the firmware flash region")
    if payload[23] != 4 or hashlib.sha256(payload[4096:]).digest() != payload[28:60]:
        raise ValueError("Firmware body SHA-256 mismatch or unsupported hash type")
    magic, ext_version, size, fw_type = struct.unpack_from("<IHHH", payload, 0x100)
    if (magic, ext_version, fw_type) != (0x5041484B, 1, FIRMWARE_TYPES[firmware]) or size < 40 or size > 4096 - 0x100:
        raise ValueError("Firmware is not a supported standalone " + ("KCAN" if firmware == "kcan-x4" else firmware) + " image")
    packed = struct.unpack_from("<I", payload, 0x118)[0]
    actual = tuple((packed >> shift) & 255 for shift in (0, 8, 16))
    if actual != version_tuple(version):
        raise ValueError("Firmware header version differs from release metadata")


@dataclass(frozen=True)
class Release:
    version: str
    image: Path
    sha256: str
    fw_type: str = "kcan-x4"


def select_archive(archive, expected_version, firmware="kcan-x4"):
    """Return the validated manifest, app entry and bytes. Do not write anything."""
    with zipfile.ZipFile(archive) as bundle:
        members = {}
        size = 0
        for entry in bundle.infolist():
            name = _member_name(entry.filename)
            if name.casefold() in {key.casefold() for key in members}:
                raise ValueError("Duplicate firmware ZIP member: " + name)
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError("Firmware ZIP contains a symbolic link")
            if entry.is_dir() or entry.filename.endswith("\\"):
                continue
            size += entry.file_size
            if len(members) >= 256 or entry.file_size > MAX_IMAGE or size > MAX_ARCHIVE:
                raise ValueError("Firmware ZIP exceeds size/count limits")
            members[name] = entry
        manifests = [name for name in members if PurePosixPath(name).name == "firmware-release.json"]
        if len(manifests) != 1 or members[manifests[0]].file_size > MAX_JSON:
            raise ValueError("Expected exactly one firmware-release.json")
        manifest_name = manifests[0]
        manifest = _json(bundle.read(members[manifest_name]))
        if manifest.get("schema_version") not in (2, 3) or manifest.get("product", {}).get("id") != "kh-ucanfd-g2":
            raise ValueError("Unsupported firmware release schema/product")
        release = manifest["release"]
        if release.get("version") != expected_version or release.get("channel", "stable") != "stable":
            raise ValueError("Release version/channel differs from latest stable metadata; retry later")
        apps = [app for app in manifest.get("apps", [])
                if app.get("fw_type") == firmware and app.get("mode", "default") == "default"]
        if len(apps) != 1:
            raise ValueError("Expected exactly one standalone " + ("KCAN" if firmware == "kcan-x4" else firmware) + " firmware")
        app = apps[0]
        filename = _member_name(app["file"])
        if PurePosixPath(filename).suffix.lower() != ".kpcfg":
            raise ValueError("Online KCAN firmware must be a KPCFG file")
        member = str(PurePosixPath(manifest_name).parent / filename)
        if member not in members:
            raise ValueError("KCAN firmware is missing from release archive")
        expected_hash = app.get("sha256", "")
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
            raise ValueError("Missing/invalid firmware SHA-256")
        expected_size = app.get("size_bytes")
        if type(expected_size) is not int or not 0 < expected_size <= MAX_IMAGE:
            raise ValueError("Missing/invalid firmware size")
        if members[member].file_size != expected_size:
            raise ValueError("Firmware size differs from release manifest")
        data = bundle.read(members[member])
        if hashlib.sha256(data).hexdigest() != expected_hash.lower():
            raise ValueError("Firmware SHA-256 differs from release manifest")
        validate_kcan_image(data, expected_version, int(release["source_addr"], 0), firmware)
        return manifest, app, data


def release_urls(version=None):
    """A pinned version uses only its immutable release tag, never latest."""
    if version is not None:
        version_tuple(version)
    base = RELEASE_ROOT + (version or "latest") + "/"
    return base + "KH-UCANFD-G2-latest.json", base + "KH-UCANFD-G2.zip"


def download_release(cache_dir=None, info_url=None, release_url=None, version=None, firmware="kcan-x4"):
    default_info, default_archive = release_urls(version)
    info_url = info_url or default_info
    cache = firmware_cache(cache_dir, firmware)
    cache.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Validate both resources before publishing any cache records.
    with tempfile.TemporaryDirectory(prefix=".download-", dir=cache) as temporary:
        temporary = Path(temporary)
        info_path = temporary / "info.json"
        _download(info_url, info_path, MAX_JSON)
        info = _json(info_path.read_bytes())
        if isinstance(info.get("channels"), dict):
            info = info["channels"].get("stable", info)
        published_version = info.get("version")
        version_tuple(published_version)
        if version is not None and published_version != version:
            raise ValueError("Requested firmware version differs from release metadata")
        if info.get("channel", "stable") != "stable":
            raise ValueError("Latest metadata is not from the stable channel")
        # A pinned request cannot be redirected by metadata to the moving latest
        # archive. Custom mirrors remain available through --release-url.
        url = release_url or (default_archive if version is not None else next(
            (info[key] for key in ("download_url", "firmware_url", "url") if info.get(key)), default_archive))
        archive = temporary / "release.zip"
        _download(url, archive, MAX_ARCHIVE)
        manifest, app, data = select_archive(archive, published_version, firmware)
        digest = hashlib.sha256(data).hexdigest()
        final_dir = cache / (published_version + "-" + digest)
        final_dir.mkdir(exist_ok=True, mode=0o700)
        image = final_dir / PurePosixPath(_member_name(app["file"])).name
        staged_image = temporary / "image.kpcfg"
        staged_image.write_bytes(data)
        os.replace(staged_image, image)
        record = {"version": published_version, "fw_type": firmware, "file": str(image.relative_to(cache)), "sha256": digest,
                  "size_bytes": len(data), "source_addr": manifest["release"]["source_addr"],
                  "info_url": info_url, "release_url": url}
        staged_record = temporary / "latest.json"
        staged_record.write_text(json.dumps(record, indent=2), encoding="utf-8")
        index_dir = cache / "versions"
        index_dir.mkdir(exist_ok=True, mode=0o700)
        os.replace(staged_record, index_dir / (published_version + ".json"))
        if version is None:
            staged_record.write_text(json.dumps(record, indent=2), encoding="utf-8")
            os.replace(staged_record, cache / "latest.json")
        return Release(published_version, image, digest, firmware)


def _read_cache_record(cache, version):
    if version is not None:
        version_tuple(version)
    record_path = cache / "versions" / (version + ".json") if version else cache / "latest.json"
    try:
        record = _json(record_path.read_bytes())
    except FileNotFoundError:
        return None
    version_tuple(record["version"])
    if version is not None and record["version"] != version:
        raise ValueError("Cached firmware version differs from requested version")
    return record


def _validate_cache_record(cache, record, firmware="kcan-x4"):
    if record.get("fw_type", "kcan-x4") != firmware:
        raise ValueError("Cached firmware series differs from requested series")
    image = cache / _member_name(record["file"])
    try:
        image.resolve().relative_to(cache.resolve())
    except ValueError:
        raise ValueError("Cached firmware points outside the cache")
    if not image.is_file() or image.stat().st_size > MAX_IMAGE:
        raise ValueError("Cached firmware is missing or exceeds the size limit")
    data = image.read_bytes()
    if len(data) != record["size_bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError("Cached firmware checksum mismatch")
    # Legacy indexes lack the manifest address. The validator still compares
    # the transport address against the firmware header and checks flash bounds.
    source_addr = int(record["source_addr"], 0) if "source_addr" in record else None
    validate_kcan_image(data, record["version"], source_addr, firmware)
    return Release(record["version"], image, record["sha256"], firmware)


def cached_release(cache_dir=None, version=None, firmware="kcan-x4"):
    cache = firmware_cache(cache_dir, firmware)
    record = _read_cache_record(cache, version)
    return _validate_cache_record(cache, record, firmware) if record is not None else None


def list_cached_releases(cache_dir=None, firmware="kcan-x4"):
    """Return verified releases newest first. Invalid records are reported via logging."""
    cache = firmware_cache(cache_dir, firmware)
    releases = {}
    latest_record = None
    versions = [None] + [path.stem for path in (cache / "versions").glob("*.json")]
    for version in versions:
        try:
            record = _read_cache_record(cache, version)
            if record is None or record == latest_record:
                continue
            item = _validate_cache_record(cache, record, firmware)
        except (OSError, ValueError, KeyError, TypeError) as error:
            logging.getLogger(__name__).warning(
                "Ignoring invalid firmware cache record %s: %s", version or "latest", error)
            continue
        if version is None:
            latest_record = record
        releases[item.version, item.sha256] = item
    return sorted(releases.values(), key=lambda item: version_tuple(item.version), reverse=True)
