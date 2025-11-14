# SocketCAN

## 简介
SocketCAN是Linux内核中集成的CAN总线子系统，它将CAN总线通信接口抽象为标准的网络套接字（Socket），使开发者能够使用熟悉的BSD Socket API（如socket()、bind()、sendto()、recvfrom()等）来实现CAN总线的数据收发、设备管理等功能，极大降低了CAN应用开发的门槛。        
与传统的CAN驱动相比，SocketCAN具有良好的兼容性、可扩展性和稳定性，支持CAN 2.0A（标准帧）、CAN 2.0B（扩展帧）以及CAN FD（Flexible Data Rate，灵活数据率）等多种CAN协议类型，广泛应用于汽车电子、工业控制、智能家居等领域。


## 基础操作
以下为 SocketCAN 开发的基础操作模块，点击链接可进入对应子文档查看详细步骤与说明。

### CAN 设备初始化
- 设备识别：确认 CAN 设备是否正常挂载、获取设备基础信息（如型号、接口名）
- 设备配置：设置波特率、采样点、工作模式等核心参数，保障总线通信匹配

📚 详细操作指南：[CAN 配置手册](/socketcan/config.md)

## can-utils
can-utils 是 SocketCAN 官方配套的命令行工具集，提供了 CAN 通信的快速测试与调试能力，常见工具如下表所示。
| 工具命令    | 功能描述                                | 常用参数示例                    |
|------------|-----------------------------------------|-------------------------------|
| cansend    | 发送单条CAN报文                          | `cansend can0 123#112233445566`|
| candump    | 监听并记录CAN报文，可输出到屏幕或文件      | `candump -l -t a can0`         |
| cansniffer |  实时监听CAN报文，按ID分组显示，支持过滤   | `cansniffer -c can0`           |
| canbusload | 统计CAN总线负载率                        | `canbusload can0@500000`       |

📦 工具集完整文档：[can-utils 使用指南](/socketcan/can-utils.md)

## SocketCAN编程
SocketCAN 核心优势在于支持标准 Socket 编程接口，开发者可基于此快速实现 CAN 报文的收发、过滤与异常处理。编程模块将涵盖以下核心内容：
- SocketCAN 套接字创建与初始化（AF_CAN 协议族配置）
- CAN 报文结构解析（标准帧/扩展帧、数据段、ID 等）
- 绑定（bind）、发送（sendto）、接收（recvfrom）核心接口使用
- 报文过滤规则配置与中断处理
- CAN FD 高带宽通信编程实现     
  
💻 编程实践教程：[SocketCAN 编程开发指南](/socketcan/can-utils.md)
