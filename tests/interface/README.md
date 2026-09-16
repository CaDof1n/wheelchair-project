# tests/interface

**所有者：系统集成测试与项目管理组（接口测试负责人）**

标准 §9.1 的 **IF-01 ~ IF-10** 接口验收自动测试。

## 验收项

| 编号 | 验收项 | 通过条件 | 证据 | 状态 |
|---|---|---|---|---|
| IF-01 | 接口包构建 | `wheelchair_interfaces` 在干净工作空间 `colcon build` 成功 | 构建日志 | ⬜ |
| IF-02 | Topic 名称与类型 | `ros2 topic list/type` 与注册表一致，无重复私有替代接口 | 命令输出 | ⬜ |
| IF-03 | QoS 兼容 | 所有订阅连接成功，无 QoS incompatibility 警告 | 节点日志 | ⬜ |
| IF-04 | TF 完整性 | TF 单树连通、唯一发布、时间戳有效 | `view_frames` 与 `tf2_echo` | ⬜ |
| IF-05 | 串口正常帧 | 连续 10000 帧无解析错误，字段缩放一致 | 自动测试报告 | ⬜ |
| IF-06 | 串口异常帧 | CRC、超长和截断帧被丢弃且不执行 | 故障注入日志 | ⬜ |
| IF-07 | 通信超时 | 300 ms 内速度归零，1000 ms 内进入通信故障 | 波形或日志 | ⬜ |
| IF-08 | 急停链路 | 物理急停独立生效，ROS 状态正确锁存 | 测试记录 | ⬜ |
| IF-09 | 速度仲裁 | 多速度源竞争时优先级和超时符合标准 §4.5 | rosbag 与曲线 | ⬜ |
| IF-10 | 仿真实物一致 | `sim` 和 `real` 配置仅实现不同，公开接口相同 | 接口 diff | ⬜ |

## 目录规划

```
tests/interface/
├── test_if01_build.sh
├── test_if02_topic_registry.py     # 比对 ros2 topic list 与 interface_registry.yaml
├── test_if03_qos.py
├── test_if04_tf_tree.sh
├── test_if05_serial_valid_frames.py
├── test_if06_serial_bad_frames.py  # 故障注入
├── test_if07_comm_timeout.py
├── test_if08_estop.py
├── test_if09_velocity_arbitration.py
└── test_if10_sim_real_diff.sh
```

## 运行

```bash
cd wheelchair_ws
source install/setup.bash
# 从 tests/interface 逐项执行；CI 接入后由 PR 门禁自动触发
```

## 注意

- **IF-08 安全故障复现必须使用架空轮、仿真或沙袋。**
  未通过安全门禁前禁止人员乘坐（标准 §9.3、§1.3）。
- 串口异常帧测试（IF-06）属于**故障注入**，只能在架空轮或仿真条件下进行。
- 测试失败按标准 §9.2 分级：**P0 立即停止测试**，P1 当日给出负责人和方案，
  P2 下个集成节点前解决，P3 纳入迭代。
