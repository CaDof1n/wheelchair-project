# RangeArray.msg
# 标准 §附录A.3  —  发布方：串口桥 / 频率：10 Hz / QoS：SENSOR
# 对应话题 /wheelchair/ultrasonic/ranges
# 按传感器名与距离数组成对发布，sensor_names 与 ranges_m 长度必须一致。

std_msgs/Header header

string[] sensor_names        # 传感器名称，须与 URDF/安装台账一致
float32[] ranges_m           # 距离，m；无效值用 NaN 并同步上报诊断
float32 min_range_m          # 本组传感器量程下限
float32 max_range_m          # 本组传感器量程上限
