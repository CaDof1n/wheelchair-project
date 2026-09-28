# tools

**所有者：第六大组 · 架构与接口规范单元**

接口相关的辅助脚本与工具。

## 规划内容

| 工具 | 用途 |
|---|---|
| `gen_iw_if_std_001.py` | **已入库**。生成《第一版全局软硬件接口标准》V1.0 的 docx。改动正文后重跑本脚本，并同步注册表 |
| `check_iw_if_std_001.py` | **已入库**。一致性校验：题注完整性、表/图引用可解析、正文与注册表交叉比对、示例帧 CRC 复算 |
| `ros_container_build.sh` | **已入库**。在容器（`ros:humble-ros-base`）里构建并验证 ROS 2 包：宿主机没有 ROS 2 时用。`src` 只读挂载，产物不落回仓库 |
| `serial_frame_codec.py` | 串口帧编解码（SOF / CRC16-MODBUS / SEQ），供 IF-05、IF-06 复用 |
| `gen_serial_example.py` | 生成标准 §6.6 的示例帧，验证 `AA 55 01 10 ... 22 81` |
| `check_interface_registry.py` | 校验 `docs/interfaces/interface_registry.yaml` 与实际 `ros2 topic list` 的差异 |
| `fault_bits_decode.py` | 把 `uint32 fault_bits` 解码为可读名称（标准 fault_bits 位定义） |
| `tf_tree_check.py` | 检查 TF 单树连通与重复发布（IF-04） |

## 用法

```bash
python tools/gen_iw_if_std_001.py      # 重新生成标准正文 docx
python tools/check_iw_if_std_001.py    # 校验正文与注册表是否一致（退出码非 0 即不一致）

tools/ros_container_build.sh                       # 容器内构建并验证 wheelchair_interfaces
tools/ros_container_build.sh wheelchair_base       # 指定包（可多个）
ROS_APT=0 tools/ros_container_build.sh             # 镜像依赖已齐时跳过 apt，提速
```

`ros_container_build.sh` 需要 `wheelchair_ws/src` 之外**没有**任何前置条件：
容器运行时用 rootless podman（Arch 系 `sudo pacman -S podman`）或 docker，
首次会拉取约 811 MB 的镜像。容器内发行版为 Ubuntu 22.04 + ROS 2 Humble，
构建日志里的发行版信息请**如实抄进验证记录**——若哪天只在别的发行版上跑通，
Humble 仍记为待验证（标准 §4.1）。

## 约定

- 所有工具**必须**从 `docs/interfaces/interface_registry.yaml` 读取定义，
  **不得**硬编码 Topic 名、MSG_ID、错误码或 fault_bits 位含义。
- 脚本输出使用 UTF-8。
- **不得**在工具中写入 API 密钥、密码或校园内网地址（标准 §10.1）。

## 待办

- [ ] `serial_frame_codec.py`
- [ ] `check_interface_registry.py`（与 `ros2 topic list` 实测比对，需 ROS 2 环境）
- [ ] 把渲染类校验脚本化：docx 转 PDF 后检查内容是否越出下边距、
  拉丁标识符是否被换行截断成 1~3 字符的碎片（当前为人工目视 + 一次性脚本）
