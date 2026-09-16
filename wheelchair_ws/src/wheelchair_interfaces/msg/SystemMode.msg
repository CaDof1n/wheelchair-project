# SystemMode.msg
# 标准 §附录A.6  —  发布方：状态机 / 频率：2 Hz + 事件 / QoS：STATE
# 对应话题 /wheelchair/system/mode
#
# 注意：V1.0 文档附录 A 中状态常量与字段交错，此处按 ROS 2 要求将常量前置。
# 各模式的速度限制见标准 §2.2 运行模式表 与 §4.5 速度命令仲裁。

std_msgs/Header header

# 运行模式，与标准表 3「运行模式」一致
uint8 INIT=0
uint8 SIMULATION=1
uint8 MANUAL=2
uint8 AUTONOMOUS=3
uint8 STANDING=4
uint8 FAULT=5
uint8 ESTOP=6

uint8 mode
string reason                # 模式变更原因，供日志与 HMI 显示
