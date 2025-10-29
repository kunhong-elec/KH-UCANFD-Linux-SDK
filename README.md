# KH-UCANFD_Linux_SDK


## SDK 介绍
KH-UCANFD_Linux_SDK是专为鲲弘 CAN FD 系列硬件产品设计，提供基于 SocketCAN 标准的深度优化 Linux 驱动及工具，旨在解决 Linux 社区原生驱动性能瓶颈问题，充分释放 CAN FD 设备的吞吐能力并降低 CPU 开销。
- **提供标准SocktCAN接口驱动** 
  - 支持SocktCAN二次开发
  - 支持can-utils, 如cansend，candump等命令
  - 支持python-can
- 源码形式发布,可针对不同目标系统编译/交叉编译
- 支持X86或ARM/ARM64平台
- 支持Linux 内核版本：2.6.x, 3.x，4.x, 5.x, 6.x
- 支持Linux实时扩展，如Xenomai或RTAI(RTDM)

[截图/ip -d link show]

### 支持硬件
适配鲲弘 CAN FD 系列硬件设备：
- **KH-UCANFD-Mini 系列产品**（6 通道 CAN FD 接口设备）
- 其他鲲弘 CAN FD 系列兼容设备（参考产品手册确认）

### 使用场景
鲲弘 CAN FD 系列产品均支持Linux 内核自带的SocketCAN驱动
相较于 Linux 系统自带的驱动，KH-UCANFD_Linux SDK有以下特性：
- 同样支持SocktCAN驱动
- 针对硬件进行深度优化，性能显著提升
- 提供转为硬件定制的状态监测工具：lskcan和kcanmoniter

**性能对比**：
关键测试数据（基于 KH-UCANFDX6-Mini + Ubuntu 22.04.3 LTS + 内核 6.8.0）
  | 指标                    | Linux社区驱动    | KH-UCANFD SDK  | 提升效果       |  
  | ----------------------- | ---------------- | -------------- | -------------- |  
  | CAN FD 帧率（1M/5M）    | 2800 帧 / 秒     | 20500 帧 / 秒  | 约**7 倍**提升 |  
  | CAN 总线负载率（1M/5M） | 14%              | 103%（满负载） | 达到极限负载   |  
  | CPU 开销                | 单核心占用超 50% | 无明显占用     | 降低约**85%**  |  

测试数据来源：[KCANFD_Test.md](KCANFD_Test.md)  
![性能对比图](images/2.png)  

### 状态监测工具  
KH-UCANFD_Linux SDK集成kcan_monitor和lskcan工具，用户可以轻松监测和分析设备CAN/FD接口状态。  
kcan_monitor可实时监测CAN总线状态和CAN传输帧率统计:  
![监视器演示](images/monitor.png)  
- **dev name**：设备物理标识与通道号  
- **ndev**：Linux 系统中 SocketCAN 子系统分配的网络接口名，如 “can0”“can1”，可通过该名称使用`candump`、`cansend`等标准工具操作。  
- **bits**：CAN FD 波特率配置，格式为 “仲裁段波特率 + 数据段波特率”。  
- **bus**：总线工作状态：  
  - ACTIVE：正常激活状态  
  - PASSIVE：被动状态  
  - BUSOFF：总线关闭状态  
- **%bus**：总线负载率  
- **%tx fifo**：发送缓冲区使用率  
- **rx_fr/s**：每秒接收帧数  
- **tx_fr/s**：每秒发送帧数  
- **rx**：累计接收帧数  
- **tx**：累计发送帧数  
- **rec/tec**：接收错误计数 / 发送错误计数：  
- **err**：累计错误数，包含位错误、填充错误等各类 CAN 总线错误的总计数。  

lskcan列举CAN接口详细信息:  
![列表信息演示](images/lskcan.png)  
一次性列举所有接口的设备状态，以及详细的波特率配置，便于用户检查CAN设备状态。

## 二次开发支持

