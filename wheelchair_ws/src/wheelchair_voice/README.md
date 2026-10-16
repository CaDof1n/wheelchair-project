# wheelchair_voice

**所有者：语音交互与多模态控制组**

离线语音识别、意图解析与对话。

## 本包负责的接口

| 接口 | 方向 | 说明 |
|---|---|---|
| `/wheelchair/voice/text` | 发布 | `std_msgs/msg/String`，事件驱动 |
| `/wheelchair/voice/intent` | 发布 | `wheelchair_interfaces/msg/VoiceIntent`，事件驱动 |

## 硬性约束

- **禁止**直接执行安全关键动作（标准表 2-1「禁止事项」）。
- 语音**通常只生成导航目标，不直接持续发布速度**（标准 §4.5 第 2 条）。
- 安全关键动作（站立/急停/推杆）必须经状态机与安全过滤器，不得由语音绕过。
- **离线识别为基线**；云端大模型 API **只能**通过 HTTPS 443 提供非安全关键的意图解析服务，且必须可整体关闭（标准 §2，D9）。
- `intent` 取值见标准**表 C-1**（STOP、CANCEL、MOVE_FORWARD、MOVE_BACKWARD、TURN_LEFT、TURN_RIGHT、STAND_UP、SIT_DOWN、GRASP、RELEASE、NAVIGATE_TO 共 11 项），会签确认后即为冻结接口。
- 急停或故障锁存期间，除 STOP 与 CANCEL 外的全部意图必须拒绝并回报原因；MOVE_* 不得持续发布 Twist，须译为不超过 2 s 的限时低速动作（附录 C）。
- **API 密钥通过环境变量或密钥文件注入，不得提交 Git**（标准 §7.2）。
- **不得**向外部 AI 服务提交 API 密钥、密码、个人信息、校园内网地址或未经许可的敏感数据（标准 §10.1）。

## VoiceIntent 字段要点（标准附录 A.4）

`intent`（取值见表 C-1）、`parameter_names` / `parameter_values`（一一对应）、`confidence`、`original_text`、
`request_id`（链路追踪 ID，用于跨节点串联同一次请求）。

`confidence` 低于阈值应丢弃并上报，不得把低置信结果静默传给状态机。

## 验收

- **IF-02** 接口名称与类型与注册表一致
- 语音触发的动作在仿真中验证不会绕过 `safety_filter`
