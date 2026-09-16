# wheelchair_manipulation

**所有者：机械臂视觉与抓取控制组**

目标检测、目标定位、MoveIt 2 规划与抓取执行。

## 本包负责的接口

| 接口 | 方向 | 说明 |
|---|---|---|
| `/camera/color/image_raw` | 订阅 | 15-30 Hz |
| `/camera/depth/points` | 订阅 | 5-15 Hz，可按算力降频 |
| `/wheelchair/perception/detections` | 发布 | `vision_msgs/msg/Detection3DArray`，5-15 Hz |
| `/wheelchair/perception/target_pose` | 发布 | `geometry_msgs/msg/PoseStamped`，**必须给出 `frame_id` 和时间戳** |
| `/wheelchair/arm/grasp_object` | Action 服务端 | `wheelchair_interfaces/action/GraspObject` |

## 硬性约束

- **禁止**自行定义重复 TF 根节点（标准表 4「视觉抓取」禁止事项）。
- 图像坐标遵循相机驱动约定；**进入三维目标接口前必须转换到 `frame_id` 指定的 ROS 坐标系**（标准 §3.3）。
- 光学坐标系保持 z 向前、x 向右、y 向下，业务节点**不得手工改写图像坐标含义**（标准 §5.1）。
- 二维导航姿态使用 quaternion 表达，不得直接把角度数值写入 `orientation.z`。

## 抓取动作语义（标准附录 A.7）

识别 -> 规划 -> 夹爪闭合 -> 抬升。`error_code` 取值见标准 §6.5 错误码表。

机械臂基座 `arm_base_link` 的父坐标系是 `seat_link`，关节链
`arm_base_link -> arm_link_1 ... arm_link_6 -> gripper_link` 由 `robot_state_publisher` 发布。

## 验收

- **IF-02 / IF-04** 接口与 TF 一致性
- 抓取动作在仿真中闭环验证后再上实物；涉及机械臂运动的 AI 建议必须通过仿真、单元测试和安全工况测试（标准 §10.1）
