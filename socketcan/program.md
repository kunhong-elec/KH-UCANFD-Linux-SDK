# SocketCAN编程实践

## API
SocketCAN 官方API：  
https://docs.kernel.org/networking/can.html       

## 示例
### kcanfdtest
KH-UCANFD_Linux_SDK中包含kcanfd_test.c、cantx_1KHz.c 等测试代码。       
以下是kcanfd_test.c中的部分代码，用于创建套接字、发送、接收：       
详细代码内容可下载查看： https://gitee.com/ChengDu-KunHong/KH-UCANFD_Linux_SDK/releases/download/latest/KH-UCANFD_Linux_SDK.zip
#### 创建套接字
```
if ((sockfd = socket(family, type, proto)) < 0) // 创建CAN原始套接字
	{
		perror("socket");
		return 1;
	}

	if (echo_gen) // 启用生成模式
	{
		if (setsockopt(sockfd, SOL_CAN_RAW, CAN_RAW_RECV_OWN_MSGS,
					   &enable_socket_option, sizeof(enable_socket_option)) == -1)
		{
			perror("setsockopt CAN_RAW_RECV_OWN_MSGS");
			return 1;
		}
	}

	if (is_can_fd) // 启用CAN FD帧
	{
		if (setsockopt(sockfd, SOL_CAN_RAW, CAN_RAW_FD_FRAMES,
					   &enable_socket_option, sizeof(enable_socket_option)) == -1)
		{
			perror("setsockopt CAN_RAW_FD_FRAMES");
			return 1;
		}
```
#### 发送报文
```
static int send_frame(struct canfd_frame *frame)
{
	ssize_t ret, len;

	if (is_can_fd)
		len = sizeof(struct canfd_frame);
	else
		len = sizeof(struct can_frame);

	if (bit_rate_switch)
		frame->flags |= CANFD_BRS;

	while ((ret = send(sockfd, frame, len, 0)) != len)
	{
		if (ret >= 0)
		{
			fprintf(stderr, "send returned %zd", ret);
			return -1;
		}
		if (errno != ENOBUFS)
		{
			perror("send failed");
			return -1;
		}
		if (verbose)
		{
			printf("N");
			fflush(stdout);
		}
	}
	return 0;
}
```

#### 接收报文
```
static int recv_frame(struct canfd_frame *frame, int *flags)
{
	struct iovec iov = {
		.iov_base = frame,
		.iov_len = is_can_fd ? sizeof(struct canfd_frame) : sizeof(struct can_frame),
	};
	struct msghdr msg = {
		.msg_iov = &iov,
		.msg_iovlen = 1,
	};
	ssize_t ret;

	ret = recvmsg(sockfd, &msg, 0);
	if (ret < 0)
	{
		perror("recvmsg() failed");
		return -1;
	}
	if ((size_t)ret != iov.iov_len)
	{
		fprintf(stderr, "recvmsg() returned %zd", ret);
		return -1;
	}

	if (flags)
		*flags = msg.msg_flags;

	return 0;
}
```
### can-utils
can-utils是基于SocketCAN实现的，项目中提供的各种工具的代码都是很好的参考示例。       
can-utils开源项目：       
https://gitee.com/ChengDu-KunHong/can-utils

### openarm_can
openarm_can是OpenArm项目中的一部分，是用于CAN通信的库，其中提供了针对电机的应用和测试的代码，可以参考。    
openarmcan开源项目：       
https://gitee.com/ChengDu-KunHong/openarmcan

