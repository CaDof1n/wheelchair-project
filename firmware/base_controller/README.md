# firmware/base_controller

**所有者：电气动力与底层控制组**

ESP32 / STM32 下位机固件。负责电机驱动、推杆控制、限位采集、基础遥测，
以及上位机与执行机构之间的串口协议实现。

## 协议实现依据

标准 §6 与 `docs/interfaces/interface_registry.yaml` 的 `serial` 段。

| 项目 | 值 |
|---|---|
| 接口 | USB CDC / USB 转 UART（长线可用隔离 RS-485） |
| 波特率 | 115200 |
| 数据格式 | 8N1 |
| 字节序 | little-endian |
| 最大载荷 | 128 byte |
| 帧界定 | 二进制帧，**无行结束符** |

## 帧格式

| 偏移 | 长度 | 字段 | 说明 |
|---|---|---|---|
| 0 | 2 | `SOF` | 固定 `0xAA 0x55` |
| 2 | 1 | `VERSION` | V1.0 固定 `0x01` |
| 3 | 1 | `MSG_ID` | 消息编号 |
| 4 | 1 | `FLAGS` | bit0 `ACK_REQ`, bit1 `IS_ACK`, bit2 `IS_ERROR`，**其余必须为 0** |
| 5 | 2 | `SEQ` | uint16，发送方每帧递增，溢出回 0 |
| 7 | 2 | `LENGTH` | PAYLOAD 字节数，0–128 |
| 9 | N | `PAYLOAD` | 按 `MSG_ID` 解释 |
| 9+N | 2 | `CRC16` | CRC-16/MODBUS，覆盖 `VERSION` 至 `PAYLOAD`，**低字节先发送** |

接收端先查找 `SOF`，再读固定头和 `LENGTH`。
**`LENGTH` 超过 128 时立即丢弃并重新同步。**
**CRC 错误帧不得执行，也不得用其中的 `SEQ` 更新有效序号。**

## 消息编号

| ID | 名称 | 方向 | 频率 |
|---|---|---|---|
| `0x01` | HOST_HEARTBEAT | HOST -> MCU | 10 Hz |
| `0x10` | CMD_VEL | HOST -> MCU | 20 Hz |
| `0x11` | CMD_POSTURE | HOST -> MCU | 事件 |
| `0x12` | CMD_SOFT_ESTOP | HOST -> MCU | 事件 |
| `0x13` | CMD_OUTPUT_ENABLE | HOST -> MCU | 事件 |
| `0x7E` | ACK_NACK | 双向 | 响应 |
| `0x81` | MCU_HEARTBEAT | MCU -> HOST | 10 Hz |
| `0xA0` | BASE_STATE | MCU -> HOST | 30 Hz |
| `0xA1` | IMU_STATE | MCU -> HOST | 50 Hz |
| `0xA2` | POWER_STATE | MCU -> HOST | 1 Hz |
| `0xA3` | SAFETY_STATE | MCU -> HOST | 10 Hz + 事件 |
| `0xA4` | ULTRASONIC_STATE | MCU -> HOST | 10 Hz |

## CMD_VEL 载荷

| 偏移 | 类型 | 字段 | 单位与范围 |
|---|---|---|---|
| 0 | int16 | `linear_x` | mm/s；实物初期 **-200 ~ 200** |
| 2 | int16 | `angular_z` | mrad/s；实物初期 **-400 ~ 400** |
| 4 | uint16 | `timeout_ms` | 命令有效期，100–500，推荐 **200** |

## 固件侧安全要求

- **安全上限必须同时在上位机安全过滤器和本固件中限制，以更严格者为准**（标准 §3.4 第 3 条）。
  固件常量命名规则：大写 snake_case，例 `MAX_LINEAR_MM_S`（标准表 6）。
- 连续 **300 ms** 未收到有效 `HOST_HEARTBEAT` 或 `CMD_VEL` -> **立即把底盘速度置零**。
- 连续 **1000 ms** 未收到上位机有效帧 -> 置 `COMM_TIMEOUT` 并**禁止驱动**，直至通信恢复且收到合规复位。
- 自检未通过时**拒绝** `CMD_OUTPUT_ENABLE`。
- **物理急停链路必须独立于上位机和 ROS 2**，硬件断能或禁止驱动，
  同时由 MCU 上报 `SAFETY_STATE`（标准 §2.1）。

## 示例帧

SEQ=42、线速度 200 mm/s、角速度 0、有效期 200 ms 的 `CMD_VEL` 帧，请求 ACK：

```
AA 55 01 10 01 2A 00 06 00 C8 00 00 00 C8 00 22 81
```

`CRC16/MODBUS = 0x8122`，低字节先发送。

## 验收

- **IF-05** 连续 10000 帧无解析错误，字段缩放一致
- **IF-06** CRC、超长、截断帧被丢弃且不执行
- **IF-07** 300 ms 内速度归零，1000 ms 内进入通信故障
- **IF-08** 物理急停独立生效，ROS 状态正确锁存

## 待办

- [ ] 确定 MCU 型号（ESP32 或 STM32）与构建工具链（PlatformIO / STM32CubeIDE）
- [ ] 实测资源占用、字节序、错误恢复与电机停止时延（标准 AI 记录表要求电气组实测）
