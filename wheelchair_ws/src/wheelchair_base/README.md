# wheelchair_base

**所有者：电气动力与底层控制组**

电机、推杆、限位、基础遥测；上位机与 MCU 之间的串口通信。

## 本包负责的接口

| 接口 | 方向 | 说明 |
|---|---|---|
| `/cmd_vel` | 订阅 | 唯一实物底盘速度输入，来自安全过滤器 |
| `serial_bridge` 节点 | — | ROS 2 <-> 串口帧双向桥接 |
| `/wheelchair/base/odom` | 发布 | 30 Hz，`frame_id=odom` |
| `/wheelchair/base/mcu_state` | 发布 | 10 Hz，`wheelchair_interfaces/msg/McuState` |
| `/wheelchair/imu/data` | 发布 | 50 Hz，`frame_id=imu_link` |
| `/wheelchair/ultrasonic/ranges` | 发布 | 10 Hz |
| `/wheelchair/power/battery_state` | 发布 | 1 Hz |

串口协议见 `docs/interfaces/interface_registry.yaml` 的 `serial` 段，或标准 §6。

## 硬性约束

- **禁止**绕过急停或接收未过滤速度（标准表 4「底层控制」禁止事项）。
- **禁止**硬编码串口号：必须通过参数 `serial_port` 和 `baud_rate` 配置（标准表 13）。
- 端口配置不得出现 `COM*` 或 `/dev/*` 字面量。

## 超时与失效安全（标准 §6.6）

| 条件 | 行为 |
|---|---|
| MCU 连续 **300 ms** 未收到有效 `HOST_HEARTBEAT` 或 `CMD_VEL` | 立即把底盘速度置零 |
| 连续 **1000 ms** 未收到上位机有效帧 | 置 `COMM_TIMEOUT` 并禁止驱动，直至收到合规复位 |
| `CMD_VEL` | **不重发**旧命令；上位机持续发送最新值 |
| 离散命令（配置/推杆/急停/使能） | 设 `ACK_REQ`，100 ms 无响应可重试 2 次 |
| 重复 SEQ 的离散命令 | 只执行一次，并再次返回相同 ACK |
| CRC 错误率 10 秒内 > 1% | 置 `CRC_RATE_HIGH` |

## 验收

- **IF-05** 连续 10000 帧无解析错误，字段缩放一致
- **IF-06** CRC、超长、截断帧被丢弃且不执行
- **IF-07** 300 ms 内速度归零，1000 ms 内进入通信故障

编解码测试位于 `tests/interface/`。
