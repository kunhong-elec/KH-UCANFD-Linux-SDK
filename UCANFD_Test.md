# ucanfdtest测试脚本使用方法  
#### 介绍
在KH-socket-can-test/文件夹中提供了若干测试程序/脚本  
ucanfd_test.sh脚本是为测试UCANFD设备在满负载条件下，是否能够正常收发数据不丢包。  
驱动安装完成后，命令行运行sudo ucanfd_test.sh，脚本将自动进行驱动加载、参数设置、收发数据包、验证结果等功能。  
#### 测试步骤
测试前，需将设备CAN接口按通道顺序两两对接，  
可参考测试UCANFDX6接线：  
 <img src="images\UCANFDX6.png" />  
脚本测试详细流程如下图：  
<img src="images\1.png" />  
 
**注**：  
脚本默认测试6通道和1M/5M波特率，可根据需求修改通道数（≤12）、波特率、测试数据包数量。  
*例：sudo ucanfd_test.sh -c 2 -b 500000 -d 4000000 -t 500000#开启can0和can1两个通道，波特率设置500k/4M，测试收发500000数据包*  
日志将保存在运行脚本的目录下。
 <img src="images\testlog.png" />  
如下图所示，包含测试日志、帧率和接口收发数据量记录。
<img src="images\lstree.png" />  	 
