# tools

**所有者：第六大组 · 架构与接口规范单元**

接口相关的辅助脚本与工具。

## 规划内容

| 工具 | 用途 |
|---|---|
| `serial_frame_codec.py` | 串口帧编解码（SOF / CRC16-MODBUS / SEQ），供 IF-05、IF-06 复用 |
| `gen_serial_example.py` | 生成标准 §6.7 的示例帧，验证 `AA 55 01 10 ... 22 81` |
| `check_interface_registry.py` | 校验 `docs/interfaces/interface_registry.yaml` 与实际 `ros2 topic list` 的差异 |
| `fault_bits_decode.py` | 把 `uint32 fault_bits` 解码为可读名称（标准 fault_bits 位定义） |
| `tf_tree_check.py` | 检查 TF 单树连通与重复发布（IF-04） |

## 约定

- 所有工具**必须**从 `docs/interfaces/interface_registry.yaml` 读取定义，
  **不得**硬编码 Topic 名、MSG_ID、错误码或 fault_bits 位含义。
- 脚本输出使用 UTF-8。
- **不得**在工具中写入 API 密钥、密码或校园内网地址（标准 §10.1）。

## 待办

- [ ] `serial_frame_codec.py`
- [ ] `check_interface_registry.py`
- [ ] 把 `build_interface_standard.py`（当前在 `tmp/`）中的表格校验逻辑迁入本目录
