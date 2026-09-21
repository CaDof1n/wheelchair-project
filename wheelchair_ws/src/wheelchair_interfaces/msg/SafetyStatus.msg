# SafetyStatus.msg
# 标准 §附录A.1  —  发布方：安全监督节点 / 频率：10 Hz + 事件 / QoS：STATE（RELIABLE, KEEP_LAST 10）
#
# 注意：V1.0 文档附录 A 中 Header 写在常量之前。ROS 2 的 .msg 要求常量先声明，
# 故此处将常量前置（字段顺序与语义不变，序列化结果一致）。

std_msgs/Header header

# 急停状态
uint8 ESTOP_RELEASED=0
uint8 ESTOP_PHYSICAL=1
uint8 ESTOP_SOFTWARE=2
uint8 ESTOP_BOTH=3

uint8 estop_state
bool drive_enabled
bool posture_enabled        # 来源：串口 0xA3 SAFETY_STATE 偏移 16（标准 V1.1 新增）。
                            # 载荷仅 16 字节（未含该字段）时置 false，并须通过 /diagnostics
                            # 报告「站立机构使能状态来源缺失」——bool 无法表达「未知」，
                            # 静默置 false 即评审报告 REV-001 的 A2 所述失败模式。
uint32 fault_bits          # 位定义见表 12
float32 roll_rad           # 车体滚转角，rad
float32 pitch_rad          # 车体俯仰角，rad
float32 min_obstacle_distance_m   # 最近障碍距离，m；未知用 NaN
string summary             # 人类可读摘要，供 HMI 与日志使用
