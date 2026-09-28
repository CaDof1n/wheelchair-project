#!/usr/bin/env bash
# 在容器里构建并验证本仓库的 ROS 2 包（宿主机没有 ROS 2 时使用）。
#
# 用法：
#   tools/ros_container_build.sh                       # 默认构建 wheelchair_interfaces
#   tools/ros_container_build.sh wheelchair_base ...   # 指定包，可多个
#
# 环境变量：
#   ROS_IMAGE   容器镜像，默认 docker.io/library/ros:humble-ros-base
#   ROS_MIRROR  ROS 与 Ubuntu 的 apt 镜像主机，默认 mirrors.tuna.tsinghua.edu.cn
#   ROS_APT     1（默认）在容器内换源并装构建依赖；镜像依赖已齐时可设 0 提速
#
# 隔离方式与 docs/interfaces/自检清单.md「非 Ubuntu 环境」一节一致：
#   wheelchair_ws/src 只读挂载，容器内拷到 /tmp/ws 构建，
#   build/ install/ log/ 一律不落回仓库。
#
# 容器内脚本只能用 `set -eo pipefail`，**不能加 -u**：
#   `source install/setup.bash` 会引用未定义变量（如 COLCON_TRACE），
#   nounset 下会直接报 unbound variable，看着像构建失败。
set -eo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$REPO_ROOT/wheelchair_ws/src"
ROS_IMAGE="${ROS_IMAGE:-docker.io/library/ros:humble-ros-base}"
ROS_MIRROR="${ROS_MIRROR:-mirrors.tuna.tsinghua.edu.cn}"
ROS_APT="${ROS_APT:-1}"

if [ ! -d "$SRC_DIR" ]; then
  echo "找不到源码目录：$SRC_DIR" >&2
  exit 1
fi

RUNTIME="$(command -v podman || command -v docker || true)"
if [ -z "$RUNTIME" ]; then
  echo "没找到 podman 或 docker。Arch 系：sudo pacman -S podman（rootless，无需守护进程）" >&2
  exit 1
fi

PACKAGES=("$@")
if [ "${#PACKAGES[@]}" -eq 0 ]; then
  PACKAGES=(wheelchair_interfaces)
fi

echo "运行时     : $RUNTIME"
echo "镜像       : $ROS_IMAGE"
echo "源码(只读) : $SRC_DIR"
echo "目标包     : ${PACKAGES[*]}"
echo "apt 镜像   : $ROS_MIRROR"
echo

"$RUNTIME" run --rm -i \
  -v "$SRC_DIR":/src:ro \
  -e ROS_MIRROR="$ROS_MIRROR" \
  -e ROS_APT="$ROS_APT" \
  "$ROS_IMAGE" bash -s -- "${PACKAGES[@]}" <<'INNER'
set -eo pipefail

. /etc/os-release
echo "容器发行版 : $PRETTY_NAME"
echo "ROS_DISTRO : $ROS_DISTRO"
echo

SELECT_ARGS=()
for pkg in "$@"; do
  SELECT_ARGS+=(--packages-select "$pkg")
done

if [ "$ROS_APT" = "1" ]; then
  echo "=== 1. 换源（ROS 源 + Ubuntu 源）==="
  ROS_SRC=/usr/share/ros-apt-source/ros2.sources
  [ -f "$ROS_SRC" ] || ROS_SRC=/etc/apt/sources.list.d/ros2.list
  if [ ! -f "$ROS_SRC" ]; then
    echo "找不到 ROS apt 源文件，无法换源" >&2
    exit 1
  fi
  echo "ROS 源文件 : $ROS_SRC"
  # 该镜像用 deb822 格式。清华不提供源码包索引，deb-src 会 404，故收成 deb。
  sed -i "s|^Types: deb deb-src|Types: deb|" "$ROS_SRC" 2>/dev/null || true
  sed -i "s|packages.ros.org/ros2/ubuntu|$ROS_MIRROR/ros2/ubuntu|g" "$ROS_SRC"
  sed -i "s|http://archive.ubuntu.com/ubuntu|https://$ROS_MIRROR/ubuntu|g; \
          s|http://security.ubuntu.com/ubuntu|https://$ROS_MIRROR/ubuntu|g" /etc/apt/sources.list
  grep -E "^URIs" "$ROS_SRC" || true

  echo "=== 2. apt-get update 与构建依赖 ==="
  apt-get update 2>&1 | tail -3
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-colcon-common-extensions ros-humble-ament-lint-auto ros-humble-ament-lint-common \
    2>&1 | tail -3
else
  echo "=== 1-2. 按 ROS_APT=0 跳过换源与装依赖 ==="
fi

echo "=== 3. 构建 ==="
cp -r /src /tmp/ws
cd /tmp/ws
colcon build --symlink-install "${SELECT_ARGS[@]}" 2>&1 | tail -12

echo
echo "=== 4. 接口清点（仅接口包适用）==="
source install/setup.bash
for pkg in "$@"; do
  if ros2 interface package "$pkg" >/tmp/ifaces.txt 2>/dev/null; then
    echo "$pkg 接口条数：$(wc -l < /tmp/ifaces.txt)"
    cat /tmp/ifaces.txt
  else
    echo "$pkg：非接口包或未安装，跳过清点"
  fi
done

echo
echo "=== 5. colcon test ==="
TEST_RC=0
colcon test "${SELECT_ARGS[@]}" >/tmp/colcon-test.log 2>&1 || TEST_RC=1
tail -6 /tmp/colcon-test.log
colcon test-result --verbose >/tmp/colcon-test-result.log 2>&1 || true
tail -25 /tmp/colcon-test-result.log
if [ "$TEST_RC" -ne 0 ]; then
  echo "构建通过，但存在测试失败（详见上方 test-result）" >&2
  exit 1
fi

echo "ALL_DONE"
INNER
