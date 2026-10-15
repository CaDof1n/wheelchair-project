# docs/interfaces

**所有者：第六大组 · 架构与接口规范单元（接口文档负责人）**

## 当前版本

**《第一版全局软硬件接口标准》V1.0（IW-IF-STD-001），第四周发布。**

| 文件 | 说明 |
|---|---|
| `第一版全局软硬件接口标准_V1.0.docx` | 标准正文 IW-IF-STD-001 **当前版本** |
| `interface_registry.yaml` | **全局接口注册表**（机器可读）。QoS 档 / Topic / Service / Action / TF / 串口 / 已闭环 ICR / TBD 项 |
| `整机通信架构框图.png` `.svg` | 图 1，标准 §2 引用（300 dpi） |
| `各组汇报接口对齐差异清单.md` | 与五组方案汇报对表的差异裁决记录，标准 V1.0 全部变更的依据 |
| `表号映射表.md` | 表号重编对照，旧草案表号 → V1.0 表号 |
| `自检清单.md` | **改接口后、提交前要跑的检查**（接口包构建 / 文档一致性 / 渲染 / PR 门禁） |
| `archive/` | 正式发布前的内部草案（V1.0 / V1.1 / 评审报告 Rev.B）。**不再对外引用**，见 `archive/README.md` |

> **版本号说明**：V1.0 的版本号**重新起算**，与归档的旧 V1.0 / V1.1 **无继承关系**。
> 旧稿是在未与其他五个大组逐条对表之前编写的内部雏形，其中若干定义与五组后来的
> 方案汇报直接冲突。把草案与正式版并列存放会让「哪一份才算数」在联调时产生歧义，
> 因此旧稿统一降级归档。

## V1.0 相对内部草案的主要变化

变更的完整依据（两组原话、PPT 页码出处、裁决理由）见
`各组汇报接口对齐差异清单.md`。摘要如下。

### D 类 · 跨组差异裁决（10 项）

| 编号 | 事项 | 裁决 |
|---|---|---|
| D1 | ROS 2 发行版 | 基线 **Humble**；Iron 不考虑；Jazzy 仅作 SO-ARM 上游参考 |
| D2 | SLAM 框架 | 基线 **slam_toolbox**，Cartographer 列备选，二者不得同时运行 |
| D3 | 坐标系命名 | **保留 `base_footprint` 与 `laser_frame`**（REP 105） |
| D4 | 上位机平台 | **香橙派 5（8 GB, RK3588S）** |
| D5 | 串口链路拓扑 | 明确**两级**：上位机 ↔ ESP32 走第 6 章帧；ESP32 ↔ STM32 为组内实现 |
| D6 | 心跳超时 | **300 ms → 200 ms**（取严者） |
| D7 | 超声波频率 | **10 Hz → 50 Hz**，10 Hz 记为下限 |
| D8 | 速度上限 | 区分三层：安全上限 < 台架调试限速 < 机械设计上限 |
| D9 | 云端大模型 | **离线识别为基线**；云端意图解析仅限非安全关键且可整体关闭 |
| D10 | 接口所有者 | 表 2-1 补齐安全监督 / 仿真 / 工程管理三行（ICR-002 闭环） |

### G 类 · 缺口新增（10 项）

`/arm_controller/follow_joint_trajectory`、`/wheelchair/arm/wrench`、
`/arm_camera/*` 臂端相机话题与 frame、附录 C 语音意图枚举、语音优先级与急停联动、
`fault_bits` 新增 bit10 `WHEEL_STALL`、ICR-001 九条载荷表代拟、
新增 QoS 档 `TF`、环境交付方式、图 1 整机通信架构框图。

### T 类 · 标记 TBD（4 项）

母线电压（T1）、下位机通信路线（T2）、超声波阵列数量与命名（T3）、
臂端相机型号与手眼外参（T4）。本版**冻结其接口名称与帧结构**，
但不代为裁定数值，避免后续返工。登记于注册表 `tbd_items`。

### F 类 · 结构性修正（9 项）

表号体系重编（30 张 → 40 张，全部补全题注，另出 `表号映射表.md`）、
术语统一、表 1-1～1-3 重写、附录 B 改为「第一版交付检查表」、
附录 A 常量前置、新增附录 C、环境基线表增补、`/tf` 改 `TF` 档、
第 10 章补本版 AI 应用记录。

## 注册表维护规则

标准 §8.3 规定：**涉及 Topic、Service、Action、TF、串口或参数的改动，
必须同步更新 `interface_registry.yaml`**，否则 PR 不予合并。

任何条目变更都必须附带 ICR 编号（`.github/ISSUE_TEMPLATE/icr.yml`）。

### 版本规则（标准 §8.5）

| 变更 | 版本示例 | 处理方式 |
|---|---|---|
| 修正文档错字、实现缺陷，不改变接口 | 1.0.0 -> 1.0.1 | 补丁版本 |
| 新增兼容 Topic、可选字段或诊断项 | 1.0 -> 1.1 | 次版本，旧调用仍可工作 |
| 修改类型、字段顺序、单位、语义或删除接口 | 1.x -> 2.0 | 主版本，**必须迁移评审** |

