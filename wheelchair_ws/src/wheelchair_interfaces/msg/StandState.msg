# StandState.msg
# 标准 §附录A.5  —  发布方：推杆控制节点 / 频率：10 Hz / QoS：STATE
# 对应话题 /wheelchair/stand/state
#
# 注意：V1.0 文档附录 A 中状态常量与字段交错，此处按 ROS 2 要求将常量前置。

std_msgs/Header header

# 状态定义
uint8 UNKNOWN=0
uint8 SEATED=1
uint8 MOVING_TO_STAND=2
uint8 STANDING=3
uint8 MOVING_TO_SEAT=4
uint8 FAULT=5

uint8 state
float32 position_ratio       # 行程比例 0.0 ~ 1.0
bool lower_limit             # 下限位开关触发
bool upper_limit             # 上限位开关触发
uint32 fault_bits            # 推杆相关故障位，见表 12
