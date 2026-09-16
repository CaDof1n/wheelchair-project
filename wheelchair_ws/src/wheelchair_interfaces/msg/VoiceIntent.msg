# VoiceIntent.msg
# 标准 §附录A.4  —  发布方：意图解析节点 / 事件驱动 / QoS：EVENT
# 对应话题 /wheelchair/voice/intent
#
# 安全约束：语音通常只生成导航目标，不直接持续发布速度（§4.5）。
# 安全关键动作（站立/急停/推杆）不得由语音直接执行，须经状态机与安全过滤器。

std_msgs/Header header

string intent                # 结构化意图标识，如 navigate_to / stop / query_status
string[] parameter_names     # 与 parameter_values 一一对应
string[] parameter_values
float32 confidence           # 置信度 0.0 ~ 1.0，低于阈值应丢弃并上报
string original_text         # 识别后的原始文本
string request_id            # 链路追踪 ID，用于跨节点串联同一次请求
