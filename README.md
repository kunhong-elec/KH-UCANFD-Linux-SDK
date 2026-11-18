# KH-UCANFD Linux SDK

[![SDK 下载安装 CI](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/workflows/release-install.yml/badge.svg?branch=master)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/workflows/release-install.yml)
[![Gitee 同步状态](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/workflows/gitee-sync.yml/badge.svg?branch=master)](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/workflows/gitee-sync.yml)

## Release 下载安装 CI

<!-- sdk-install-results:start -->

| 发行版 | 实测内核 | SDK 版本 | 下载安装结果 |
| --- | --- | --- | --- |
| Ubuntu 22.04 | `6.8.0-1070-azure` | `1.5.1` | [✅ 通过](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/44325006039/job/134873833426) |
| Ubuntu 24.04 | `7.0.0-1014-aws` | `1.5.1` | [✅ 通过](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/44325006039/job/134873832517) |
| Ubuntu 26.04 | `7.0.0-1019-azure` | `1.5.1` | [✅ 通过](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/actions/runs/44325006039/job/134873833352) |

<!-- sdk-install-results:end -->

## SDK 介绍

KH-UCANFD Linux SDK 为鲲弘 USB-CAN/CAN FD 接口设备提供 Linux 驱动和配套工具。`kcan` 驱动将设备通道接入 Linux SocketCAN，可用 `can-utils` 调试，也可通过 SocketCAN C 接口或 `python-can` 开发应用。

本仓库提供 SDK 介绍与教程索引，源码 ZIP 随 [GitHub Releases](https://github.com/kunhong-elec/KH-UCANFD-Linux-SDK/releases) 分发。设备和固件适配信息见[支持的硬件与固件](https://docs.kunhong-elec.com/zh/tutorials/technical/linuxsdk/introduction/README.html)。

## 功能特性简介

- **SocketCAN 通信**。配置 CAN 和 CAN FD 通道，完成报文收发和接口状态查询。
- **通道绑定与监测**。固定多设备环境下的接口名称，用 `lskcan` 枚举接口，用 `kcan_monitor` 查看通道状态和帧率。
- **通信测试与固件管理**。用 `kcanfd_test` 执行通道压力测试，用固件工具查询版本并升级受支持的设备。
- **多平台安装**。提供本机编译、DKMS 安装和交叉编译流程。

## 已验证的平台

| CPU 架构 | 硬件平台 | 内核版本 | 发行版 |
| --- | --- | --- | --- |
| x86_64 | Intel Xeon E5-2690 v4 测试主机 | `5.15.0-198-generic`、`5.15.220-rt102` | Ubuntu 22.04.5 LTS |
| x86_64 | Intel Xeon E5-2690 v4 测试主机 | `6.8.0-147-generic` | Ubuntu 24.04.5 LTS |
| x86_64 | Intel Xeon E5-2690 v4 测试主机 | `7.0.0-38-generic` | Ubuntu 26.04.1 LTS |
| x86_64 | Intel Xeon E5-2690 v4 测试主机 | `5.15.220-rt102`、`5.15.225-kcan-lts`、`6.1.192-kcan-lts`、`6.6.162-kcan-lts`、`6.12.116-kcan-lts`、`7.3.0-9-generic`、`7.3.0-10-generic`、`7.3.1-070301-generic` | Ubuntu 26.10 |
| x86_64 | Intel Xeon E5-2690 v4 测试主机 | `6.1.71-1-lts`、`6.18.42-1-lts`、`7.1.5-zen1-2-zen` | Arch Linux |
| x86_64 | Intel Xeon E5-2690 v4 测试主机 | `6.6.72-1-lts`、`6.12.75-1-lts`（仅软件 CI） | Arch Linux |
| x86_64 | Intel Xeon E5-2690 v4 测试主机 | `6.8.0-060800-generic`、`6.12.0-061200-generic`（仅编译验证） | Ubuntu 26.10（构建环境） |
| x86_64 | HP ProBook 455 G7 | `6.8.0-138-generic` | Ubuntu 22.04.5 LTS |
| x86_64 | Dell OptiPlex 7050 | `6.8.0-138-generic` | Ubuntu 22.04.3 LTS |
| ARM64（aarch64） | NVIDIA Jetson Orin Nano | `6.8.12-1021-tegra` | Ubuntu 24.04.4 LTS |
| ARM64（aarch64） | Orange Pi 5 Plus（Rockchip RK3588） | `5.10.160-rockchip-rk3588` | Orange Pi 1.2.0 Jammy（Ubuntu 22.04） |
| ARM64（aarch64） | Orange Pi 5 Plus（Rockchip RK3588） | `6.1.99-rockchip-rk3588`（驱动安装、功能和延迟专项） | Orange Pi 1.2.2 Jammy（Ubuntu 22.04） |

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
