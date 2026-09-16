cmake_minimum_required(VERSION 3.8)
project(wheelchair_interfaces)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
  set(CMAKE_CXX_STANDARD_REQUIRED ON)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# ---------------------------------------------------------------
# 接口清单 —— 与标准附录 A 一一对应
# 新增/修改接口前必须先发起 ICR（标准 §8.4），并同步更新
# docs/interfaces/interface_registry.yaml
# ---------------------------------------------------------------

set(msg_files
  "msg/SafetyStatus.msg"    # A.1  /wheelchair/safety/status
  "msg/McuState.msg"        # A.2  /wheelchair/base/mcu_state
  "msg/RangeArray.msg"      # A.3  /wheelchair/ultrasonic/ranges
  "msg/VoiceIntent.msg"     # A.4  /wheelchair/voice/intent
  "msg/StandState.msg"      # A.5  /wheelchair/stand/state
  "msg/SystemMode.msg"      # A.6  /wheelchair/system/mode
)

set(action_files
  "action/GraspObject.action"     # A.7  /wheelchair/arm/grasp_object
  "action/ChangePosture.action"   # A.8  /wheelchair/stand/change_posture
)

# Service 全部复用 std_srvs，无需自定义（标准表 10）：
#   /wheelchair/safety/set_soft_estop   std_srvs/srv/SetBool
#   /wheelchair/system/reset_fault      std_srvs/srv/Trigger
#   /wheelchair/system/health_check     std_srvs/srv/Trigger
#   /navigate_to_pose                   nav2_msgs/action/NavigateToPose

rosidl_generate_interfaces(${PROJECT_NAME}
  ${msg_files}
  ${action_files}
  DEPENDENCIES std_msgs geometry_msgs
)

ament_export_dependencies(rosidl_default_runtime)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
