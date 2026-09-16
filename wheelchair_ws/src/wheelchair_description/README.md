# wheelchair_description

**所有者：机械结构与物理装配组**

URDF / XACRO 模型、关节限位、传感器安装位姿、网格与标定外参。

## 本包负责的接口

| 接口 | 类型 | 说明 |
|---|---|---|
| `/tf_static` 中 `base_link -> 传感器` | TF | 外参来自 CAD 和实测标定（标准 §5.2） |
| `/joint_states` 的关节名 | Topic 字段 | 名称、数量和 URDF 必须一致 |
| `arm_link_1 .. arm_link_6` | TF 链 | 六轴机械臂关节链 |
| `camera_link` / `laser_frame` / `imu_link` / `seat_link` / `gripper_link` | TF | 见 `docs/interfaces/interface_registry.yaml` |

## 硬性约束

- **禁止**未经评审改变 link 或 joint 名称（标准表 4「机械结构」禁止事项）。
- **禁止**重复定义 TF 根节点。
- URDF joint 命名规则：`部件_位置_joint`，例 `front_left_wheel_joint`（标准表 6）。
- TF frame 全小写 snake_case，**不得带前导斜杠**（标准表 6）。

## 注意

标准 §5.1 规定：**相机驱动关闭 TF 发布功能**，由 `robot_state_publisher` 统一发布
`camera_link` 与两个 optical_frame 的静态变换，避免驱动与 URDF 重复发布。

## 验收（标准 §5.3 / IF-04）

```bash
ros2 run tf2_tools view_frames     # 只有一棵连通树，无重复发布警告
ros2 run tf2_ros tf2_echo base_link laser_frame
```

任意传感器数据的 `header.frame_id` 必须在 TF 树中存在，并可在其时间戳处转换到 `base_link`。

## 待办

- [ ] 接收机械组 CAD 输出的 `wheelchair.urdf` / `wheelchair.xacro`
- [ ] mesh 文件入库策略：`.dae` / `.stl` 若 >10MB 请改用 Git LFS（`build_interface_standard.py` 同目录的约定）
