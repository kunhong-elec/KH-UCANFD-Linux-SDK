# Development validation / 开发验证

[English README](README.md) · [简体中文](README_zh.md)

## x86_64

| Architecture / CPU 架构 | Hardware / 硬件平台 | Kernel / 内核 | Distribution / 发行版 |
| --- | --- | --- | --- |
| x86_64 | Intel Xeon E5-2690 v4 test host | `5.15.0-198-generic`、`5.15.220-rt102` | Ubuntu 22.04.5 LTS |
| x86_64 | Intel Xeon E5-2690 v4 test host | `6.8.0-147-generic` | Ubuntu 24.04.5 LTS |
| x86_64 | Intel Xeon E5-2690 v4 test host | `7.0.0-38-generic` | Ubuntu 26.04.1 LTS |
| x86_64 | Intel Xeon E5-2690 v4 test host | `5.15.220-rt102`、`5.15.225-kcan-lts`、`6.1.192-kcan-lts`、`6.6.162-kcan-lts`、`6.12.116-kcan-lts`、`7.3.0-9-generic`、`7.3.0-10-generic`、`7.3.1-070301-generic` | Ubuntu 26.10 |
| x86_64 | Intel Xeon E5-2690 v4 test host | `6.1.71-1-lts`、`6.18.42-1-lts`、`7.1.5-zen1-2-zen` | Arch Linux |
| x86_64 | Intel Xeon E5-2690 v4 test host | `6.6.72-1-lts`、`6.12.75-1-lts` (software CI only / 仅软件 CI) | Arch Linux |
| x86_64 | Intel Xeon E5-2690 v4 test host | `6.8.0-060800-generic`、`6.12.0-061200-generic` (build only / 仅编译验证) | Ubuntu 26.10 (build environment / 构建环境) |
| x86_64 | HP ProBook 455 G7 | `6.8.0-138-generic` | Ubuntu 22.04.5 LTS |
| x86_64 | Dell OptiPlex 7050 | `6.8.0-138-generic` | Ubuntu 22.04.3 LTS |

## NVIDIA Jetson

| Architecture / CPU 架构 | Hardware / 硬件平台 | Kernel / 内核 | Distribution / 发行版 |
| --- | --- | --- | --- |
| ARM64（aarch64） | NVIDIA Jetson Orin Nano | `6.8.12-1021-tegra` | Ubuntu 24.04.4 LTS |

## Rockchip RK3588

| Architecture / CPU 架构 | Hardware / 硬件平台 | Kernel / 内核 | Distribution / 发行版 |
| --- | --- | --- | --- |
| ARM64（aarch64） | Orange Pi 5 Plus（Rockchip RK3588） | `5.10.160-rockchip-rk3588` | Orange Pi 1.2.0 Jammy（Ubuntu 22.04） |
| ARM64（aarch64） | Orange Pi 5 Plus（Rockchip RK3588） | `6.1.99-rockchip-rk3588` (driver installation, functionality and latency / 驱动安装、功能和延迟专项) | Orange Pi 1.2.2 Jammy（Ubuntu 22.04） |
