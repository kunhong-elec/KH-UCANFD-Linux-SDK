# SocketCAN编程实践

## 基础应用
### 初始化socket
```
int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
```

### 绑定接口
```
struct sockaddr_can addr;
struct ifreq ifr;

strcpy(ifr.ifr_name, "can0");
ioctl(s, SIOCGIFINDEX, &ifr);

addr.can_family = AF_CAN;
addr.can_ifindex = ifr.ifr_ifindex;

bind(s, (struct sockaddr *)&addr, sizeof(addr));
```

### 发送报文
```
struct can_frame frame;
frame.can_id = 0x123;
frame.can_dlc = 8;
memcpy(frame.data, "\x11\x22\x33\x44\x55\x66\x77\x88", 8);

write(s, &frame, sizeof(frame));
```

### 接收报文
```
int nbytes = read(s, &frame, sizeof(frame));
printf("CAN ID: %03X\n", frame.can_id);
```

## 应用技巧

### 设置过滤规则
```
struct can_filterr filter[1];
rfilter[0].can_id = 0x123;
rfilter[0].can_mask = CAN_SFF_MASK;
setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, &rfilter, sizeof(rfilter)); 
```

### 非阻塞模式
```
fcntl(s, F_SETFL, O_NONBLOCK);
``` 