# KH CAN 固件升级工具

SDK 只分发升级工具，不再携带固件、测试固件或固件版本清单，安装 SDK 不访问网络。
默认从与 CANmeleon Device Manager 相同的发布源获取最新稳定版。支持 KCAN、PCANFD 系列、
Kvaser FD 和 GS USB，省略 `--firmware` 时继续选择 KCAN。固件自行适配设备模式和通道数。
Python 入口与历史 Bash 入口共用同一实现，依赖 Python 3.8+ 标准库，无需 curl 或 unzip。

## 构建与安装

```bash
make
sudo make install
# 安装到其他前缀或打包目录
make DESTDIR=/tmp/kcan-package PREFIX=/usr/local install
```

安装 `kcan_fw_tool`、`kcan_fw_upgrade`、`kcan_fw_upgrade_bash` 和
`kcan_firmware_release.py` 到 PREFIX/bin。最后一个是运行时模块，不能遗漏。
开发源码的 Python 入口为 `kcan_fw_upgrade.py`，Shell 入口为 `kcan_fw_upgrade.sh`。
`sudo make uninstall` 删除工具，保留在线缓存及用户固件，不扫描或删除 `/usr/lib/firmware`。

## 下载最新稳定固件

与 CDM 共用固定发布链接：

- [最新版本信息](https://gitee.com/sysmax/kpcfg4-canmeleon/releases/download/latest/KH-UCANFD-G2-latest.json)
- [最新固件发布包](https://gitee.com/sysmax/kpcfg4-canmeleon/releases/download/latest/KH-UCANFD-G2.zip)

```bash
# 只下载并验证，无需设备，不发送升级命令
sudo kcan_fw_upgrade download
# 选择目标系列；四系列均支持 --version X.Y.Z
sudo kcan_fw_upgrade download --firmware pcanfd
sudo kcan_fw_upgrade download --firmware kvaser-fd
sudo kcan_fw_upgrade download --firmware gs-usb
# 下载一个确实存在、且使用受支持发布格式的稳定版（不存在或不匹配即失败）
sudo kcan_fw_upgrade download --version 8.14.8
sudo kcan_fw_upgrade download --version 8.14.8 --json
# 查看指定系列的版本缓存；省略 --firmware 时按 KCAN 查询
sudo kcan_fw_upgrade lsfw --version 8.14.8 --firmware pcanfd
# 显示支持切换的系列及所有已校验的缓存版本；空缓存也会显示系列
sudo kcan_fw_upgrade lsfw
# 只列出指定系列的缓存版本
sudo kcan_fw_upgrade lsfw --firmware gs-usb
# JSON 仅包含缓存记录；带 --version 时返回单个对象或 null
sudo kcan_fw_upgrade lsfw --json
# 明确指定镜像源及缓存目录
sudo kcan_fw_upgrade download --info-url https://mirror.example/latest.json \
    --release-url https://mirror.example/firmware.zip --cache-dir /path/to/cache
```

下载、查询、解析路径和升级均需 root 权限，请通过 `sudo` 执行。默认共用系统缓存
`/var/cache/kcan/firmware`，也可用 `--cache-dir` 指定其他目录。
缓存按版本和内容 SHA-256 存放，只保留选中的
目标系列镜像、各版本索引与独立的 latest 索引，不展开其他类型固件，也不保留下载 ZIP。
KCAN 保留原有缓存布局；其他系列分别存入根缓存下的 `pcanfd/`、`kvaser-fd/`、`gs-usb/`。
`download`、`lsfw`、`resolvefw`、指定 `--version` 和在线恢复均接受 `--firmware`。
`lsfw` 默认查询四个系列的缓存，可用 `--firmware` 筛选。JSON 中的 `fw_type` 标识记录所属系列。

先下载 latest JSON，再下载 ZIP，核对清单中的产品、稳定通道、版本、唯一目标系列
条目、文件大小和 SHA-256，并检查 KPCFG 分块、固件正文 SHA-256、KHAP 固件
类型和版本（PCANFD=1、Kvaser FD=4、KCAN=11、GS USB=12）。仅全部通过后才发布缓存索引、允许进入 bootloader。
ZIP 支持 Windows/POSIX 路径分隔符；拒绝越界路径、重复条目、链接及超限资源。
发布过程中 JSON 与 ZIP 版本不一致时会失败，请稍后重试。
`download` 在网络或校验失败时返回非零。升级遇到 DNS 或连接失败时，会提示并使用当前缓存中
所选系列内校验通过的最高版本，绝不回退到其他系列。指定 `--version` 时只查找该版本。HTTP 错误、TLS 校验失败和固件校验
失败会直接退出。离线回退仍执行设备识别、版本比较和降级限制。

## 安装最新固件

先停止 CAN 业务，只连接目标 USB CAN 适配器，并断开其他 OTA 设备。
实际接口名可能是 `can0` 或启用 SDK udev 规则后的 `kcan0`。

```bash
sudo kcan_fw_upgrade kcan0 latest
sudo kcan_fw_upgrade kcan0 auto   # 默认也从在线发布源选择
sudo kcan_fw_upgrade kcan0        # 省略固件参数等价于 latest
# 同版本默认不写入；明确需要重装时
sudo kcan_fw_upgrade kcan0 latest --force
# 可以从上述任一固件切换到另一个系列；使用当前实际接口名
sudo kcan_fw_upgrade can0 latest --firmware pcanfd
sudo kcan_fw_upgrade can0 latest --firmware kvaser-fd
sudo kcan_fw_upgrade can0 latest --firmware gs-usb
sudo kcan_fw_upgrade can0 latest --firmware kcan-x4
```

设备正常运行、可读取 CAN 接口与当前版本时，在线升级识别源协议，并通过 KH 工厂响应检查设备身份与 boot 完整性；不能只凭公共 VID/PID 判断为 KH 设备。下载及校验完成后才发送
bootloader 命令。正常在线升级默认不降级，`--force` 仅允许同版本重装，不能用于在线降级。
只有同系列、同版本才默认跳过；同版本跨系列仍实际写入，无需 `--force`。
指定版本使用发布仓库 `releases/download/X.Y.Z/` 下的元数据和 ZIP，不存在时直接失败，
不会回退 latest。请求版本、元数据版本、发布清单版本和镜像内部版本必须一致。

```bash
sudo kcan_fw_upgrade kcan0 --version 8.14.8
# 显式选择旧版本，并且明确允许降级；同样检查目标型号和最终版本
sudo kcan_fw_upgrade kcan0 --version 8.14.8 --allow-downgrade
# 同版本也必须实际写入时加 --force
sudo kcan_fw_upgrade kcan0 --version 8.14.8 --allow-downgrade --force
```

`--allow-downgrade` 只适用于显式 `--version`，不能与 latest/auto 的默认选择一起使用。
`--expected-sha256` 可额外固定指定版本镜像的 SHA-256；不匹配时在进入 bootloader 前失败。
指定版本入口不支持 `--skip-bootloader`，恢复与本地文件使用独立入口。

只识别 `395e/34cc:ffff` 的唯一 OTA 磁盘；找不到或发现多个时失败，
不会把任意新出现的 sdX 当作升级目标。设备授权与最终写入仍由 bootloader 检查。

复制后重新发现接口，检查目标系列、KH 工厂响应，并读取版本与在线目标版本精确比较。
接口名可以从 `kcan0` 变成 `can0`。多个适配器或多个 OTA 磁盘均拒绝继续。
重启超时、版本读取失败或版本不匹配均不会报告成功。
在虚拟机中需同时直通源固件、OTA 和目标固件，否则会明确超时。
VMware 可能为不同 USB 身份分配不同虚拟端口：在原运行设备消失、只有一个新增 OTA 磁盘、
没有其他运行适配器的独占流程中允许端口变化；最终仍验证唯一目标系列和版本。

## 本地文件及恢复

本地 `.kpcfg`／`.enc` 安装后重新发现唯一设备和接口，并按实际枚举系列选择工厂时序，
支持跨系列安装和接口改名。此路径没有发布元数据，成功时仅报告版本读回，
不声称与镜像内目标版本精确匹配。

```bash
sudo kcan_fw_upgrade kcan0 /path/to/firmware.kpcfg
# 兼容明确提供的旧 .enc；不再随 SDK 提供任何旧固件
sudo kcan_fw_upgrade kcan0 /path/to/firmware.enc
# 已经进入 OTA 的单一设备；没有 CAN 接口时显式跳过最终版本确认
sudo kcan_fw_upgrade latest --skip-bootloader --skip-version
# 已处于 OTA 时恢复为其他系列
sudo kcan_fw_upgrade latest --firmware gs-usb --skip-bootloader --skip-version
sudo kcan_fw_upgrade /path/to/firmware.kpcfg --skip-bootloader kcan0
# 已进入 OTA 且没有可用 CAN 接口的本地镜像恢复
sudo kcan_fw_upgrade /path/to/firmware.kpcfg --skip-bootloader --skip-version
```

异常设备已经进入 OTA 模式时，保留上述 `latest --skip-bootloader --skip-version`
在线恢复方式，无需先手工下载本地镜像，也不增加交互确认。
该模式无法读取原设备型号和版本，因此不提供目标型号匹配和防降级保证；
下载包自身的产品类型、稳定通道、版本、大小、SHA-256 和镜像格式校验仍然执行，
并且只接受唯一的 Kunhong OTA 磁盘。

`--skip-version` 表示不执行最后的版本确认。没有可用 CAN 接口时，恢复完成仅报告
“恢复镜像已复制，设备启动状态和固件版本未验证”，不把文件复制成功等同于设备恢复成功。
若提供了恢复后的 CAN 接口且没有 --skip-version，仍等待重启并读取版本；在线镜像还会
与目标版本精确比较。本地文件不推断目标版本，只报告读回值，不宣称已与镜像版本比较。
`lsfw` 只查询缓存，不再把 `/usr/lib/firmware` 中的旧随包文件当作最新版本来源。
可通过 `resolvefw <filename-or-glob>` 获取选定缓存中的唯一镜像绝对路径，
`--version` 可选定版本缓存；匹配多个文件时要求提供准确文件名。
本地刷写直接传已有文件的绝对路径或相对路径（也支持当前目录中的文件名），不访问网络，
不依赖版本清单，也不自动搜索旧随包目录。`auto` 始终等价于在线 `latest`。
`kcan_fw_tool <CAN_INTERFACE> version` 查询 KCAN 固件/bootloader 版本；其他三系列使用
`kcan_fw_tool --factory-timing modern <CAN_INTERFACE> version`。查询会进入工厂模式并启停 CAN，
应在空闲设备上执行。安装工具会自动选择源协议时序，普通安装无需指定该参数。

## 开发回归

```bash
python3 -m unittest discover -s test -p 'test_*firmware*.py' # 合成数据，不写设备
./release.sh --test                        # 在 fw_tool_dev 目录生成发布组件并验证
# 显式实机测试：在线升级并同版本重装，不切换其他固件类型
sudo bash test/test_firmware_upgrade.sh kcan0
```

测试数据由测试代码即时生成，不在仓库保留可下发固件。离线测试覆盖下载失败、
校验/版本/类型错误、危险 ZIP、缓存损坏、同版本跳过、拒绝降级，以及重启/版本验证失败。


## 精简 Linux 环境

udevadm 为可选依赖。缺失或 settle 失败/超时后，会提示并继续通过 sysfs 和设备节点
等待唯一的 Kunhong OTA 磁盘，总等待时间保持有界。mount、umount、mountpoint、sync
是安装所需工具，缺少时会在进入 bootloader 前报错；只下载或查询缓存不要求这些工具。