### SocketCAN
#### SocketCAN介绍与can-utils入门上手
https://github.com/linux-can/can-utils
#### SocketCAN编程

### python-CAN

## 安装教程

### 1. 安装前系统环境要求
1. Linux系统运行32位或64位内核
2. make、gcc编译工具
3. Linux系统的内核头文件包（或Linux头文件包），或交叉编译内核的源码树
4. g++编辑器及libstdc++库
5. libpopt-dev包


### 2. 依赖安装命令
```bash
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


### 3. SDK下载
可在releases中手动下载，或使用wget下载。
```bash
# 安装wget（若未安装）
sudo apt install -y wget

# 下载SDK（最新版本）
wget https://gitee.com/ChengDu-KunHong/KH-UCANFD_Linux_SDK/releases/download/latest/KH-UCANFD_Linux_SDK.zip

# 解压SDK（替换x.y.z为实际版本号）
unzip KH-UCANFD_Linux_SDK.zip && cd KH-UCANFD_Linux_SDK_x.y.z/
```


### 4. 编译与安装
执行以下命令完成驱动编译和安装（需 sudo 权限）：
```bash
# 清理历史编译文件
sudo make clean

# 编译驱动（若报错，检查依赖是否齐全、gcc版本是否匹配）
sudo make

# 安装驱动（无报错则安装成功）
sudo make install
```


### 5. 驱动加载验证
加载驱动：
```bash
# 加载kcan驱动模块
sudo modprobe kcan

# 验证驱动是否加载成功（输出含"kcan"即正常）
lsmod | grep kcan
```
![列表信息演示](images/lsmod.png)  
重新拔插 CAN FD 设备后，执行以下命令确认设备被识别：
```bash
# 查看CAN接口信息（输出含"can0"、"can1"等接口即正常）
ip -d link show
```  
![iplinkshow](images/ipdlinkshow.png)  
```bash
# 查看USB设备驱动绑定（输出含"Driver=kcan"即正常）
lsusb -t
```  
![iplinkshow](images/lsusb-t.png)  

## 常见问题

### Q1：驱动加载时报错 “modprobe: ERROR: could not insert 'pcan': Key was rejected by service”
**原因**：系统启用了 Secure Boot（安全启动），阻止了未签名的第三方驱动加载。  
**解决方案**：进入主板 BIOS/UEFI 设置，关闭 Secure Boot 功能（具体步骤需根据主板型号查询，常见路径：BIOS → Security → Secure Boot → Disabled）。


### Q2：运行`kcanfd_test.sh`测试脚本时丢包或测试失败
**原因 1**：CAN 接口通道未正确对接（脚本需通道两两交叉连接）。  
**解决方案 1**：将设备的 can0 与 can1、can2 与 can3 等通道两两用 CAN 线连接（需接终端电阻，若硬件自带则无需额外添加）。  

**原因 2**：测试参数不匹配设备能力（如通道数超过设备支持上限、波特率配置异常）。  
**解决方案 2**：修改脚本参数（示例：测试 2 通道、500k/4M 波特率、50 万数据包）：
```bash
sudo kcanfd_test.sh -c 2 -b 500000 -d 4000000 -t 500000
```

**补充**：测试日志默认保存在当前目录（如`kcanfd_test_20251028_101329`），可查看日志排查具体错误。  
![测试日志目录结构](images/lstree.png)  

## 达妙电机控制demo
使用UCANFD_SDK搭配UCANFDX6，通过socketcan控制达妙电机动作。  
![达妙电机](images/damiao.png)  
demo链接：https://gitee.com/ChengDu-KunHong/KH-UCANFD-motor-demo/tree/hoyo/DM  

## 联系支持
若遇到 SDK 安装或使用问题，可通过以下方式获取技术支持：
- **微信公众号**：搜索 “鲲弘电子 KUNHONG”
- **技术支持邮箱**：support@cdkhdz.com
- **销售咨询**：sales@cdkhdz.com  

![鲲弘电子公众号二维码](images/QR.png)