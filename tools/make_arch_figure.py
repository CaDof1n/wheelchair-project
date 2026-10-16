# -*- coding: utf-8 -*-
"""
IW-IF-STD-001 图 1 · 整机通信架构框图 生成脚本
第六大组 · 架构与接口规范单元

用法（在仓库根目录执行）：
    python tools/make_arch_figure.py            # 覆盖 docs/interfaces/ 下的图
    python tools/make_arch_figure.py <目录>     # 输出到别处，用于比对
输出：
    整机通信架构框图.png（300 dpi，标准正文嵌入）与 .svg（矢量版）

依赖 matplotlib，以及 Microsoft YaHei 或 SimHei 字体（Windows 自带；
其他系统缺字体时中文会显示为方框）。改图后须重跑 tools/gen_iw_if_std_001.py，
使标准正文嵌入的图同步更新。
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from pathlib import Path

matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

# ---------------- 配色 ----------------
C_HMI  = "#5B7DB1"
C_HL   = "#2F4F7F"
C_DEC  = "#DCE6F2"
C_ARB  = "#FCE4D6"
C_SAFE = "#F2C6C9"
C_OUT  = "#D6E4D6"
C_PER  = "#E6DFF0"
C_MCU  = "#F2DCDB"
C_PWR  = "#FFF2CC"
C_STOP = "#C00000"
EDGE   = "#333333"

fig, ax = plt.subplots(figsize=(17.0, 10.4))
ax.set_xlim(0, 170); ax.set_ylim(0, 112)
ax.axis("off")

# ---------------- 辅助 ----------------
def zone(x, y, w, h, label, fc, ec, lw=1.6, r=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=1))
    ax.text(x + 1.4, y + h - 1.6, label, fontsize=9.6, color=ec,
            weight="bold", va="top", ha="left", zorder=3)

def box(x, y, w, h, title, lines=(), fc="#FFFFFF", ec=EDGE, fs=8.0,
        tfs=9.4, r=0.9, lw=1.2, tcolor=None, lh=2.15):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=4))
    tc = tcolor or "#1A1A1A"
    ty = y + h - 1.5 if lines else y + h / 2
    ax.text(x + w / 2, ty, title, fontsize=tfs, weight="bold", ha="center",
            va="top" if lines else "center", color=tc, zorder=5)
    for i, ln in enumerate(lines):
        ax.text(x + w / 2, ty - 2.5 - i * lh, ln, fontsize=fs, ha="center",
                va="top", color="#333333", zorder=5)

def arrow(p0, p1, color=EDGE, lw=1.5, ls="-", rad=0.0, ms=11, z=6):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", color=color, lw=lw,
        linestyle=ls, mutation_scale=ms, zorder=z,
        connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))

def path(pts, color=EDGE, lw=1.5, ls="-", ms=11, z=6):
    """折线：前 n-1 段为普通线，最后一段带箭头"""
    for i in range(len(pts) - 2):
        ax.plot([pts[i][0], pts[i+1][0]], [pts[i][1], pts[i+1][1]],
                color=color, lw=lw, ls=ls, zorder=z,
                solid_capstyle="round")
    arrow(pts[-2], pts[-1], color=color, lw=lw, ls=ls, ms=ms, z=z)

# =====================================================================
# 标题
# =====================================================================
ax.text(85, 108.4, "图 1　整机通信架构框图", fontsize=16, weight="bold",
        ha="center", va="center")
ax.text(85, 104.8, "IW-IF-STD-001 《第一版全局软硬件接口标准》V1.0.1　|　"
                   "第六大组 · 架构与接口规范单元　|　第四周",
        fontsize=9.6, ha="center", va="center", color="#555555")

# =====================================================================
# 人机交互域
# =====================================================================
zone(34, 92, 90, 10, "人机交互域", C_HMI, C_HMI)
box(36, 92.5, 25.5, 7.0, "语音交互（CAREMOVE）",
    ["离线识别 · 5 麦阵列 · <100 ms", "/wheelchair/voice/intent"],
    fc="#FFFFFF", ec=C_HMI)
box(67, 92.5, 25.5, 7.0, "2.4G 无线手柄",
    ["PS2 协议 · 双摇杆 (v, ω)", "/wheelchair/cmd_vel/teleop"],
    fc="#FFFFFF", ec=C_HMI)
box(98, 92.5, 25.5, 7.0, "机械臂遥操作 / 仿真调试",
    ["RViz2 · Gazebo 数字孪生", "/arm_controller/*"],
    fc="#FFFFFF", ec=C_HMI)

# =====================================================================
# 上位机域
# =====================================================================
zone(34, 40, 90, 49, "上位机域　·　香橙派 5（8 GB, RK3588S）　·　"
                     "Ubuntu 22.04 + ROS 2 Humble", "#F4F7FC", C_HL, lw=2.0)

# --- 决策层 ---
box(44, 74, 24, 9, "语音意图节点",
    ["VoiceIntent.msg", "附录 C 意图枚举（11 项）"], fc=C_DEC, ec=C_HL)
box(71.75, 74, 24, 9, "Nav2 导航栈",
    ["/wheelchair/cmd_vel/nav", "自动导航与 SLAM 算法组"], fc=C_DEC, ec=C_HL,
    tfs=8.6, fs=7.2)
box(99.5, 74, 24, 9, "MoveIt 2 运动规划",
    ["follow_joint_trajectory", "机械臂视觉与抓取控制组"], fc=C_DEC, ec=C_HL)

# --- 仲裁层 行一 ---
box(44, 62.5, 24, 7.5, "状态机 /wheelchair/state",
    ["坐姿 · 站立 · 导航 · 抓取"], fc=C_ARB, ec="#C55A11", tfs=8.6)
box(71.75, 62.5, 24, 7.5, "safety_supervisor 安全监督",
    ["/wheelchair/safety/status", "急停锁存 · 故障聚合"],
    fc=C_SAFE, ec=C_STOP, tcolor="#7A1F1F", tfs=8.8)

# --- 仲裁层 行二 ---
box(44, 52, 26, 9, "speed_mux 速度复用器",
    ["优先级仲裁", "→ /wheelchair/cmd_vel_raw"], fc=C_ARB, ec="#C55A11")
box(76, 52, 29, 9, "safety_filter 安全过滤器",
    ["限速 · 倾角 · 超声急停", "→ /wheelchair/cmd_vel"],
    fc=C_SAFE, ec=C_STOP, tcolor="#7A1F1F")

# --- 桥接层 ---
box(44, 41.5, 24, 7, "/cmd_vel",
    ["唯一合法速度出口 · ≤ 0.20 m/s"], fc=C_OUT, ec="#548235", tfs=9.6)
box(71.75, 41.5, 24, 7, "serial_bridge 串口桥",
    ["ROS 2 与第 6 章串口帧互转"], fc=C_OUT, ec="#548235", tfs=9.6)
box(99.5, 41.5, 24, 7, "/arm_controller 机械臂驱动",
    ["FollowJointTrajectory 服务端"], fc=C_OUT, ec="#548235", tfs=8.8)

# --- 上位机域内部连线 ---
arrow((56, 92.5), (56, 83), color=C_HMI, lw=1.3)
arrow((83.75, 92.5), (83.75, 83), color=C_HMI, lw=1.3)
arrow((111.5, 92.5), (111.5, 83), color=C_HMI, lw=1.3)

arrow((56, 74), (56, 70), color=C_HL, lw=1.3)                 # 语音 → 状态机
arrow((56, 62.5), (56, 61), color=C_HL, lw=1.3)               # 状态机 → mux
path([(83.75, 74), (83.75, 71.4), (69.5, 71.4), (69.5, 61)],
     color=C_HL, lw=1.3)                                       # Nav2 → mux
arrow((70, 56.5), (76, 56.5), color=C_STOP, lw=1.6)           # mux → filter
ax.text(73, 58.2, "仲裁", fontsize=7.4, color=C_STOP, ha="center")
arrow((83.75, 62.5), (83.75, 61), color=C_STOP, lw=1.6, ls=(0, (4, 2)))
ax.text(97.5, 62.0, "门控", fontsize=7.4, color=C_STOP, ha="left",
        va="center")
path([(90.5, 52), (90.5, 50.3), (56, 50.3), (56, 48.5)],
     color=C_STOP, lw=1.6)                                     # filter → cmd_vel
arrow((68, 45), (71.75, 45), color="#548235", lw=1.5)          # cmd_vel → bridge
arrow((111.5, 74), (111.5, 48.5), color=C_HL, lw=1.4)          # MoveIt2 → arm_driver

# 物理急停 → safety_supervisor（带跨线断口）
path([(130.5, 73), (114, 73)], color=C_STOP, lw=1.8, ls=(0, (5, 2)))
path([(109, 73), (90, 73), (90, 70)], color=C_STOP, lw=1.8, ls=(0, (5, 2)))
ax.text(120, 74.3, "硬件急停链", fontsize=7.4, color=C_STOP, ha="center")

# =====================================================================
# 感知域
# =====================================================================
zone(2, 40, 28, 49, "感知域", C_PER, "#7030A0")
box(3.5, 74, 25, 9, "RPLIDAR A2 / A3",
    ["→ /scan　10 Hz", "frame: laser_frame"], fc="#FFFFFF", ec="#7030A0")
box(3.5, 62.5, 25, 9, "深度相机",
    ["→ /camera/*", "frame: camera_link"], fc="#FFFFFF", ec="#7030A0")
box(3.5, 51, 25, 9, "IMU（BMI088）",
    ["→ /wheelchair/imu/data", "0xA1 帧 · SPI 读取"], fc="#FFFFFF",
    ec="#7030A0")
box(3.5, 40, 25, 9, "超声波阵列（HC-SR04）",
    ["→ /wheelchair/ultrasonic/ranges", "50 Hz　★ T3 命名待定"],
    fc="#FFFFFF", ec="#7030A0", fs=7.4)

# 感知话题总线
ax.plot([37, 37], [44.5, 84.9], color="#7030A0", lw=2.0, zorder=6)
ax.plot([37, 83.75], [84.9, 84.9], color="#7030A0", lw=2.0, zorder=6)
arrow((83.75, 84.9), (83.75, 83), color="#7030A0", lw=2.0, ms=12)
for yc in (78.5, 67, 55.5, 44.5):
    arrow((28.5, yc), (37, yc), color="#7030A0", lw=1.4, ms=10)
ax.text(41.3, 62, "ROS 2 感知话题", fontsize=7.4, color="#7030A0",
        rotation=90, ha="center", va="center", weight="bold")

# =====================================================================
# 下位机域
# =====================================================================
zone(34, 20, 90, 17, "下位机域", C_MCU, "#943634")
box(36, 22, 24, 8, "ESP32-WROOM-32",
    ["通信网关 · 协议打包 50 Hz"], fc="#FFFFFF", ec="#943634", tfs=8.6)
box(66, 22, 23, 8, "STM32F407VET6",
    ["运动主控 · 4 路 PID 1 kHz"], fc="#FFFFFF", ec="#943634", tfs=8.6)
box(90, 22, 17.5, 8, "执行器驱动",
    ["轮毂电机 4 路 待定", "推杆 IBT-2/BTS7960"], fc="#FFFFFF", ec="#943634",
    tfs=7.8, fs=6.1, lh=2.0)
box(109.5, 22, 14.5, 8, "执行器",
    ["轮毂电机 × 4", "电动推杆"], fc="#FFFFFF", ec="#943634", tfs=8.4,
    fs=6.4, lh=2.0)

arrow((60, 26), (66, 26), color="#943634", lw=1.4)
ax.text(63, 28.4, "UART", fontsize=6.8, color="#943634", ha="center")
ax.text(63, 26.3, "CRC8", fontsize=6.8, color="#943634", ha="center")
ax.text(63, 23.5, "20 ms", fontsize=6.8, color="#943634", ha="center")
ax.text(63, 21.4, "底盘组内部", fontsize=6.4, color="#943634", ha="center")
arrow((89, 26), (90, 26), color="#943634", lw=1.4)
arrow((107.5, 26), (109.5, 26), color="#943634", lw=1.4)

# 唯一跨组串口接口
path([(83.75, 41.5), (83.75, 38.5), (48, 38.5), (48, 30)], color=C_STOP,
     lw=2.6, ms=13, z=7)
ax.text(82, 32.8,
        "唯一跨组串口接口　·　第 6 章　SOF AA 55 + CRC-16/MODBUS　·　"
        "200 ms 看门狗",
        fontsize=8.4, color=C_STOP, weight="bold", ha="center", va="center")

# 电源域供电指示
arrow((130.5, 50), (125.5, 50), color="#B8860B", lw=1.4, ls=(0, (4, 2)))
ax.text(127.4, 51.6, "5 V", fontsize=7.0, color="#B8860B", ha="center")
arrow((130.5, 35), (125.5, 35), color="#B8860B", lw=1.4, ls=(0, (4, 2)))
ax.text(127.4, 36.4, "5 V", fontsize=7.0, color="#B8860B", ha="center")

# =====================================================================
# 电源域
# =====================================================================
zone(128, 12, 38, 87, "电源域", C_PWR, "#B8860B", lw=1.8)
box(130.5, 86, 33, 10, "锂电池组",
    ["8S 磷酸铁锂 · 24 V 级", "标称 25.6 V / 满充 29.2 V", "T1 已合流（V1.0.1）"],
    fc="#FFF9E6", ec="#B8860B", fs=7.6, tfs=9.2)
box(130.5, 78, 33, 6, "主保险 / 断路器", [], fc="#FFFFFF", ec="#B8860B",
    tfs=8.8)
box(130.5, 69.5, 33, 6.5, "物理急停（22 mm 红色自锁）", [], fc="#FDE9E9",
    ec=C_STOP, tfs=8.4, tcolor=C_STOP)
box(130.5, 61.5, 33, 6, "接触器 24 V / 100 A", [], fc="#FFFFFF",
    ec="#B8860B", tfs=8.8)
box(130.5, 44, 33, 14, "隔离 DC-DC",
    ["输入 9 ~ 36 V", "12 V / 2.5 A → 传感器", "5 V / 6 A → 香橙派 5",
     "5 V → ESP32 / 逻辑"],
    fc="#FFF9E6", ec="#B8860B", fs=7.0, tfs=9.2)
box(130.5, 33, 33, 8.5, "BMS 8S / 100 A",
    ["电压 · 电流 · 温度", "→ 0xA2 帧（ICR-001 代拟）"],
    fc="#FFFFFF", ec="#B8860B", fs=7.4, tfs=9.2)
box(130.5, 21, 33, 9, "★ 安全原则",
    ["急停不依赖任何软件", "断电即停车"], fc="#FDE9E9", ec=C_STOP,
    fs=7.8, tfs=9.2, tcolor=C_STOP)

for y0, y1, c in [(86, 84, "#B8860B"), (78, 76, "#B8860B"),
                  (69.5, 67.5, C_STOP), (61.5, 58, "#B8860B")]:
    arrow((147, y0), (147, y1), color=c, lw=1.6)

# =====================================================================
# 图例
# =====================================================================
lg = [(C_DEC, "决策层"), (C_ARB, "仲裁层"), (C_SAFE, "安全层"),
      (C_OUT, "输出 / 桥接层"), (C_PER, "感知域"), (C_MCU, "下位机域"),
      (C_PWR, "电源域")]
lx = 4.0
for fc, lb in lg:
    ax.add_patch(Rectangle((lx, 9.0), 2.6, 2.2, fc=fc, ec=EDGE, lw=0.8,
                           zorder=4))
    ax.text(lx + 3.4, 10.1, lb, fontsize=8.4, va="center", color="#333333")
    lx += 3.4 + len(lb) * 1.75 + 1.6

ax.text(4.0, 5.6,
        "红色实/虚线 = 安全链路（物理急停、速度门控）　|　"
        "紫色 = 感知话题　|　金色虚线 = 供电",
        fontsize=8.2, color="#555555", va="center")
ax.text(166, 5.6,
        "★ 为 TBD（待实测）项，详见《跨组汇报接口对齐差异清单》T2–T4",
        fontsize=8.2, color="#B8860B", ha="right", va="center")

_out = (Path(sys.argv[1]) if len(sys.argv) > 1 else
        Path(__file__).resolve().parents[1] / "docs" / "interfaces")
_out.mkdir(parents=True, exist_ok=True)
fig.savefig(_out / "整机通信架构框图.png", dpi=300,
            bbox_inches="tight", facecolor="white")
fig.savefig(_out / "整机通信架构框图.svg",
            bbox_inches="tight", facecolor="white")
print("saved ->", _out)
