# KH-UCANFD Linux SDK

[English](README.md)

[![Gitee 同步状态](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/workflows/gitee-sync.yml/badge.svg?branch=master)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/workflows/gitee-sync.yml)

## Release 下载安装 CI

<!-- sdk-install-results:start -->
<!-- sdk-install-run: 9.1 -->

SDK `1.5.2`

[![Ubuntu 22.04.5 LTS · x86_64 · 6.8.0-1070-azure | 失败](https://img.shields.io/badge/%E5%A4%B1%E8%B4%A5-cf222e?label=Ubuntu+22.04.5+LTS+%C2%B7+x86_64+%C2%B7+6.8.0-1070-azure&logo=github&labelColor=30363d)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/45571721712/job/139059740395)
[![Ubuntu 24.04.5 LTS · x86_64 · 7.0.0-1014-aws | 失败](https://img.shields.io/badge/%E5%A4%B1%E8%B4%A5-cf222e?label=Ubuntu+24.04.5+LTS+%C2%B7+x86_64+%C2%B7+7.0.0-1014-aws&logo=github&labelColor=30363d)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/45571721712/job/139059740403)
[![Ubuntu 24.04.5 LTS · aarch64 · 7.0.0-1017-azure | 失败](https://img.shields.io/badge/%E5%A4%B1%E8%B4%A5-cf222e?label=Ubuntu+24.04.5+LTS+%C2%B7+aarch64+%C2%B7+7.0.0-1017-azure&logo=github&labelColor=30363d)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/45571721712/job/139059740175)
[![Ubuntu 26.04.1 LTS · x86_64 · 7.0.0-1020-azure | 失败](https://img.shields.io/badge/%E5%A4%B1%E8%B4%A5-cf222e?label=Ubuntu+26.04.1+LTS+%C2%B7+x86_64+%C2%B7+7.0.0-1020-azure&logo=github&labelColor=30363d)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/45571721712/job/139059740376)
[![Ubuntu 26.04.1 LTS · aarch64 · 7.0.0-1020-azure | 失败](https://img.shields.io/badge/%E5%A4%B1%E8%B4%A5-cf222e?label=Ubuntu+26.04.1+LTS+%C2%B7+aarch64+%C2%B7+7.0.0-1020-azure&logo=github&labelColor=30363d)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/45571721712/job/139059739923)

<!-- sdk-install-results:end -->

## SDK 介绍

KH-UCANFD Linux SDK 为鲲弘 USB-CAN/CAN FD 接口设备提供 Linux 驱动和配套工具。`kcan` 驱动将设备通道接入 Linux SocketCAN，可用 `can-utils` 调试，也可通过 SocketCAN C 接口或 `python-can` 开发应用。

本仓库提供 SDK 介绍与教程索引，源码 ZIP 随 [GitHub Releases](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/releases) 分发。设备和固件适配信息见[支持的硬件与固件](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/introduction/README.html)。

## 功能特性简介

- **SocketCAN 通信**。配置 CAN 和 CAN FD 通道，完成报文收发和接口状态查询。
- **通道绑定与监测**。固定多设备环境下的接口名称，用 `lskcan` 枚举接口，用 `kcan_monitor` 查看通道状态和帧率。
- **通信测试与固件管理**。用 `kcanfd_test` 执行通道压力测试，用固件工具查询版本并升级受支持的设备。
- **多平台安装**。提供本机编译、DKMS 安装和交叉编译流程。

## 开发验证

[x86_64](#x86_64) · [NVIDIA Jetson](#nvidia-jetson) · [Rockchip RK3588](#rockchip-rk3588) · [硬件与测试范围](VALIDATION.md)

### x86_64

Intel Xeon E5-2690 v4 测试主机、HP ProBook 455 G7、Dell OptiPlex 7050

[![Ubuntu 22.04.5 LTS · 5.15.0-198-generic | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+22.04.5+LTS+%C2%B7+5.15.0-198-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 22.04.5 LTS · 5.15.220-rt102 | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+22.04.5+LTS+%C2%B7+5.15.220-rt102&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 24.04.5 LTS · 6.8.0-147-generic | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+24.04.5+LTS+%C2%B7+6.8.0-147-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.04.1 LTS · 7.0.0-38-generic | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+26.04.1+LTS+%C2%B7+7.0.0-38-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 5.15.220-rt102 | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+26.10+%C2%B7+5.15.220-rt102&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 5.15.225-kcan-lts | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+26.10+%C2%B7+5.15.225-kcan-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 6.1.192-kcan-lts | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+26.10+%C2%B7+6.1.192-kcan-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 6.6.162-kcan-lts | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+26.10+%C2%B7+6.6.162-kcan-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 6.12.116-kcan-lts | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+26.10+%C2%B7+6.12.116-kcan-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 7.3.0-9-generic | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+26.10+%C2%B7+7.3.0-9-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 7.3.0-10-generic | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+26.10+%C2%B7+7.3.0-10-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 7.3.1-070301-generic | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+26.10+%C2%B7+7.3.1-070301-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Arch Linux · 6.1.71-1-lts | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Arch+Linux+%C2%B7+6.1.71-1-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Arch Linux · 6.18.42-1-lts | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Arch+Linux+%C2%B7+6.18.42-1-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Arch Linux · 7.1.5-zen1-2-zen | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Arch+Linux+%C2%B7+7.1.5-zen1-2-zen&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Arch Linux · 6.6.72-1-lts | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Arch+Linux+%C2%B7+6.6.72-1-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Arch Linux · 6.12.75-1-lts | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Arch+Linux+%C2%B7+6.12.75-1-lts&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 6.8.0-060800-generic | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+26.10+%C2%B7+6.8.0-060800-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 26.10 · 6.12.0-061200-generic | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+26.10+%C2%B7+6.12.0-061200-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 22.04.5 LTS · 6.8.0-138-generic | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+22.04.5+LTS+%C2%B7+6.8.0-138-generic&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Ubuntu 22.04.3 LTS · 6.8.0-138-generic | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+22.04.3+LTS+%C2%B7+6.8.0-138-generic&logo=linux&labelColor=30363d)](VALIDATION.md)

### NVIDIA Jetson

Jetson Orin Nano

[![Ubuntu 24.04.4 LTS · 6.8.12-1021-tegra | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Ubuntu+24.04.4+LTS+%C2%B7+6.8.12-1021-tegra&logo=linux&labelColor=30363d)](VALIDATION.md)

### Rockchip RK3588

Orange Pi 5 Plus

[![Orange Pi 1.2.0 Jammy · 5.10.160-rockchip-rk3588 | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Orange+Pi+1.2.0+Jammy+%C2%B7+5.10.160-rockchip-rk3588&logo=linux&labelColor=30363d)](VALIDATION.md)
[![Orange Pi 1.2.2 Jammy · 6.1.99-rockchip-rk3588 | 已验证](https://img.shields.io/badge/%E5%B7%B2%E9%AA%8C%E8%AF%81-2da44e?label=Orange+Pi+1.2.2+Jammy+%C2%B7+6.1.99-rockchip-rk3588&logo=linux&labelColor=30363d)](VALIDATION.md)

## 下载安装建议

1. **下载发布包。** 从 [GitHub 最新发行版](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/releases/latest) 下载 `KH-UCANFD_Linux_SDK.zip` 和同名的 `.sha256` 文件。也可访问 [Gitee 发行版镜像](https://gitee.com/ChengDu-KunHong/KH-UCANFD_Linux_SDK/releases)。
2. **校验并解压。** 在下载目录执行 `sha256sum -c KH-UCANFD_Linux_SDK.zip.sha256`，校验通过后解压。
3. **准备依赖并安装。** 用 `uname -r` 确认当前内核，安装与它匹配的内核头文件和编译依赖。内核会随系统升级的主机可采用 DKMS。参考[驱动安装与设备识别](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/installation/README.html)和[内核升级与 DKMS](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/faq/03-kernel-upgrade.html)。
4. **验证接口并收发报文。** 接入设备后用 `lskcan` 检查通道，再按下方教程设置位速率并进行收发测试。

## 基础教程索引

| 使用场景 | 教程 |
| --- | --- |
| 配置 CAN/CAN FD 接口与首次收发 | [SocketCAN 接口配置](https://docs.kunhong-elec.com/zh/tutorials/can/SocketCAN/can-config.html) · [can-utils 报文收发](https://docs.kunhong-elec.com/zh/tutorials/can/SocketCAN/can-utils.html) |
| 管理多台设备与诊断通道 | [通道绑定](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/installation/channel-binding.html) · [SDK 实用工具](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/tools/README.html) |
| 嵌入式平台安装或交叉编译 | [RK3588 安装示例](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/installation/rk3588-5.10.160.html) · [交叉编译](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/installation/cross-compile.html) |
| 编写应用程序 | [SocketCAN C 编程](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/development/socketcan/socketcan-programming.html) · [python-can](https://docs.kunhong-elec.com/zh/tutorials/can/PythonCan.html) |
| 查看和升级固件 | [KCAN 固件工具](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/tools/fwtools.html) |

## 相关链接

- [KH-UCANFD 系列产品快速上手](https://docs.kunhong-elec.com/zh/tutorials/can/ucanfd/ucanfd.html)
- [SocketCAN 命令生成器](https://docs.kunhong-elec.com/zh/online-tools/socketcan-command-generator/)
- [SDK 常见问题排查](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/faq/README.html) · [Secure Boot 与驱动加载](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/faq/01-secure-boot-conflict.html)
- [鲲弘电子文档中心](https://docs.kunhong-elec.com/zh/)
