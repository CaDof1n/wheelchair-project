# wheelchair-project

**基于「数字孪生 (Sim-to-Real)」的多功能智能辅助轮椅 · 研发与集成**

> 第六大组 · 架构与接口规范单元（第一微单元）

本仓库是全项目的**单一代码基线**。目录结构、分支规则、提交规范均由
《第一版全局软硬件接口标准》V1.0（文档编号 **IW-IF-STD-001**）定义，任何结构调整
必须先走 ICR（接口变更申请）流程。

---

## 仓库结构

```
wheelchair-project/
├── wheelchair_ws/src/          # ROS 2 工作空间（wheelchair_ws）
│   ├── wheelchair_interfaces/  # 接口包：msg / srv / action，独立版本管理
│   ├── wheelchair_description/ # URDF / XACRO / 网格 / 标定外参
│   ├── wheelchair_base/        # 底盘驱动、serial_bridge
│   ├── wheelchair_navigation/  # SLAM、定位、Nav2
│   ├── wheelchair_manipulation/# MoveIt 2、视觉抓取
│   ├── wheelchair_voice/       # 语音识别与意图解析
│   ├── wheelchair_supervisor/  # 状态机、cmd_vel_mux、safety_filter
│   └── wheelchair_simulation/  # Gazebo / Isaac Sim
├── firmware/base_controller/   # ESP32 / STM32 下位机固件
├── config/
│   ├── sim/                    # 仿真参数（*_sim 后缀）
│   └── real/                   # 实物参数（*_real 后缀）
├── docs/
│   ├── interfaces/             # 接口标准文档 + interface_registry.yaml
│   └── tests/                  # 测试规范与报告
├── tests/interface/            # §9 接口验收自动测试（IF-01 ~ IF-10）
└── tools/                      # 编解码、诊断、日志工具
```

## 环境基线（§4.1）

| 项目 | 约定 |
|---|---|
| 操作系统 | Ubuntu 22.04 LTS |
| ROS 2 | **Humble** 为集成基线；Iron 节点须证明消息与 QoS 兼容 |
| DDS 域 | `ROS_DOMAIN_ID=26` |
| 工作空间 | `wheelchair_ws` |
| 仿真时间 | 仿真节点 `use_sim_time=true`；实物统一 `false` |

## 分支规则（§8.2）

| 分支 | 命名 | 规则 |
|---|---|---|
| 主分支 | `main` | 只保存可演示、可回退的版本，**禁止直接 push** |
| 集成分支 | `develop` | 各组联调入口，通过构建与接口测试后合并 |
| 功能分支 | `feature/gN-issue-short-name` | N 为大组编号，一个分支一个任务 |
| 修复分支 | `fix/gN-issue-short-name` | 修复缺陷，不夹带无关重构 |
| 发布分支 | `release/vX.Y` | 冻结接口，只允许修复阻断问题 |
| 标签 | `vX.Y.Z` | 阶段验收、仿真验收、实物验收必须打标签 |

提交信息格式：`type(scope): summary`
例：`feat(interface): add safety status message`

## 安全红线（§1.3）

完成连续 **50 次稳定空载运行**及 **50–70 kg 沙袋配重测试**前，
**严禁人员乘坐**进行通电或动态测试。

实物初期速度上限：线速度 `0.20 m/s`、角速度 `0.40 rad/s`（§4.5）。
安全上限必须**同时**在上位机安全过滤器与下位机固件中限制，以更严格者为准。

## 接口变更

1. 在 Issue 中提交 **ICR**（模板：`.github/ISSUE_TEMPLATE/icr.yml`）
2. 接口所有者 + 架构组 + 受影响组评估兼容性与安全影响
3. V1.x 兼容性新增由架构组批准；**破坏性修改须经六大组接口负责人共同确认**
4. 先改 `wheelchair_interfaces` 与 `docs/interfaces/interface_registry.yaml`，再改发布方/订阅方

V1.x 内**不得**改变已有字段含义。新增可选字段或接口 → 次版本；破坏兼容性 → V2.0。

## 快速开始

```bash
cd wheelchair_ws
colcon build --symlink-install
source install/setup.bash

# 接口包自检
ros2 interface list | grep wheelchair_interfaces
ros2 topic list
ros2 run tf2_tools view_frames     # TF 单树连通性（IF-04）
```

## AI 工具使用

依据课程任务书学术诚信要求及本标准 §10：AI 生成的代码/文档须在 PR 中登记工具名称、
输入目的、采用内容、人工修改与验证结果。**AI 输出不得未经验证直接进入安全关键控制链路。**
