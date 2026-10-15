# wheelchair_supervisor

**所有者：系统集成测试与项目管理组**

状态机调度、速度复用、安全过滤、诊断聚合。

## 本包负责的接口

| 接口 | 角色 | 说明 |
|---|---|---|
| `/wheelchair/cmd_vel/nav` `/teleop` `/task` | 订阅 | 三路速度源的复用输入 |
| `/wheelchair/cmd_vel/task` | 发布 | 状态机，按需 20 Hz，仅用于低速短动作 |
| `/wheelchair/cmd_vel_raw` | 包内发布 / 订阅 | 速度复用器 -> 安全过滤器，20 Hz，QoS `CONTROL`；仲裁结果尚未经安全校验，**禁止直接下发串口** |
| `/cmd_vel` | 发布 | **安全过滤器输出，唯一实物底盘速度输入** |
| `/wheelchair/safety/status` | 发布 | `SafetyStatus`，10 Hz 加事件，QoS `STATE` |
| `/wheelchair/system/mode` | 发布 | `SystemMode`，2 Hz 加事件 |
| `/diagnostics` | 发布 | `DiagnosticArray`，诊断聚合入口 |
| `/wheelchair/voice/intent` | 订阅 | `VoiceIntent`，状态机按标准表 C-1 处理 |
| `/wheelchair/stand/state` | 订阅 | `StandState`，状态机与安全节点使用 |
| `/wheelchair/perception/detections` | 订阅 | 状态机据此调度抓取 |
| `/wheelchair/imu/data` `/wheelchair/ultrasonic/ranges` `/wheelchair/arm/wrench` | 订阅 | 安全监督输入：倾角、近距障碍、碰撞力 |
| `/wheelchair/safety/set_soft_estop` | Service 服务端 | `std_srvs/srv/SetBool`（安全监督节点） |
| `/wheelchair/system/reset_fault` | Service 服务端 | `std_srvs/srv/Trigger`（状态机） |
| `/wheelchair/system/health_check` | Service 服务端 | `std_srvs/srv/Trigger`（诊断聚合节点），详细项同时发布到 `/diagnostics` |
| `/navigate_to_pose` | Action 客户端 | 状态机下发导航目标 |
| `/wheelchair/arm/grasp_object` | Action 客户端 | 状态机下发抓取 |
| `/wheelchair/stand/change_posture` | Action 客户端 | 站立/坐下编排 |

## 速度仲裁优先级（标准 §4.5）

```
安全过滤器（最高，可把任意速度命令置零）
  > 手柄人工接管
    > Nav2
      > 状态机低速直控
```

语音通常生成导航目标，不直接持续发布速度。

复用器的仲裁结果先发布到 `/wheelchair/cmd_vel_raw`，安全过滤器限幅与门控后再发布到 `/cmd_vel`。两级之间的话题必须保留，否则二者的连接无法被独立观测与测试（IF-09）。

**速度源必须以 10 Hz 以上刷新。超过 200 ms 未更新即视为过期，复用器输出零速度。**

## 强制零速条件（标准 §4.5 第 5 条）

站立、急停、严重倾斜、串口失联或关键传感器故障时，线速度和角速度**强制为零**。

数值见 `config/sim/safety_limits.yaml` 与 `config/real/safety_limits.yaml`。

## 启动顺序（标准 §4.6）

1. `robot_state_publisher` 与静态 TF
2. 硬件驱动和 `serial_bridge`
3. `diagnostics` 与 `safety_supervisor`
4. `localization` / SLAM 与 `perception`
5. Nav2 与 MoveIt 2
6. `voice` 与 `task_supervisor`
7. `cmd_vel_mux` 与 `safety_filter` 进入 **ACTIVE**

核心节点应采用 ROS 2 **Lifecycle**。任一安全前置节点未激活时，**控制输出保持为零**。
关停顺序与启动顺序相反，并在断开串口或电源前发送零速度。

## 安全红线

- `/cmd_vel` 是唯一实物底盘速度输入；任何导航、手柄或语音节点**均不得直接连接电机驱动**。
- 安全上限必须**同时**在上位机安全过滤器和下位机固件中限制，**以更严格者为准**（标准 §3.4 第 3 条）。
- **物理急停链路必须独立于 ROS 2 和上位机。**ROS 2 软件急停只用于提前停止、联调和状态传播，**不得作为唯一安全措施**（标准 §2.1）。

## 验收

- **IF-03** 所有订阅连接成功，无 QoS incompatibility 警告
- **IF-08** 物理急停独立生效，ROS 状态正确锁存
- **IF-09** 多速度源竞争时优先级和超时符合标准 §4.5
