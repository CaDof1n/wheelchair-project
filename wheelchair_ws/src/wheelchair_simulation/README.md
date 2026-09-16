# wheelchair_simulation

**所有者：系统集成测试与项目管理组**

Gazebo / Isaac Sim 仿真环境、`use_sim_time` 与 `/clock` 管理、仿真场景与测试用例。

## 本包负责的接口

| 接口 | 角色 | 说明 |
|---|---|---|
| `/clock` | 发布 | `rosgraph_msgs/msg/Clock`，**仅仿真发布** |
| `/wheelchair/ultrasonic/ranges` | 发布 | 仿真超声波 |
| 其余传感器 Topic | 仿真替身 | 名称必须与实物**完全一致** |

## 硬性约束

- 仿真节点统一 `use_sim_time=true`；实物统一 `false`（标准 §4.1）。
- **同一仿真进程中不得混用系统时间和仿真时间**（标准 §7.3 第 4 条）。
- 仿真与实物参数分别使用 `config/sim/` 和 `config/real/`，**接口名称保持一致**，
  通过 launch 参数选择，只允许实现不同（标准 §3.4 第 2 条）。

## 验收

- **IF-10 仿真实物一致**：`sim` 和 `real` 配置仅实现不同，公开接口相同，需附接口 diff 证据。

```bash
# 接口一致性 diff 示例
ros2 topic list  > /tmp/topics_sim.txt
# 切到 real 配置后再执行一次，然后 diff
```

## 待办

- [ ] 从 `wheelchair_description` 接收 URDF/XACRO
- [ ] 搭建整车仿真场景与 50 次空载运行自动化脚本（对应标准 §1.3 安全红线）
