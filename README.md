# KH-UCANFD Linux SDK

[简体中文](README_zh.md)

[![Gitee mirror sync](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/workflows/gitee-sync.yml/badge.svg?branch=master)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/workflows/gitee-sync.yml)

## Release installation CI

<!-- sdk-install-results:start -->
<!-- sdk-install-run: 9.1 -->

SDK `1.5.2`

[![Ubuntu 22.04.5 LTS · x86_64 · 6.8.0-1070-azure | failing](https://img.shields.io/badge/failing-cf222e?label=Ubuntu+22.04.5+LTS+%C2%B7+x86_64+%C2%B7+6.8.0-1070-azure&logo=github&labelColor=30363d)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/45571721712/job/139059740395)
[![Ubuntu 24.04.5 LTS · x86_64 · 7.0.0-1014-aws | failing](https://img.shields.io/badge/failing-cf222e?label=Ubuntu+24.04.5+LTS+%C2%B7+x86_64+%C2%B7+7.0.0-1014-aws&logo=github&labelColor=30363d)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/45571721712/job/139059740403)
[![Ubuntu 24.04.5 LTS · aarch64 · 7.0.0-1017-azure | failing](https://img.shields.io/badge/failing-cf222e?label=Ubuntu+24.04.5+LTS+%C2%B7+aarch64+%C2%B7+7.0.0-1017-azure&logo=github&labelColor=30363d)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/45571721712/job/139059740175)
[![Ubuntu 26.04.1 LTS · x86_64 · 7.0.0-1020-azure | failing](https://img.shields.io/badge/failing-cf222e?label=Ubuntu+26.04.1+LTS+%C2%B7+x86_64+%C2%B7+7.0.0-1020-azure&logo=github&labelColor=30363d)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/45571721712/job/139059740376)
[![Ubuntu 26.04.1 LTS · aarch64 · 7.0.0-1020-azure | failing](https://img.shields.io/badge/failing-cf222e?label=Ubuntu+26.04.1+LTS+%C2%B7+aarch64+%C2%B7+7.0.0-1020-azure&logo=github&labelColor=30363d)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/45571721712/job/139059739923)

<!-- sdk-install-results:end -->

## Overview

KH-UCANFD Linux SDK provides a Linux driver and tools for Kunhong USB-CAN/CAN FD interfaces. The `kcan` driver exposes device channels through SocketCAN for use with `can-utils`, the C socket API, and `python-can`.

The SDK source ZIP is available from [GitHub Releases](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/releases). See the [hardware and firmware guide](https://docs.kunhong-elec.com/en/tutorials/technical/linuxsdk/introduction/README.html) for supported devices.

## Features

- **CAN and CAN FD via SocketCAN**. Configure interfaces, send and receive frames, and inspect channel status.
- **Channel naming and monitoring**. Keep interface names stable across devices, list channels with `lskcan`, and monitor traffic with `kcan_monitor`.
- **Testing and firmware tools**. Run channel stress tests with `kcanfd_test`, query firmware versions, and update supported devices.
- **Installation options**. Build on the target, install with DKMS, or cross-compile.

## Development validation

[x86_64](#x86_64) · [NVIDIA Jetson](#nvidia-jetson) · [Rockchip RK3588](#rockchip-rk3588) · [Hardware and test scope](VALIDATION.md)

### x86_64

Intel Xeon E5-2690 v4 test host · HP ProBook 455 G7 · Dell OptiPlex 7050

[![Ubuntu 22.04.5 LTS · 5.15.0-198-generic | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+22.04.5+LTS+%C2%B7+5.15.0-198-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 22.04.5 LTS · 5.15.220-rt102 | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+22.04.5+LTS+%C2%B7+5.15.220-rt102&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 24.04.5 LTS · 6.8.0-147-generic | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+24.04.5+LTS+%C2%B7+6.8.0-147-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.04.1 LTS · 7.0.0-38-generic | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+26.04.1+LTS+%C2%B7+7.0.0-38-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 5.15.220-rt102 | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+26.10+%C2%B7+5.15.220-rt102&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 5.15.225-kcan-lts | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+26.10+%C2%B7+5.15.225-kcan-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 6.1.192-kcan-lts | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+26.10+%C2%B7+6.1.192-kcan-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 6.6.162-kcan-lts | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+26.10+%C2%B7+6.6.162-kcan-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 6.12.116-kcan-lts | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+26.10+%C2%B7+6.12.116-kcan-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 7.3.0-9-generic | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+26.10+%C2%B7+7.3.0-9-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 7.3.0-10-generic | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+26.10+%C2%B7+7.3.0-10-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 7.3.1-070301-generic | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+26.10+%C2%B7+7.3.1-070301-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Arch Linux · 6.1.71-1-lts | verified](https://img.shields.io/badge/verified-2da44e?label=Arch+Linux+%C2%B7+6.1.71-1-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Arch Linux · 6.18.42-1-lts | verified](https://img.shields.io/badge/verified-2da44e?label=Arch+Linux+%C2%B7+6.18.42-1-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Arch Linux · 7.1.5-zen1-2-zen | verified](https://img.shields.io/badge/verified-2da44e?label=Arch+Linux+%C2%B7+7.1.5-zen1-2-zen&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Arch Linux · 6.6.72-1-lts | verified](https://img.shields.io/badge/verified-2da44e?label=Arch+Linux+%C2%B7+6.6.72-1-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Arch Linux · 6.12.75-1-lts | verified](https://img.shields.io/badge/verified-2da44e?label=Arch+Linux+%C2%B7+6.12.75-1-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 6.8.0-060800-generic | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+26.10+%C2%B7+6.8.0-060800-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 6.12.0-061200-generic | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+26.10+%C2%B7+6.12.0-061200-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 22.04.5 LTS · 6.8.0-138-generic | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+22.04.5+LTS+%C2%B7+6.8.0-138-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 22.04.3 LTS · 6.8.0-138-generic | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+22.04.3+LTS+%C2%B7+6.8.0-138-generic&logo=linux&labelColor=30363d)](VALIDATION.md)

### NVIDIA Jetson

Jetson Orin Nano

[![Ubuntu 24.04.4 LTS · 6.8.12-1021-tegra | verified](https://img.shields.io/badge/verified-2da44e?label=Ubuntu+24.04.4+LTS+%C2%B7+6.8.12-1021-tegra&logo=linux&labelColor=30363d)](VALIDATION.md)

### Rockchip RK3588

Orange Pi 5 Plus

[![Orange Pi 1.2.0 Jammy · 5.10.160-rockchip-rk3588 | verified](https://img.shields.io/badge/verified-2da44e?label=Orange+Pi+1.2.0+Jammy+%C2%B7+5.10.160-rockchip-rk3588&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Orange Pi 1.2.2 Jammy · 6.1.99-rockchip-rk3588 | verified](https://img.shields.io/badge/verified-2da44e?label=Orange+Pi+1.2.2+Jammy+%C2%B7+6.1.99-rockchip-rk3588&logo=linux&labelColor=30363d)](VALIDATION.md)

## Download and install

1. Download `KH-UCANFD_Linux_SDK.zip` and its `.sha256` file from the [latest GitHub release](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/releases/latest) or the [Gitee mirror](https://gitee.com/ChengDu-KunHong/KH-UCANFD_Linux_SDK/releases).
2. Run `sha256sum -c KH-UCANFD_Linux_SDK.zip.sha256` in the download directory, then extract the ZIP.
3. Check your kernel with `uname -r` and install matching kernel headers and build dependencies. See [Driver installation](https://docs.kunhong-elec.com/en/tutorials/technical/linuxsdk/installation/README.html) and [Kernel upgrades and DKMS](https://docs.kunhong-elec.com/en/tutorials/technical/linuxsdk/faq/03-kernel-upgrade.html).
4. Connect the device, check its channels with `lskcan`, and follow the SocketCAN tutorials to configure bit rates and send or receive frames.

## Tutorials

| Task | Guide |
| --- | --- |
| Set up an interface and exchange frames | [SocketCAN configuration](https://docs.kunhong-elec.com/en/tutorials/can/SocketCAN/can-config.html) · [can-utils](https://docs.kunhong-elec.com/en/tutorials/can/SocketCAN/can-utils.html) |
| Manage and monitor multiple devices | [Stable channel naming](https://docs.kunhong-elec.com/en/tutorials/technical/linuxsdk/installation/channel-binding.html) · [SDK tools](https://docs.kunhong-elec.com/en/tutorials/technical/linuxsdk/tools/README.html) |
| Install on embedded Linux or cross-compile | [RK3588 installation](https://docs.kunhong-elec.com/en/tutorials/technical/linuxsdk/installation/rk3588-5.10.160.html) · [Cross-compilation](https://docs.kunhong-elec.com/en/tutorials/technical/linuxsdk/installation/cross-compile.html) |
| Write an application | [SocketCAN in C](https://docs.kunhong-elec.com/en/tutorials/technical/linuxsdk/development/socketcan/socketcan-programming.html) · [python-can](https://docs.kunhong-elec.com/en/tutorials/can/PythonCan.html) |
| Check or update firmware | [KCAN firmware tools](https://docs.kunhong-elec.com/en/tutorials/technical/linuxsdk/tools/fwtools.html) |

## Related links

- [KH-UCANFD quick start](https://docs.kunhong-elec.com/en/tutorials/can/ucanfd/ucanfd.html)
- [SocketCAN command generator](https://docs.kunhong-elec.com/en/online-tools/socketcan-command-generator/)
- [Troubleshooting](https://docs.kunhong-elec.com/en/tutorials/technical/linuxsdk/faq/README.html) · [Secure Boot and driver loading](https://docs.kunhong-elec.com/en/tutorials/technical/linuxsdk/faq/01-secure-boot-conflict.html)
- [Kunhong Documentation Center](https://docs.kunhong-elec.com/en/)
