# wheelchair_navigation

**所有者：自动导航与 SLAM 算法组**

SLAM、定位、路径规划与避障。

## 本包负责的接口

| 接口 | 方向 | 说明 |
|---|---|---|
| `/scan` | 订阅 | 5-15 Hz，`frame_id=laser_frame` |
| `/map` | 发布 | `frame_id=map`，QoS `STATIC` |
| `/wheelchair/cmd_vel/nav` | 发布 | 10-20 Hz，QoS `CONTROL`，重映射到速度复用器 |
| `map -> odom` | TF（`/tf`，QoS `TF`） | **唯一发布方**：SLAM 或定位节点二选一 |
| `odom -> base_footprint` | TF（`/tf`，QoS `TF`） | 与 EKF 二选一 |
| `/navigate_to_pose` | Action 服务端 | `nav2_msgs/action/NavigateToPose` |
| `/wheelchair/base/odom` | 订阅 | 30 Hz，`frame_id=odom` |
| `/camera/depth/points` | 订阅 | 5-15 Hz，融合进代价地图 |
| `/wheelchair/ultrasonic/ranges` | 订阅（可选） | 50 Hz，近距避障；`sensor_names` 未定前该话题不会发布（T3） |

## 硬性约束

- **禁止**直接写串口或控制电机 PWM（标准表 2-1「禁止事项」）。
- **禁止**直接发布 `/cmd_vel`：必须经 `cmd_vel_mux` -> `safety_filter`（标准 §2.1）。
- **禁止**再包装第二套导航 Action；标准点到点导航一律走 `/navigate_to_pose`（标准表 4-4）。
- `map` 与 `odom` 职责不得交换：`map` 可全局校正，`odom` 必须局部连续（标准 §5.3）。
- SLAM 基线为 **slam_toolbox**，Cartographer 列备选，**二者不得同时运行**（D2）。
- 坐标系用 **`base_footprint`** 与 **`laser_frame`**，不得写成 `base_link` / `laser_link`（D3，REP 105）。

## TF 所有权（标准 §5.2）

切换模式时**不得**同时运行两个 `map -> odom` 发布源。这是 P1 级问题的典型来源。

## 验收

- **IF-02** `ros2 topic list/type` 与注册表一致，无重复私有替代接口
- **IF-04** TF 单树连通、唯一发布、时间戳有效
- **IF-09** 多速度源竞争时优先级和超时符合标准 §4.5
