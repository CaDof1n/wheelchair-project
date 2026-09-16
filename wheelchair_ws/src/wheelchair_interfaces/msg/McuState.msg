# McuState.msg
# 标准 §附录A.2  —  发布方：串口桥 / 频率：10 Hz / QoS：STATE
# 对应话题 /wheelchair/base/mcu_state

std_msgs/Header header

string firmware_version      # 固件版本字符串
uint32 uptime_ms             # MCU 启动后毫秒数
uint32 valid_rx_frames       # 累计有效接收帧数
uint32 crc_error_frames      # 累计 CRC 错误帧数
uint32 timeout_count         # 累计通信超时次数
uint16 last_rx_seq           # 最近一次有效接收的 SEQ
uint8 controller_state       # 控制器状态，取值见固件侧枚举
