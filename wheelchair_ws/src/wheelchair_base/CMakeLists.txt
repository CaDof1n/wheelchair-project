cmake_minimum_required(VERSION 3.8)
project(wheelchair_base)

# 骨架包：第六大组 · 架构与接口规范单元按标准 §8.1 代建，暂无节点。
# 所有者组接手后在此添加可执行目标与 install 规则；
# 公开接口以 README.md 与 docs/interfaces/interface_registry.yaml 为准，
# 增改须先走 ICR（标准 §8.4）。
# 若本包改用 Python（ament_python）：删除本文件，改用 setup.py、setup.cfg
# 与 resource/<包名>，并把 package.xml 的 build_type 改为 ament_python。

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
  set(CMAKE_CXX_STANDARD_REQUIRED ON)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