**V1.x 内不得改变已有字段含义**（标准 §1.5 第 4 条）。

### V1.0 注册表结构

```
meta             文档标识、版本、编制单位
nan_policy       NaN 允许字段 + 串口哨兵 0xFFFF 的转换规则
qos_profiles     6 档 QoS（CONTROL / STATE / SENSOR / EVENT / STATIC / TF）
topics           33 条 Topic
services         3 条 Service
actions          4 条 Action
tf_frames        16 条 frame 定义
tf_ownership     5 条变换的唯一发布方
serial           物理层 / 帧格式 / 12 条消息编号 / 12 张载荷表 / 故障位 /
                 错误码 / 超时策略 / 示例帧
resolved_icrs    已闭环 ICR-001 / 002 / 003
tbd_items        待实测标定项 T1 ~ T4
```

## 已闭环 ICR

三项原 `pending_icrs` 已在 V1.0 中裁决并落地，转为 `resolved_icrs` 登记。

| 编号 | 事项 | 责任方 | Issue | 结论 |
|---|---|---|---|---|
| ICR-001 | 补齐 9 条串口消息的载荷字段表 | 电气动力与底层控制组 | [#2](https://github.com/CaDof1n/wheelchair-project/issues/2) | 已代拟为表 6-8 ~ 表 6-17，标注「待该组确认」 |
| ICR-002 | 表 3 与第 2 章子系统划分口径统一 | 系统集成测试与项目管理组 | [#3](https://github.com/CaDof1n/wheelchair-project/issues/3) | 表 2-1 由 6 行补至 9 行；`speed_mux` / `safety_filter` 归系统集成测试与项目管理组 |
| ICR-003 | `/tf` 的 QoS 档 | 自动导航与 SLAM 算法组 | [#4](https://github.com/CaDof1n/wheelchair-project/issues/4) | 不采用原提案的 STATE 档，改为新增 `TF` 档（RELIABLE / KEEP_LAST 100） |

> ICR-001 的「已裁决」指**架构侧已给出可实现的完整定义**；
> 载荷表的偏移、类型、缩放与哨兵取值仍须电气动力与底层控制组按固件实测确认后
> 才转为冻结。冻结前不得据此实现固件。

## 交付检查表的状态口径

标准附录 B（表 B-1）的两条口径需注意：

- **「IW-IF-STD-001 评审」记为已完成**——完成标准写的是「完成评审意见并**签字或**
  在 Git 留痕」，二者取一即可，评审报告入库即满足留痕。**各组会签尚未办理**，
  签署页（表 D-1）仍为空，若项目要求纸质或电子签章，需另行走该流程。
- **「wheelchair_interfaces ROS 2 包」已由待验证转为已完成**——2026-09-28 在
  Ubuntu 22.04.5 LTS + ROS 2 Humble（`ros:humble-ros-base` 容器；本机 CachyOS 无 ROS 2，
  经 rootless podman 运行）中执行 `colcon build --symlink-install --packages-select
  wheelchair_interfaces` 通过，`ros2 interface package` 列出 **6 个 msg 与 2 个 action 共 8 条**，
  `colcon test` 5 项全部通过。过程中另修掉一处 `package.xml` 元素顺序问题
  （`test_depend` 须在 `member_of_group` 之前，否则 xmllint 判 invalid）。

## 已知遗留项

V1.0 已处理完毕的项：

- [x] 表号 caption 与实际表格数量不符、17 张表无题注 → **表号全部重编，40 张表全部有题注**（评审 C5）
- [x] 附录 A 的 `.msg` 常量未前置（ROS 2 语法会解析失败）→ **常量一律前置**（评审 C5）
- [x] 术语不统一（「第六组第一小组」/「系统集成组」）→ **统一为「第六大组 · 架构与接口规范单元」
      与「系统集成测试与项目管理组」**
- [x] 环境交付方式未入 §4.1 → **已补「Docker 镜像或虚拟机模板」一行**
- [x] `/tf` 的 QoS 档 → **新增 TF 档，ICR-003 闭环**
- [x] `/wheelchair/ultrasonic/ranges` 的 10 Hz → **50 Hz**

仍未关闭的项：

- [ ] **各组会签**：表 D-1 签署页为空，ICR-002 的所有者归属需系统集成测试与项目管理组确认。
- [ ] **T1 ~ T4**：见注册表 `tbd_items`，需硬件选型或实测数据。
- [x] **`wheelchair_interfaces` 独立构建验证**：2026-09-28 于 Ubuntu 22.04.5 LTS + ROS 2 Humble 通过，见上文「交付检查表的状态口径」。
- [ ] **URDF / XACRO**：尚未提交至 `wheelchair_description`，TF 树初版无法在 RViz 2 实际加载。
