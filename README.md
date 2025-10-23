# KH-UCANFD_Linux_SDK

#### SDK 介绍

KH-UCANFD_Linux_SDK是专为鲲弘CAN FD 系列硬件产品设计，提供深度优化的 Linux 驱动及配套工具，旨在解决 Linux 社区原生驱动性能瓶颈问题，充分释放 CAN FD 设备的吞吐能力并降低 CPU 开销。



##### 产品适配

SDK 支持鲲弘 CAN FD 系列硬件设备，已通过实测验证的典型型号包括：

- **KH-UCANFDX6-Mini**（6 通道 CAN FD 接口设备）
- 其他鲲弘 CAN FD 系列兼容设备（需参考硬件手册确认）



##### 核心优势

相较于 Linux 系统自带的通用 CAN 驱动，本 SDK 驱动在性能上有显著提升，关键测试数据（基于 KH-UCANFDX6-Mini + Ubuntu 22.04.3 LTS + 内核 6.8.0）如下：

| 指标                    | Linux社区驱动    | KH-UCANFD SDK  | 提升效果       |
| ----------------------- | ---------------- | -------------- | -------------- |
| CAN FD 帧率（1M/5M）    | 2800 帧 / 秒     | 20500 帧 / 秒  | 约**7 倍**提升 |
| CAN 总线负载率（1M/5M） | 14%              | 103%（满负载） | 达到极限负载   |
| CPU 开销                | 单核心占用超 50% | 无明显占用     | 降低约**85%**  |




#### 安装教程

##### 1. 安装前请确认以下系统环境要求：

1. Linux系统运行32位或64位内核
2. make、gcc编译工具
3. Linux系统的内核头文件包（或Linux头文件包），或交叉编译内核的源码树
4. g++编辑器及libstdc++库
5. libpopt-dev包



**2. 依赖安装命令**

```
# 1. 安装编译基础工具
sudo apt update && sudo apt install -y build-essential g++

# 2. 安装内核头文件（必须与当前内核版本匹配）
sudo apt install -y linux-headers-$(uname -r)

# 3. 安装libpopt依赖
sudo apt install -y libpopt-dev

# 4. 验证gcc版本（需与内核编译版本一致，查询方法如下）
cat /boot/config-$(uname -r) | grep -i "gcc_version"
# 示例输出：CONFIG_GCC_VERSION=120300（表示需安装gcc-12）
# 若版本不匹配，安装对应gcc：sudo apt install -y gcc-12
```



**3. SDK下载**

可在releases中手动下载，或使用wget下载。

```
# 安装wget（若未安装）
sudo apt install -y wget

# 下载SDK（最新版本）
wget https://gitee.com/ChengDu-KunHong/KH-UCANFD_Linux_SDK/releases/download/latest/KH-UCANFD_Linux_SDK.zip

# 解压SDK（替换x.y.z为实际版本号）
unzip KH-UCANFD_Linux_SDK.zip && cd KH-UCANFD_Linux_SDK_x.y.z/
```



**4. 编译与安装**

执行以下命令完成驱动编译和安装（需 sudo 权限）：

```
# 清理历史编译文件
sudo make clean

# 编译驱动（若报错，检查依赖是否齐全、gcc版本是否匹配）
sudo make

# 安装驱动（无报错则安装成功）
sudo make install
```



**5. 驱动加载验证**

加载驱动

```
# 加载pcan驱动模块
sudo modprobe pcan

# 验证驱动是否加载成功（输出含"pcan"即正常）
lsmod | grep pcan
# 示例输出：pcan                 233472  0  can_dev              53248  1 pcan
```


重新拔插 CAN FD 设备后，执行以下命令确认设备被识别：

```
# 查看CAN接口信息（输出含"can0"、"can1"等接口即正常）
ip -d link show

# 查看USB设备驱动绑定（输出含"Driver=pcan"即正常）
lsusb -t
```


#### 常见问题

##### Q1：驱动加载时报错 “modprobe: ERROR: could not insert 'pcan': Key was rejected by service”

**原因**：系统启用了 Secure Boot（安全启动），阻止了未签名的第三方驱动加载。

**解决方案**：进入主板 BIOS/UEFI 设置，关闭 Secure Boot 功能（具体步骤需根据主板型号查询，常见路径：BIOS → Security → Secure Boot → Disabled）。



##### Q2：运行`ucanfd_test.sh`测试脚本时丢包或测试失败

**原因 1**：CAN 接口通道未正确对接（脚本需通道两两交叉连接）。

**解决方案 1**：将设备的 can0 与 can1、can2 与 can3 等通道两两用 CAN 线连接（需接终端电阻，若硬件自带则无需额外添加）。

**原因 2**：测试参数不匹配设备能力（如通道数超过设备支持上限、波特率配置异常）。

**解决方案 2**：修改脚本参数（示例：测试 2 通道、500k/4M 波特率、50 万数据包）：

```
sudo ucanfd_test.sh -c 2 -b 500000 -d 4000000 -t 500000
```

**补充**：测试日志默认保存在当前目录（如`ucanfd_test_20250909_173210`），可查看日志排查具体错误。




#### 联系支持

若遇到 SDK 安装或使用问题，可通过以下方式获取技术支持：

- **微信公众号**：搜索 “鲲弘电子 KUNHONG”
- **技术支持邮箱**：support@cdkhdz.com
- **销售咨询**：sales@cdkhdz.com

