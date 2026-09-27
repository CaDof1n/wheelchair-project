# -*- coding: utf-8 -*-
"""
IW-IF-STD-001 《第一版全局软硬件接口标准》V1.0 生成脚本
第六大组 · 架构与接口规范单元

用法（在仓库根目录执行）：
    python tools/gen_iw_if_std_001.py
输出：
    docs/interfaces/第一版全局软硬件接口标准_V1.0.docx

改动正文后须同时更新 docs/interfaces/interface_registry.yaml（标准 §8.3），
并跑一遍 tools/check_iw_if_std_001.py 校验题注、引用与排版。
"""
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Inches

OUT = (Path(__file__).resolve().parents[1] /
       "docs" / "interfaces" / "第一版全局软硬件接口标准_V1.0.docx")

BLACK = "000000"; NAVY = "17365D"; MID_BLUE = "2F5597"
PALE_GRAY = "F5F7FA"; LIGHT_GRAY = "D9D9D9"; WHITE = "FFFFFF"

# ---------------------------------------------------------------- helpers
def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd"); tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=90, start=100, bottom=90, end=100):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar"); tc_pr.append(tc_mar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}"); tc_mar.append(node)
        node.set(qn("w:w"), str(v)); node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader"); el.set(qn("w:val"), "true"); tr_pr.append(el)


def set_table_borders(table, color=LIGHT_GRAY, size="6"):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders"); tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = borders.find(qn(f"w:{edge}"))
        if el is None:
            el = OxmlElement(f"w:{edge}"); borders.append(el)
        el.set(qn("w:val"), "single"); el.set(qn("w:sz"), size)
        el.set(qn("w:space"), "0"); el.set(qn("w:color"), color)


def set_cell_width(cell, width_cm):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW"); tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(int(Cm(width_cm).emu / 635)))
    tc_w.set(qn("w:type"), "dxa")


def font_run(run, name="Microsoft YaHei", size=10.5, bold=False, color=BLACK):
    run.font.name = name
    rfonts = run._element.get_or_add_rPr().rFonts
    rfonts.set(qn("w:ascii"), name); rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:cs"), name); rfonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size); run.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)
    return run


def set_word_wrap(p, char_level=True):
    pPr = p._p.get_or_add_pPr()
    tag = qn("w:wordWrap")
    node = pPr.find(tag)
    if node is None:
        node = OxmlElement("w:wordWrap")
        anchor = None
        for t in ("w:spacing", "w:ind", "w:jc", "w:rPr", "w:sectPr"):
            found = pPr.find(qn(t))
            if found is not None:
                anchor = found; break
        if anchor is not None:
            anchor.addprevious(node)
        else:
            pPr.append(node)
    node.set(qn("w:val"), "0" if char_level else "1")


def set_paragraph_format(p, *, before=0, after=5, line=1.25, keep_next=False):
    pf = p.paragraph_format
    pf.space_before = Pt(before); pf.space_after = Pt(after)
    pf.line_spacing = line; pf.keep_with_next = keep_next


def add_text(doc, text="", *, bold_lead=None, align=None, before=0, after=5,
             indent=0, size=10.5, color=BLACK):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.left_indent = Cm(indent)
    set_paragraph_format(p, before=before, after=after)
    if bold_lead and text.startswith(bold_lead):
        font_run(p.add_run(bold_lead), bold=True, size=size, color=color)
        font_run(p.add_run(text[len(bold_lead):]), size=size, color=color)
    else:
        font_run(p.add_run(text), size=size, color=color)
    return p


def add_bullet(doc, text, level=0, bold_lead=None):
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    p.paragraph_format.left_indent = Cm(0.74 + level * 0.55)
    p.paragraph_format.first_line_indent = Cm(-0.25)
    set_paragraph_format(p, after=3, line=1.18)
    if bold_lead and text.startswith(bold_lead):
        font_run(p.add_run(bold_lead), bold=True)
        font_run(p.add_run(text[len(bold_lead):]))
    else:
        font_run(p.add_run(text))
    return p


NUMBER_COUNTER = 0


def add_numbered(doc, text):
    global NUMBER_COUNTER
    NUMBER_COUNTER += 1
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.82)
    p.paragraph_format.first_line_indent = Cm(-0.3)
    set_paragraph_format(p, after=3, line=1.18)
    font_run(p.add_run(f"{NUMBER_COUNTER}. "), bold=True)
    font_run(p.add_run(text))
    return p


def add_code(doc, lines, size=8.5):
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.65)
        p.paragraph_format.right_indent = Cm(0.25)
        set_paragraph_format(p, after=0, line=1.0)
        font_run(p.add_run(line), name="Consolas", size=size, color="202020")
    sp = doc.add_paragraph(); set_paragraph_format(sp, after=2)


def add_heading(doc, text, level=1):
    global NUMBER_COUNTER
    NUMBER_COUNTER = 0
    p = doc.add_paragraph(style=f"Heading {level}")
    set_paragraph_format(p, before=9 if level == 1 else 6, after=4,
                         line=1.08, keep_next=True)
    font_run(p.add_run(text), size={1: 16, 2: 13, 3: 11}.get(level, 10.5),
             bold=True)
    return p


def remove_paragraph_border(paragraph):
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = p_pr.find(qn("w:pBdr"))
    if p_bdr is not None:
        p_pr.remove(p_bdr)


def add_table(doc, headers, rows, widths, font_size=8.4, first_col_bold=False,
              whole_word_wrap=True, mark_rows=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    for i, text in enumerate(headers):
        cell = hdr.cells[i]
        set_cell_width(cell, widths[i]); set_cell_shading(cell, NAVY)
        set_cell_margins(cell, top=105, bottom=105)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_paragraph_format(p, after=0, line=1.05, keep_next=True)
        if whole_word_wrap:
            set_word_wrap(p, char_level=False)
        font_run(p.add_run(str(text)), size=font_size, bold=True, color=WHITE)
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cell = cells[i]
            set_cell_width(cell, widths[i]); set_cell_margins(cell)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if ridx % 2 == 1:
                set_cell_shading(cell, PALE_GRAY)
            p = cell.paragraphs[0]
            p.alignment = (WD_ALIGN_PARAGRAPH.CENTER
                           if i == 0 and widths[i] <= 2.5
                           else WD_ALIGN_PARAGRAPH.LEFT)
            set_paragraph_format(p, after=0, line=1.08)
            if whole_word_wrap:
                set_word_wrap(p, char_level=False)
            font_run(p.add_run(str(value)), size=font_size,
                     bold=(first_col_bold and i == 0))
    after = doc.add_paragraph(); set_paragraph_format(after, after=3)
    return table


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_paragraph_format(p, before=4, after=3, keep_next=True)
    font_run(p.add_run(text), size=9, bold=True)
    return p


def add_note(doc, text, kind="warn"):
    """表下注释块：warn 用于裁决/待确认提示，plain 用于普通注。"""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.3)
    set_paragraph_format(p, before=2, after=6, line=1.15)
    font_run(p.add_run(("注：" if kind == "plain" else "待确认：")),
             size=8.8, bold=True, color="8A4B00" if kind == "warn" else "444444")
    font_run(p.add_run(text), size=8.8,
             color="8A4B00" if kind == "warn" else "444444")
    return p


def add_figure(doc, path, width_cm, caption):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_format(p, before=4, after=3)
    p.add_run().add_picture(str(path), width=Cm(width_cm))
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_format(c, after=8)
    font_run(c.add_run(caption), size=9, bold=True, color="444444")


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run()
    font_run(run, size=8.5, color="666666")
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve")
    it.text = " PAGE "
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "end")
    run._r.append(f1); run._r.append(it); run._r.append(f2)


def crc16_modbus(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


# ------------------------------------------------------------- doc scaffold
doc = Document()
section = doc.sections[0]
section.top_margin = Cm(1.8); section.bottom_margin = Cm(1.7)
section.left_margin = Cm(1.9); section.right_margin = Cm(1.9)
section.header_distance = Cm(0.7); section.footer_distance = Cm(0.7)
section.different_first_page_header_footer = True

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Microsoft YaHei"
normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
normal._element.rPr.rFonts.set(qn("w:cs"), "Microsoft YaHei")
normal.font.size = Pt(10.5)
normal.font.color.rgb = RGBColor(0, 0, 0)
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.25

ts = styles["Title"]
ts.font.name = "Microsoft YaHei"
ts._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
ts._element.rPr.rFonts.set(qn("w:cs"), "Microsoft YaHei")
ts.font.size = Pt(24); ts.font.bold = True
ts.font.color.rgb = RGBColor(0, 0, 0)
tp = ts._element.get_or_add_pPr()
tb = tp.find(qn("w:pBdr"))
if tb is not None:
    tp.remove(tb)

for level, size in ((1, 16), (2, 13), (3, 11)):
    st = styles[f"Heading {level}"]
    st.font.name = "Microsoft YaHei"
    st._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    st._element.rPr.rFonts.set(qn("w:cs"), "Microsoft YaHei")
    st.font.size = Pt(size); st.font.bold = True
    st.font.color.rgb = RGBColor(0, 0, 0)

dd = doc.styles.element.find(qn("w:docDefaults"))
if dd is not None:
    rpr_d = dd.find(qn("w:rPrDefault"))
    if rpr_d is not None:
        dr = rpr_d.find(qn("w:rPr"))
        if dr is None:
            dr = OxmlElement("w:rPr"); rpr_d.append(dr)
        rf = dr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts"); dr.insert(0, rf)
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            if rf.get(qn(a)) is not None:
                del rf.attrib[qn(a)]
        for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rf.set(qn(a), "Microsoft YaHei")

_hp = section.header.paragraphs[0]
_hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
set_paragraph_format(_hp, after=0)
font_run(_hp.add_run("智能辅助轮椅项目  全局接口标准  V1.0"), size=8.5,
         color="666666")
_ft = section.footer.add_table(rows=1, cols=2, width=Inches(6.6))
_ft.autofit = False
_ft.columns[0].width = Inches(5.2); _ft.columns[1].width = Inches(1.4)
_fp = _ft.cell(0, 0).paragraphs[0]; set_paragraph_format(_fp, after=0)
font_run(_fp.add_run("文档编号 IW-IF-STD-001    第六大组 · 架构与接口规范单元"),
         size=8.5, color="666666")
add_page_number(_ft.cell(0, 1).paragraphs[0])

# ---------------------------------------------------------------- 封面
doc.add_paragraph(); doc.add_paragraph()
p = doc.add_paragraph(style="Title"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_paragraph_format(p, before=30, after=18, line=1.0)
font_run(p.add_run("多功能智能辅助轮椅项目"), size=24, bold=True)
remove_paragraph_border(p)
p2 = doc.add_paragraph(style="Title"); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_paragraph_format(p2, after=12, line=1.0)
font_run(p2.add_run("第一版全局软硬件接口标准"), size=24, bold=True)
remove_paragraph_border(p2)

sub = doc.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_paragraph_format(sub, after=34)
font_run(sub.add_run("ROS 2  TF 坐标系  串口通信  网络与版本管理"),
         size=13, bold=True, color=MID_BLUE)

add_table(doc, ["项目", "内容"], [
    ("文档编号", "IW-IF-STD-001"),
    ("版本", "V1.0"),
    ("状态", "正式发布稿"),
    ("编制单位", "第六大组 · 架构与接口规范单元"),
    ("适用项目", "基于数字孪生的多功能智能辅助轮椅研发与集成"),
    ("发布日期", "第四周"),
], [3.3, 11.7], font_size=10, first_col_bold=True)
add_caption(doc, "表 1-1  文档标识信息")

p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_paragraph_format(p, before=18, after=4)
font_run(p.add_run("本标准经各组接口负责人评审后生效"), size=10, bold=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_paragraph_format(p, after=0)
font_run(p.add_run("未经接口变更流程批准  各组不得自行改变名称  类型  单位或数据语义"),
         size=9.5, color="555555")

doc.add_page_break()

# ================================================================ 发布与使用说明
add_heading(doc, "发布与使用说明", 1)
add_text(doc, "本标准统一机械结构、电气动力与底层控制、自动导航与 SLAM、机械臂视觉与抓取、"
              "语音交互与多模态控制、系统集成测试与项目管理六大组之间的软件接口、坐标系、"
              "通信帧及协作规则。第一版用于数字孪生阶段的并行开发，并作为实物迁移的接口基线。"
              "各组应依照本文建立节点、消息和固件；任何影响其他组的接口改动，"
              "必须先提交接口变更申请并完成联调评审。")
add_text(doc, "本版为正式第一版。本单元此前在未与其他组沟通的前提下拟定的两稿内部草案"
              "（记为草案 V1.0 与草案 V1.1）已归档至 docs/interfaces/archive/，"
              "不再对外引用；全部跨组差异的裁决过程见《跨组汇报接口对齐差异清单》"
              "（IW-IF-STD-001-REV-002）。")

add_caption(doc, "表 1-2  文档审批信息")
add_table(doc, ["角色", "责任", "签名或负责人", "日期"], [
    ("编制", "起草接口标准并维护接口清单", "第六大组 · 架构与接口规范单元", "第四周"),
    ("复核", "验证 ROS 2、TF 与串口定义的可实现性", "各组接口负责人", "待填写"),
    ("批准", "确认版本生效并通知全项目组", "第六组组长", "待填写"),
], [1.8, 6.6, 4.4, 4.4], font_size=8.8)

add_caption(doc, "表 1-3  版本记录")
add_table(doc, ["版本", "日期", "变更内容", "编制"], [
    ("V1.0", "第四周",
     "正式第一版。以五组已完成的方案汇报为输入，对内部草案逐条对表后重出："
     "裁决 ROS 2 发行版、SLAM 框架、坐标系命名、上位机平台、串口链路拓扑、"
     "心跳超时、超声波频率、速度上限层次、云端大模型措辞与接口责任所有者共 10 项跨组差异；"
     "新增机械臂控制器 Action、力矩话题、臂端相机接口、语音意图枚举、语音优先级与急停联动、"
     "WHEEL_STALL 故障位、TF 专用 QoS 档、环境交付方式、整机通信架构框图共 10 项接口缺口；"
     "代拟 9 条串口消息载荷表；表号体系按章节重编并补全题注。"
     "母线电压、超声波阵列命名、下位机通信路线、臂端相机型号与外参 4 项标记为 TBD。",
     "第六大组 · 架构与接口规范单元"),
], [1.6, 1.8, 10.6, 3.2], font_size=8.4)
add_note(doc, "内部草案 V1.0（2026-09-14）与草案 V1.1（2026-09-21）为未协调稿，"
              "自本版发布起作废，仅作过程记录保存在 docs/interfaces/archive/。"
              "本版版本号重新起算，与草案的序号无继承关系。", kind="plain")

add_heading(doc, "文档结构", 2)
for item in [
    "1 总则与适用范围", "2 系统边界与通信架构", "3 全局通用约定",
    "4 ROS 2 接口标准", "5 TF 坐标系标准", "6 上位机与下位机串口协议",
    "7 网络和时间同步标准", "8 Git 仓库与接口变更管理", "9 联调验收与问题处置",
    "10 AI 工具应用记录", "附录 A 自定义消息与动作定义", "附录 B 第一版交付检查表",
    "附录 C 语音意图枚举表", "附录 D 评审签署页",
]:
    add_bullet(doc, item)

add_heading(doc, "关键结论", 2)
for t in [
    "所有跨组软件能力必须通过本标准列出的 ROS 2 Topic、Service 或 Action 暴露，"
    "禁止通过读取其他组私有文件或进程内变量完成跨组耦合。",
    "真实底盘只接受安全过滤器输出的 /cmd_vel；任何导航、手柄或语音节点均不得直接连接电机驱动。",
    "map 到 odom、odom 到 base_footprint 和静态传感器坐标变换分别设置唯一发布方，禁止重复发布。",
    "串口失联、命令过期、CRC 错误和物理急停均按安全状态处理；软件急停不能代替物理急停。",
    "上位机与 ESP32 之间的串口帧是本项目唯一的跨组串口接口；"
    "ESP32 与 STM32 之间的板间链路属底盘组内部实现，不对外暴露。",
]:
    add_bullet(doc, t)

# ================================================================ 1 总则
add_heading(doc, "1 总则与适用范围", 1)

add_heading(doc, "1.1 编制目的", 2)
add_text(doc, "本标准用于减少六大组并行开发时的接口歧义，保证仿真环境与实物环境使用同一套命名、"
              "数据类型、单位和故障语义。接口稳定优先于局部实现便利；各组可自由设计内部节点，"
              "但公开接口必须保持兼容。")

add_heading(doc, "1.2 适用范围", 2)
for t in [
    "Ubuntu 与 ROS 2 Humble 上运行的上位机节点。",
    "ESP32 网关固件、STM32 运动主控固件，以及 ESP32 与上位机之间的串口通信。",
    "Gazebo 或 Isaac Sim 仿真、RViz 2 可视化、Nav2、MoveIt 2、语音识别和状态机调度。",
    "激光雷达、RGB-D 相机、IMU、超声波、电机、推杆、机械臂、力矩传感器和急停相关数据。",
    "代码仓库、接口文档、配置文件、测试脚本和接口变更过程。",
]:
    add_bullet(doc, t)

add_heading(doc, "1.3 编制依据", 2)
for t in [
    "《计算机网络课程综合实践大作业任务书》。",
    "ROS 2 通用通信机制以及 Nav2、MoveIt 2 的标准接口习惯。",
    "REP 103 坐标轴与 SI 单位约定、REP 105 移动平台坐标系约定。",
    "底盘运动控制、电气动力与底层控制、自动导航与 SLAM、机械臂视觉与抓取、"
    "语音交互与多模态控制五组的方案汇报（第四周）。",
    "项目安全红线：完成连续 50 次稳定空载运行及 50 至 70 kg 沙袋配重测试前，"
    "严禁人员乘坐进行通电或动态测试。",
]:
    add_bullet(doc, t)

add_heading(doc, "1.4 术语与约束词", 2)
add_caption(doc, "表 1-4  术语与约束词")
add_table(doc, ["术语", "说明"], [
    ("上位机", "运行 ROS 2 的计算平台。本项目的基线平台为香橙派 5（8 GB），见表 4-1"),
    ("下位机", "对上位机呈现为单一串口端点的网关设备（ESP32）。STM32 运动主控位于其下游，"
               "属底盘组内部实现，不经串口直接对上位机暴露接口"),
    ("板间链路", "ESP32 与 STM32 之间的 UART 链路。帧格式由底盘组自定，本标准仅约束其"
                 "必须把遥测透传为第 6 章规定的 MCU 到 HOST 帧"),
    ("公开接口", "被两个及以上大组使用的 Topic、Service、Action、TF 或串口字段"),
    ("必须", "强制要求；不满足时不得进入集成分支或整机联调"),
    ("应", "正常情况下执行；偏离时需在接口变更记录中说明原因"),
    ("可", "允许选择，不构成强制要求"),
    ("TBD", "待定标项。依赖硬件选型或实测数据的接口参数，标注责任组与解除条件，"
            "解除前不得进入实物联调"),
], [2.6, 14.6], font_size=8.6)

add_heading(doc, "1.5 接口责任原则", 2)
add_numbered(doc, "每个公开接口必须指定唯一所有者。所有者负责定义、实现、测试、版本兼容和故障说明。")
add_numbered(doc, "发布方保证数据类型、单位、坐标系、频率和时间戳正确；订阅方负责超时检测，"
                  "不得无限期使用旧数据。")
add_numbered(doc, "安全相关接口采用失效安全设计。通信中断或字段非法时，系统进入停止或保持状态。")
add_numbered(doc, "不得在 V1.x 中改变已有字段含义。新增可选字段或接口可提升次版本；"
                  "破坏兼容性的改动进入 V2.0。")
add_numbered(doc, "凡标准中标注 TBD 的条目，其接口名称、类型与帧结构先行冻结，"
                  "仅数值或外参待回填；回填不得迟于对应阶段的联调开始日。")

# ================================================================ 2 系统边界与通信架构
add_heading(doc, "2 系统边界与通信架构", 1)
add_text(doc, "系统由感知、运动执行、导航、机械臂、语音与任务调度、安全监督、仿真和工程管理"
              "八类能力组成。ROS 2 是上位机各能力之间的唯一实时集成总线；"
              "串口是上位机与下位机之间的基础控制通道。")
add_text(doc, "语音交互以离线识别为基线能力，不依赖网络即可完成全部识别与控制；"
              "若启用云端意图解析，仅限非安全关键用途，且必须可整体关闭"
              "（编译期或配置期），关闭后语音功能完整可用。语音原始数据默认不出本机。")

add_figure(doc, OUT.parent / "整机通信架构框图.png", 16.6,
           "图 1  整机通信架构框图（数据流、安全链与电源域的对应关系）")

add_caption(doc, "表 2-1  子系统与接口责任")
add_table(doc, ["子系统", "主要职责", "公开接口所有者", "禁止事项"], [
    ("机械结构与物理装配", "URDF、关节限位、传感器安装位姿", "本组接口负责人",
     "未经评审改变 link 或 joint 名称"),
    ("电气动力与底层控制", "电机、推杆、限位、电源与基础遥测", "本组接口负责人",
     "绕过急停或接收未过滤速度"),
    ("自动导航与 SLAM 算法", "SLAM、定位、路径规划与避障", "本组接口负责人",
     "直接写串口或控制电机 PWM"),
    ("机械臂视觉与抓取控制", "检测、目标定位、MoveIt 2 与抓取", "本组接口负责人",
     "自行定义重复 TF 根节点"),
    ("语音交互与多模态控制", "语音文本、意图和对话", "本组接口负责人",
     "直接执行安全关键动作"),
    ("系统集成测试与项目管理", "接口基线、安全门控（speed_mux 与 safety_filter）、测试与发布",
     "本组接口负责人", "未留记录直接修改他组接口"),
    ("系统集成测试与项目管理（安全监督）", "safety_supervisor、急停锁存、故障聚合",
     "系统集成测试与项目管理组", "以软件急停替代物理急停"),
    ("系统集成测试与项目管理（仿真）", "Gazebo 或 Isaac Sim 场景、/clock、节点启动顺序",
     "系统集成测试与项目管理组", "把仿真配置带入实物 launch"),
    ("系统集成测试与项目管理（工程管理）", "仓库、分支保护、ICR 流程、发布标签",
     "系统集成测试与项目管理组", "绕过 PR 门禁直接 push"),
], [3.2, 4.6, 3.4, 6.0], font_size=8.0)
add_note(doc, "本表末三行以及 speed_mux、safety_filter 的所有者归属为本单元裁决结论"
              "（ICR-002）。五组汇报中无一组认领这两个节点，其职责与"
              "「系统集成测试与项目管理」一行的描述最贴合，故暂归该组，"
              "需该组会签确认后生效。")

add_heading(doc, "2.1 数据流和控制边界", 2)
for t in [
    "语音或操作输入 -> 状态机 -> Nav2 / MoveIt 2 / 站立动作",
    "Nav2 / 手柄 / 任务控制 / 语音 -> 速度复用器 -> 安全过滤器 -> /cmd_vel",
    "/cmd_vel -> 串口桥接节点 -> ESP32 网关 -> STM32 -> 电机驱动与推杆",
    "传感器与 MCU 遥测 -> ROS 2 Topic / TF -> 导航、机械臂、监控与测试",
    "物理急停 -> 硬件断能或禁止驱动，同时由 MCU 上报 ROS 2 安全状态",
]:
    add_text(doc, t, indent=0.6)
add_text(doc, "物理急停链路必须独立于 ROS 2 和上位机。ROS 2 软件急停用于提前停止、联调"
              "和状态传播，不得作为唯一安全措施。")
add_text(doc, "上位机与下位机的链路为两级：上位机与 ESP32 之间使用第 6 章的串口帧，"
              "是本项目唯一的跨组串口接口；ESP32 与 STM32 之间为底盘组内部板间链路，"
              "使用 UART 二进制帧与 CRC8 校验、20 ms 心跳，本标准不约束其帧格式。"
              "但 ESP32 必须把 STM32 的遥测按第 6 章规定的 MCU 到 HOST 帧透传，"
              "并以 serial_bridge 作为 ROS 2 侧的唯一端点。")

add_heading(doc, "2.2 运行模式", 2)
add_caption(doc, "表 2-2  运行模式")
add_table(doc, ["模式", "值", "允许行为", "速度限制"], [
    ("INIT", "0", "节点启动、自检、禁止执行机构运动", "0"),
    ("SIMULATION", "1", "Gazebo 或 Isaac Sim 中执行全功能测试", "线速度不高于 0.8 m/s"),
    ("MANUAL", "2", "手柄或调试终端控制，安全过滤器生效", "实物初期不高于 0.20 m/s"),
    ("AUTONOMOUS", "3", "Nav2、机械臂和状态机按任务运行", "由批准配置限定"),
    ("STANDING", "4", "执行站立或坐下流程，底盘驱动锁止", "0"),
    ("FAULT", "5", "故障锁存，仅允许诊断和合规复位", "0"),
    ("ESTOP", "6", "急停锁存，执行机构禁止输出", "0"),
], [2.6, 1.4, 8.2, 5.0], font_size=8.4)

# ================================================================ 正文

# ---------------------------------------------------------------- p_a_ch34.py
# ================================================================ 3 全局通用约定
add_heading(doc, "3 全局通用约定", 1)

add_heading(doc, "3.1 命名规则", 2)
add_caption(doc, "表 3-1  命名规则")
add_table(doc, ["对象", "规则", "示例"], [
    ("ROS 包", "全小写 snake_case，以 wheelchair_ 开头", "wheelchair_base"),
    ("ROS 节点", "全小写 snake_case，名称体现单一职责", "serial_bridge"),
    ("Topic", "全小写，层级使用 /，动作或状态语义明确", "/wheelchair/safety/status"),
    ("Service", "动词含义明确，使用 set reset get reload",
     "/wheelchair/system/reset_fault"),
    ("Action", "以业务目标命名，反馈可持续更新", "/wheelchair/arm/grasp_object"),
    ("TF frame", "全小写 snake_case，不以 / 开头", "base_link"),
    ("URDF joint", "部件_位置_joint", "front_left_wheel_joint"),
    ("参数", "节点私有参数优先，snake_case", "command_timeout_ms"),
    ("固件常量", "大写 snake_case", "MAX_LINEAR_MM_S"),
], [2.6, 8.6, 6.0], font_size=8.6)

add_heading(doc, "3.2 单位 数值与时间", 2)
for t in [
    "ROS 2 消息统一使用 SI 单位：米、秒、弧度、米每秒、弧度每秒、伏特、安培和摄氏度。",
    "角度在 ROS 2 中使用弧度；界面可显示角度，但进入公开接口前必须转换。",
    "串口为减少浮点差异，使用带量纲整数，例如 mm、mrad、mV、mA 和 0.1 摄氏度；"
    "字段表必须写明缩放比例。",
    "ROS 2 数据必须填写 header.stamp。仿真时所有节点设置 use_sim_time=true，"
    "并订阅 /clock；实物时统一使用系统时钟。",
    "所有超时使用单调时钟计算，不受系统时间校准回拨影响。",
    "无效浮点数不得静默传播。NaN 仅可用于标准消息明确允许的未知量，并应同步报告诊断状态。"
    "本项目明确允许用 NaN 表示「距离未知」的字段为 RangeArray 的 ranges_m、min_range_m、"
    "max_range_m 与 SafetyStatus.min_obstacle_distance_m；串口侧的 0xFFFF 哨兵必须在 "
    "serial_bridge 中转换为 NaN，不得按 0.001 m/mm 直接缩放为 65.535 m。",
]:
    add_bullet(doc, t)

add_heading(doc, "3.3 坐标轴与符号", 2)
for t in [
    "采用右手坐标系：x 轴向前，y 轴向左，z 轴向上。",
    "绕 z 轴逆时针为正偏航；绕 x 轴为滚转；绕 y 轴为俯仰。",
    "图像坐标遵循相机驱动约定；进入三维目标接口前必须转换到 frame_id 指定的 ROS 坐标系。",
    "二维导航姿态使用 quaternion 表达，不得直接把角度数值写入 orientation.z。",
]:
    add_bullet(doc, t)

add_heading(doc, "3.4 配置与参数", 2)
add_numbered(doc, "可调参数存放在 config/*.yaml，不得把端口、速度上限、串口号、IP 地址"
                  "或坐标外参硬编码在业务代码中。")
add_numbered(doc, "仿真与实物配置分别使用 sim 和 real 后缀，通过 launch 参数选择，"
                  "接口名称保持一致。")
add_numbered(doc, "安全上限必须同时在上位机安全过滤器和下位机固件中限制，以更严格者为准。")
add_numbered(doc, "配置变更必须随代码提交，并在 PR 中说明测试环境和前后数值。")

# ================================================================ 4 ROS 2 接口标准
add_heading(doc, "4 ROS 2 接口标准", 1)

add_heading(doc, "4.1 环境基线", 2)
add_caption(doc, "表 4-1  环境基线")
add_table(doc, ["项目", "V1.0 约定"], [
    ("操作系统", "Ubuntu 22.04 LTS"),
    ("ROS 2",
     "Humble 为集成基线，不考虑 Iron 兼容。机械臂组资料中的 Jazzy 系上游项目"
     "（SO-ARM100、LeRobot）的参考版本，不得据此迁移本项目基线；"
     "如需迁移，仅评估 Jazzy 及以上 LTS 版本并走 ICR"),
    ("上位机平台",
     "香橙派 5（8 GB RAM，RK3588S，6 TOPS NPU），对应 7.1 节的 wheelchair-core"),
    ("环境交付方式", "统一 Docker 镜像或虚拟机模板，ROS_DOMAIN_ID 一致，消除环境差异"),
    ("DDS 域", "ROS_DOMAIN_ID=26；如实验室冲突，由架构组统一调整"),
    ("工作空间", "wheelchair_ws"),
    ("接口包", "wheelchair_interfaces，禁止依赖具体业务实现包"),
    ("仿真时间", "仿真节点统一 use_sim_time=true；实物统一 false"),
], [2.8, 14.4], font_size=8.6)

add_heading(doc, "4.2 QoS 配置", 2)
add_caption(doc, "表 4-2  标准 QoS 配置档")
add_table(doc, ["档位", "可靠性", "历史与深度", "持久性", "适用接口"], [
    ("CONTROL", "RELIABLE", "KEEP_LAST 1", "VOLATILE", "速度、模式、安全命令"),
    ("STATE", "RELIABLE", "KEEP_LAST 10", "VOLATILE", "里程计、电池、系统状态"),
    ("SENSOR", "BEST_EFFORT", "KEEP_LAST 5", "VOLATILE",
     "激光、图像、点云、IMU 高频数据"),
    ("EVENT", "RELIABLE", "KEEP_LAST 20", "VOLATILE", "故障、语音意图、检测结果"),
    ("TF", "RELIABLE", "KEEP_LAST 100", "VOLATILE", "/tf 动态坐标变换"),
    ("STATIC", "RELIABLE", "KEEP_LAST 1", "TRANSIENT_LOCAL",
     "/tf_static 和低频静态配置"),
], [2.0, 2.6, 3.2, 3.4, 6.0], font_size=8.6)
add_text(doc, "发布方和订阅方必须使用兼容 QoS。图像、点云和激光数据允许丢帧，"
              "不允许因重传阻塞控制链路。安全状态采用可靠传输，并由订阅方实施超时保护。")
add_note(doc, "本版新增 TF 档并用于 /tf，闭环 ICR-003。此前内部草案把 /tf 按 SENSOR 档"
              "（BEST_EFFORT）发布，而 tf2_ros 与 RViz 2 的订阅端默认按 RELIABLE 请求，"
              "发布端可靠性低于订阅端请求时连接无法建立，会导致 5.3 节的 view_frames 检查"
              "与 IF-04 验收失败。不使用 STATE 档的原因是其实例深度 KEEP_LAST 10 "
              "对 30 至 50 Hz 的坐标变换过浅，会丢帧导致 lookupTransform 失败。",
         kind="plain")

# ---------------------------------------------------------------- p_b_topic.py
add_heading(doc, "4.3 Topic 清单", 2)
add_caption(doc, "表 4-3  全局 Topic 基线")
add_table(doc, ["Topic", "类型", "发布方", "订阅方", "频率", "QoS", "说明"], [
    ("/cmd_vel", "geometry_msgs/msg/Twist", "安全过滤器", "串口桥", "20 Hz", "CONTROL",
     "唯一实物底盘速度输入"),
    ("/wheelchair/cmd_vel/nav", "geometry_msgs/msg/Twist", "Nav2", "速度复用器",
     "10-20 Hz", "CONTROL", "Nav2 输出重映射"),
    ("/wheelchair/cmd_vel/teleop", "geometry_msgs/msg/Twist",
     "手柄节点（ESP32 网关）", "速度复用器", "20 Hz", "CONTROL",
     "人工接管优先级高于导航"),
    ("/wheelchair/cmd_vel/task", "geometry_msgs/msg/Twist", "状态机", "速度复用器",
     "按需 20 Hz", "CONTROL", "仅用于低速短动作"),
    ("/wheelchair/cmd_vel_raw", "geometry_msgs/msg/Twist", "速度复用器", "安全过滤器",
     "20 Hz", "CONTROL", "仲裁结果，尚未经安全校验，禁止直接下发串口"),
    ("/wheelchair/base/odom", "nav_msgs/msg/Odometry", "底盘里程计或 EKF",
     "导航与测试", "30 Hz", "STATE", "frame_id=odom"),
    ("/joint_states", "sensor_msgs/msg/JointState", "底盘与机械臂驱动",
     "robot_state_publisher、MoveIt 2", "30 Hz", "STATE", "关节名称与 URDF 一致"),
    ("/wheelchair/base/mcu_state", "wheelchair_interfaces/msg/McuState", "串口桥",
     "监控与测试", "10 Hz", "STATE", "固件版本、通信计数、状态"),
    ("/wheelchair/power/battery_state", "sensor_msgs/msg/BatteryState", "串口桥",
     "系统监控", "1 Hz", "STATE", "电压电流百分比"),
    ("/wheelchair/imu/data", "sensor_msgs/msg/Imu", "IMU 驱动或串口桥",
     "EKF 与安全节点", "50 Hz", "SENSOR", "frame_id=imu_link"),
    ("/wheelchair/ultrasonic/ranges", "wheelchair_interfaces/msg/RangeArray", "串口桥",
     "安全与避障", "50 Hz（下限 10 Hz）", "SENSOR",
     "按传感器名与距离数组发布；命名与顺序未固定前不得发布，见表 6-17"),
    ("/scan", "sensor_msgs/msg/LaserScan", "雷达驱动", "SLAM 与 Nav2", "5-15 Hz",
     "SENSOR", "frame_id=laser_frame"),
    ("/camera/color/image_raw", "sensor_msgs/msg/Image", "RGB-D 驱动", "视觉识别",
     "15-30 Hz", "SENSOR", "轮椅端相机原始彩色图"),
    ("/camera/color/camera_info", "sensor_msgs/msg/CameraInfo", "RGB-D 驱动",
     "视觉识别", "随图像", "STATE", "内参与畸变参数"),
    ("/camera/depth/image_rect_raw", "sensor_msgs/msg/Image", "RGB-D 驱动", "目标定位",
     "15-30 Hz", "SENSOR", "深度单位由 encoding 确定"),
    ("/camera/depth/points", "sensor_msgs/msg/PointCloud2", "RGB-D 驱动",
     "代价地图与抓取", "5-15 Hz", "SENSOR", "可按算力降频"),
    ("/arm_camera/color/image_raw", "sensor_msgs/msg/Image", "臂端相机驱动",
     "手眼标定与抓取", "15-30 Hz", "SENSOR", "臂端相机，型号待定标，见表 5-1"),
    ("/arm_camera/color/camera_info", "sensor_msgs/msg/CameraInfo", "臂端相机驱动",
     "手眼标定", "随图像", "STATE", "内参与畸变参数"),
    ("/arm_camera/depth/image_rect_raw", "sensor_msgs/msg/Image", "臂端相机驱动",
     "目标定位", "15-30 Hz", "SENSOR", "深度单位由 encoding 确定"),
    ("/arm_camera/depth/points", "sensor_msgs/msg/PointCloud2", "臂端相机驱动",
     "抓取规划", "5-15 Hz", "SENSOR", "frame_id=arm_camera_depth_optical_frame"),
    ("/map", "nav_msgs/msg/OccupancyGrid", "SLAM 或 map_server", "Nav2 与 RViz 2",
     "低频或事件", "STATIC", "frame_id=map；建图分辨率 0.05 m"),
    ("/wheelchair/perception/detections", "vision_msgs/msg/Detection3DArray",
     "目标识别节点", "机械臂与状态机", "5-15 Hz", "EVENT", "类别、置信度、三维包围盒"),
    ("/wheelchair/perception/target_pose", "geometry_msgs/msg/PoseStamped",
     "目标定位节点", "机械臂规划", "事件", "EVENT", "必须给出 frame_id 和时间戳"),
    ("/wheelchair/voice/text", "std_msgs/msg/String", "离线语音节点", "意图解析节点",
     "事件", "EVENT", "识别后的原始文本"),
    ("/wheelchair/voice/intent", "wheelchair_interfaces/msg/VoiceIntent",
     "意图解析节点", "状态机", "事件", "EVENT", "结构化意图和参数，取值见附录 C"),
    ("/wheelchair/stand/state", "wheelchair_interfaces/msg/StandState", "推杆控制节点",
     "状态机与安全节点", "10 Hz", "STATE", "姿态、行程、限位和故障"),
    ("/wheelchair/safety/status", "wheelchair_interfaces/msg/SafetyStatus",
     "安全监督节点", "全系统", "10 Hz 加事件", "STATE", "急停、倾角、障碍和故障锁存"),
    ("/wheelchair/system/mode", "wheelchair_interfaces/msg/SystemMode", "状态机",
     "全系统", "2 Hz 加事件", "STATE", "当前模式及变更原因"),
    ("/wheelchair/arm/wrench", "geometry_msgs/msg/WrenchStamped", "力矩传感器驱动",
     "抓取控制与安全", "100 Hz（可降频）", "SENSOR",
     "frame_id=arm_link_6；传感器型号与量程待定标"),
    ("/diagnostics", "diagnostic_msgs/msg/DiagnosticArray", "所有硬件与核心节点",
     "监控与测试", "1 Hz 加事件", "EVENT", "标准诊断聚合入口"),
    ("/tf", "tf2_msgs/msg/TFMessage", "各动态 TF 唯一所有者", "全系统", "按表 5-2",
     "TF", "禁止重复发布同一变换"),
    ("/tf_static", "tf2_msgs/msg/TFMessage", "robot_state_publisher", "全系统",
     "启动时", "STATIC", "静态外参"),
    ("/clock", "rosgraph_msgs/msg/Clock", "仿真器", "仿真节点", "仿真步进", "STATE",
     "仅仿真发布"),
], [3.6, 3.55, 1.9, 2.0, 1.7, 1.8, 3.0], font_size=7.0)
add_note(doc, "本表由内部草案的 27 条扩至 33 条：新增 /wheelchair/cmd_vel_raw 明确"
              "速度复用器与安全过滤器之间的中间话题；新增 /arm_camera/ 下 4 条"
              "支持机械臂组的手眼标定需求；新增 /wheelchair/arm/wrench 支持其力矩传感器；"
              "/wheelchair/ultrasonic/ranges 的频率由 10 Hz 改为 50 Hz（下限 10 Hz）；"
              "/tf 由 SENSOR 档改为 TF 档。", kind="plain")

# ---------------------------------------------------------------- p_c_ch456.py
add_heading(doc, "4.4 Service 与 Action 清单", 2)
add_caption(doc, "表 4-4  Service 与 Action 清单")
add_table(doc, ["名称", "种类与类型", "服务端", "用途与约束"], [
    ("/wheelchair/safety/set_soft_estop", "Service  std_srvs/srv/SetBool",
     "安全监督节点", "true 锁存软件急停；false 仅提出解除请求，仍需满足硬件与故障条件"),
    ("/wheelchair/system/reset_fault", "Service  std_srvs/srv/Trigger", "状态机",
     "在速度为零、急停释放且故障源消失后清除可恢复故障"),
    ("/wheelchair/system/health_check", "Service  std_srvs/srv/Trigger", "诊断聚合节点",
     "返回启动自检结论，详细项同时发布到 /diagnostics"),
    ("/navigate_to_pose", "Action  nav2_msgs/action/NavigateToPose", "Nav2",
     "标准点到点导航，不再包装第二套导航 Action"),
    ("/wheelchair/arm/grasp_object", "Action  wheelchair_interfaces/action/GraspObject",
     "抓取执行节点", "识别、规划、夹爪闭合与抬升的完整动作"),
    ("/wheelchair/stand/change_posture",
     "Action  wheelchair_interfaces/action/ChangePosture", "推杆控制节点",
     "坐下、站立或保持；执行期间底盘必须锁止"),
    ("/arm_controller/follow_joint_trajectory",
     "Action  control_msgs/action/FollowJointTrajectory", "机械臂驱动节点",
     "MoveIt 2 的标准执行出口。控制器名固定为 arm_controller，"
     "不得改用 MoveIt 2 配置模板的默认名 joint_trajectory_controller"),
], [4.2, 5.6, 2.2, 5.2], font_size=7.8)
add_note(doc, "末行为本版新增。该 Action 是 MoveIt 2 与机械臂驱动之间唯一的轨迹执行接口，"
              "内部草案完全缺失，会导致机械臂组无法接入规划结果。", kind="plain")

add_heading(doc, "4.5 速度命令仲裁", 2)
add_numbered(doc, "安全过滤器拥有最高控制权，可把任意速度命令置零。")
add_numbered(doc, "优先级全序为：安全过滤器 > 手柄人工接管 > Nav2 > 语音 > 状态机低速直控。"
                  "语音通常生成导航目标，不直接持续发布速度。")
add_numbered(doc, "速度源必须以 10 Hz 以上刷新。超过 200 ms 未更新即视为过期，"
                  "复用器输出零速度。")
add_numbered(doc, "实物初期线速度上限为 0.20 m/s、角速度上限为 0.40 rad/s；"
                  "通过安全评审后只允许用受版本控制的配置文件调整。")
add_numbered(doc, "站立、急停、严重倾斜、串口失联或关键传感器故障时，线速度和角速度强制为零。")
add_numbered(doc, "本项目的速度数值分三个层次，不得混用：① 安全上限，"
                  "由上位机安全过滤器与下位机固件共同强制，实物初期为 0.20 m/s 与 "
                  "0.40 rad/s，存于 config/real/safety_limits.yaml；"
                  "② 台架调试限速，仅用于架空轮或单轮台架，存于底盘组固件内部常量；"
                  "③ 机械设计上限，为机械与电机的能力边界，不得作为运行配置下发。"
                  "三者关系为 ① < ② < ③。")
add_numbered(doc, "急停锁存或故障锁存期间，系统必须拒绝全部动作类语音意图，仅放行 STOP。"
                  "MOVE_FORWARD、MOVE_BACKWARD、TURN_LEFT、TURN_RIGHT 等意图必须由"
                  "意图解析节点翻译为定距或限时的低速动作，经速度复用器以不超过 2 s 的"
                  "时效发布，不得持续发布 Twist。")

add_heading(doc, "4.6 节点生命周期与启动顺序", 2)
for t in ["robot_state_publisher 与静态 TF", "硬件驱动和 serial_bridge",
          "diagnostics 与 safety_supervisor", "localization / SLAM 与 perception",
          "Nav2 与 MoveIt 2", "voice 与 task_supervisor",
          "speed_mux 与 safety_filter 进入 ACTIVE"]:
    add_text(doc, t, indent=0.6, after=2)
add_text(doc, "核心节点应采用 ROS 2 Lifecycle。任一安全前置节点未激活时，控制输出保持为零。"
              "关停顺序与启动顺序相反，并在断开串口或电源前发送零速度。")

# ================================================================ 5 TF 坐标系标准
add_heading(doc, "5 TF 坐标系标准", 1)

add_heading(doc, "5.1 TF 主链", 2)
add_code(doc, [
    "map -> odom -> base_footprint -> base_link",
    "base_link -> laser_frame",
    "base_link -> imu_link",
    "base_link -> camera_link -> camera_color_optical_frame",
    "base_link -> camera_link -> camera_depth_optical_frame",
    "base_link -> seat_link -> arm_base_link -> arm_link_1 ... arm_link_6",
    "                                        -> gripper_link",
    "                                        -> arm_camera_link",
    "                                           -> arm_camera_color_optical_frame",
    "                                           -> arm_camera_depth_optical_frame",
], size=8.4)
add_text(doc, "frame 名称不得带前导斜杠。TF 树只能有一个根节点；同一 parent-child 变换只能由"
              "一个节点发布。光学坐标系按相机驱动标准保持 z 向前、x 向右、y 向下，"
              "业务节点不得手工改写图像坐标含义。")
add_text(doc, "相机驱动必须关闭 TF 发布功能，由 robot_state_publisher 统一发布 camera_link、"
              "arm_camera_link 与其光学坐标系的静态变换，避免驱动与 URDF 重复发布。")
add_text(doc, "本车无悬架，base_footprint 与 base_link 之间的变换允许仅含安装高度。"
              "但该层与名称不得删除或改写：它是 REP 105 约定的地面投影层，"
              "删除后二维导航与代价地图的地面约束将失去依据。激光雷达坐标系名为 "
              "laser_frame，不得写作 laser_link 或其他别名；"
              "SLAM 侧的 tracking_frame 应填 base_footprint。")

add_caption(doc, "表 5-1  坐标系定义")
add_table(doc, ["Frame", "父坐标系", "含义", "发布方", "类型或频率"], [
    ("map", "无", "全局固定地图坐标系", "SLAM 或 map_server", "根坐标系"),
    ("odom", "map", "局部连续里程计坐标系", "SLAM 或定位节点", "5-20 Hz"),
    ("base_footprint", "odom", "车体在地面的投影，z=0", "EKF 或底盘里程计", "30 Hz"),
    ("base_link", "base_footprint", "车体几何参考中心", "robot_state_publisher",
     "静态或关节派生"),
    ("laser_frame", "base_link", "激光雷达测量原点", "robot_state_publisher", "静态"),
    ("imu_link", "base_link", "IMU 测量原点", "robot_state_publisher", "静态"),
    ("camera_link", "base_link", "轮椅端 RGB-D 相机机械安装坐标系",
     "robot_state_publisher", "静态"),
    ("camera_color_optical_frame", "camera_link", "彩色图像光学坐标系",
     "robot_state_publisher", "静态"),
    ("camera_depth_optical_frame", "camera_link", "深度图像光学坐标系",
     "robot_state_publisher", "静态"),
    ("seat_link", "base_link", "座椅与站立机构参考坐标系", "robot_state_publisher",
     "随关节状态"),
    ("arm_base_link", "seat_link", "机械臂基座坐标系", "robot_state_publisher", "静态"),
    ("arm_link_1 … arm_link_6", "arm_link_(n-1)", "六轴机械臂关节链，逐级串联",
     "robot_state_publisher", "随关节状态"),
    ("arm_camera_link", "arm_link_6", "臂端相机机械安装坐标系",
     "robot_state_publisher", "静态，外参待标定"),
    ("arm_camera_color_optical_frame", "arm_camera_link", "臂端彩色图像光学坐标系",
     "robot_state_publisher", "静态"),
    ("arm_camera_depth_optical_frame", "arm_camera_link", "臂端深度图像光学坐标系",
     "robot_state_publisher", "静态"),
    ("gripper_link", "arm_link_6", "夹爪工具中心参考", "robot_state_publisher",
     "随关节状态"),
], [5.2, 2.8, 3.8, 3.1, 2.3], font_size=7.4)

add_heading(doc, "5.2 TF 所有权", 2)
add_caption(doc, "表 5-2  TF 所有权")
add_table(doc, ["变换", "唯一发布方", "验收要求"], [
    ("map -> odom", "SLAM 或定位节点二选一", "切换模式时不得同时运行两个发布源"),
    ("odom -> base_footprint", "robot_localization EKF 或底盘里程计二选一",
     "连续无跳变，时间戳新鲜"),
    ("base_footprint -> base_link", "robot_state_publisher", "安装高度与 URDF 一致"),
    ("base_link -> 传感器", "robot_state_publisher", "外参来自 CAD 和实测标定"),
    ("机械臂关节链", "robot_state_publisher", "JointState 名称、数量和 URDF 一致"),
    ("arm_link_6 -> arm_camera_link", "robot_state_publisher",
     "外参来自手眼标定报告，标定完成前不得进入抓取联调"),
], [4.6, 6.0, 6.6], font_size=8.2)

add_heading(doc, "5.3 TF 验收条件", 2)
for t in [
    "运行 ros2 run tf2_tools view_frames 后只有一棵连通树，无重复发布警告。",
    "任意传感器数据的 header.frame_id 在 TF 树中存在，并可在数据时间戳处转换到 base_link。",
    "静态外参误差应在安装和标定报告中记录；更新外参需同步更新 URDF 或标定 YAML。",
    "map 和 odom 的职责不得交换：map 可发生全局校正，odom 必须局部连续。",
    "/tf 必须以 TF 档发布，订阅端与发布端的 QoS 可靠性不得倒挂，见 4.2 节注。",
]:
    add_bullet(doc, t)

# ---------------------------------------------------------------- p_d_ch56.py
# ================================================================ 6 串口协议
add_heading(doc, "6 上位机与下位机串口协议", 1)

add_heading(doc, "6.1 物理层参数与链路拓扑", 2)
add_text(doc, "上位机与下位机之间为两级链路。上位机与 ESP32 网关之间的链路使用本章规定的"
              "二进制帧，是本项目唯一的跨组串口接口；ESP32 与 STM32 之间的 UART 链路"
              "（CRC8 校验、20 ms 心跳）属底盘组内部实现，本标准不约束其帧格式。"
              "ESP32 必须把 STM32 的遥测按 6.3 节的 MCU 到 HOST 消息透传，"
              "并以 serial_bridge 作为 ROS 2 侧的唯一端点。")
add_caption(doc, "表 6-1  串口物理层参数")
add_table(doc, ["参数", "V1.0 约定"], [
    ("接口", "USB CDC 或 USB 转 UART；实物布线较长时可使用隔离 RS-485"),
    ("波特率", "115200 bit/s"),
    ("数据格式", "8 数据位，1 停止位，无校验，8N1"),
    ("字节序", "多字节整数统一 little-endian"),
    ("最大载荷", "128 byte"),
    ("发送策略", "二进制帧，无行结束符；控制命令可要求 ACK"),
    ("端口配置", "通过参数 serial_port 和 baud_rate 配置，不得硬编码 COM 或 /dev 名称"),
    ("链路拓扑", "上位机 至 ESP32 网关（本章协议）；ESP32 至 STM32 为板间链路（内部实现）"),
], [2.8, 14.4], font_size=8.6)

add_heading(doc, "6.2 通用数据帧", 2)
add_caption(doc, "表 6-2  串口帧格式")
add_table(doc, ["偏移", "长度", "字段", "说明"], [
    ("0", "2", "SOF", "固定 0xAA 0x55"),
    ("2", "1", "VERSION", "协议版本，V1.0 起固定 0x01；载荷长度由 LENGTH 字段决定"),
    ("3", "1", "MSG_ID", "消息编号，见表 6-3"),
    ("4", "1", "FLAGS", "bit0 ACK_REQ，bit1 IS_ACK，bit2 IS_ERROR，其余必须为 0"),
    ("5", "2", "SEQ", "序号 uint16，发送方每帧递增，溢出后回到 0"),
    ("7", "2", "LENGTH", "PAYLOAD 字节数 uint16，范围 0 至 128"),
    ("9", "N", "PAYLOAD", "消息载荷，按 MSG_ID 解释"),
    ("9+N", "2", "CRC16", "CRC-16/MODBUS，覆盖 VERSION 至 PAYLOAD，低字节先发送"),
], [1.4, 1.3, 2.2, 12.3], font_size=8.4)
add_text(doc, "接收端先查找 SOF，再读取固定头和 LENGTH。LENGTH 超过 128 时立即丢弃并重新同步。"
              "CRC 错误帧不得执行，也不得用其中的 SEQ 更新有效序号。")

add_heading(doc, "6.3 消息编号", 2)
add_caption(doc, "表 6-3  串口消息编号")
add_table(doc, ["ID", "名称", "方向", "频率", "用途"], [
    ("0x01", "HOST_HEARTBEAT", "上位机 -> MCU", "10 Hz", "上位机存活和系统模式"),
    ("0x10", "CMD_VEL", "上位机 -> MCU", "20 Hz", "底盘线速度和角速度命令"),
    ("0x11", "CMD_POSTURE", "上位机 -> MCU", "事件", "坐下、站立或保持命令"),
    ("0x12", "CMD_SOFT_ESTOP", "上位机 -> MCU", "事件", "软件急停锁存或解除请求"),
    ("0x13", "CMD_OUTPUT_ENABLE", "上位机 -> MCU", "事件",
     "执行机构使能；自检未通过时拒绝"),
    ("0x7E", "ACK_NACK", "双向", "响应", "确认可执行命令或返回错误"),
    ("0x81", "MCU_HEARTBEAT", "MCU -> 上位机", "10 Hz", "固件状态和通信计数"),
    ("0xA0", "BASE_STATE", "MCU -> 上位机", "30 Hz", "里程计、速度和四轮速度"),
    ("0xA1", "IMU_STATE", "MCU -> 上位机", "50 Hz", "加速度、角速度和姿态"),
    ("0xA2", "POWER_STATE", "MCU -> 上位机", "1 Hz", "电池电压、电流、SOC 和温度"),
    ("0xA3", "SAFETY_STATE", "MCU -> 上位机", "10 Hz 加事件",
     "急停、限位、倾角和故障位"),
    ("0xA4", "ULTRASONIC_STATE", "MCU -> 上位机", "50 Hz（下限 10 Hz）",
     "超声波距离数组"),
], [1.2, 3.5, 3.0, 2.4, 7.1], font_size=8.2)
add_note(doc, "本版把 0xA4 ULTRASONIC_STATE 的频率由 10 Hz 改为 50 Hz、10 Hz 记为下限，"
              "与电气动力与底层控制组给出的 HC-SR04 刷新能力一致；"
              "50 Hz 对 30 cm 安全阈值的响应更优，带宽核算约 42 kbit/s，"
              "115200 bit/s 链路余量充足。", kind="plain")

add_heading(doc, "6.4 核心载荷定义", 2)
add_text(doc, "本节共 14 张载荷表。表 6-4 至表 6-7 为内部草案已有内容；表 6-8 至表 6-12、"
              "表 6-14 至表 6-17 为本版新增，用于补齐原 ICR-001 所列的 9 条缺失消息。")

add_caption(doc, "表 6-4  CMD_VEL 载荷（MSG_ID 0x10）")
add_table(doc, ["偏移", "类型", "字段", "单位与范围"], [
    ("0", "int16", "linear_x", "mm/s；实物初期 -200 至 200"),
    ("2", "int16", "angular_z", "mrad/s；实物初期 -400 至 400"),
    ("4", "uint16", "timeout_ms", "命令有效期，100 至 500，推荐 200"),
], [1.3, 2.0, 3.6, 10.3], font_size=8.4)

add_caption(doc, "表 6-5  BASE_STATE 载荷（MSG_ID 0xA0）")
add_table(doc, ["偏移", "类型", "字段", "单位与说明"], [
    ("0", "uint32", "mcu_time_ms", "MCU 启动后的毫秒数"),
    ("4", "int32", "x_mm", "里程计 x，mm"),
    ("8", "int32", "y_mm", "里程计 y，mm"),
    ("12", "int32", "yaw_mrad", "偏航角，mrad"),
    ("16", "int16", "linear_mm_s", "线速度，mm/s"),
    ("18", "int16", "angular_mrad_s", "角速度，mrad/s"),
    ("20", "int16[4]", "wheel_mm_s", "前左、前右、后左、后右轮速，mm/s"),
], [1.3, 2.0, 3.6, 10.3], font_size=8.4)

add_caption(doc, "表 6-6  SAFETY_STATE 载荷（MSG_ID 0xA3）")
add_table(doc, ["偏移", "类型", "字段", "说明"], [
    ("0", "uint32", "mcu_time_ms", "MCU 时间"),
    ("4", "uint8", "estop_state", "0 释放，1 物理急停，2 软件急停，3 两者同时"),
    ("5", "uint8", "drive_enabled", "0 禁止输出，1 允许输出"),
    ("6", "uint32", "fault_bits", "故障位，见表 6-7"),
    ("10", "int16", "roll_mrad", "车体滚转角"),
    ("12", "int16", "pitch_mrad", "车体俯仰角"),
    ("14", "uint16", "min_range_mm", "最近障碍距离，未知为 0xFFFF"),
    ("16", "uint8", "posture_enabled",
     "站立机构使能状态：0 未使能，1 使能；由推杆控制固件上报"),
], [1.3, 2.0, 3.6, 10.3], font_size=8.4)
add_text(doc, "serial_bridge 必须按 LENGTH 字段确定载荷长度，并同时容忍 16 与 17 两种长度。"
              "若未收到 posture_enabled 字段，SafetyStatus.posture_enabled 置 false，"
              "同时必须通过 /diagnostics 报告「站立机构使能状态来源缺失」——"
              "该字段在 SafetyStatus.msg 中为 bool，无法自行表达未知，"
              "不予报告即等同于静默失败。")

add_caption(doc, "表 6-7  fault_bits 位定义")
add_table(doc, ["位", "名称", "等级", "系统行为"], [
    ("0", "COMM_TIMEOUT", "严重", "速度置零，禁止驱动"),
    ("1", "PHYSICAL_ESTOP", "严重", "硬件急停锁存，禁止驱动"),
    ("2", "SOFT_ESTOP", "严重", "软件急停锁存，禁止驱动"),
    ("3", "OVERCURRENT", "严重", "禁止对应输出并报告"),
    ("4", "UNDERVOLTAGE", "严重", "停止运动，保护电池"),
    ("5", "OVERTEMPERATURE", "严重", "停止或降额，按固件阈值"),
    ("6", "TILT_LIMIT", "严重", "速度置零，禁止站立"),
    ("7", "ACTUATOR_LIMIT", "警告或严重", "停止推杆，保留底盘判断"),
    ("8", "SENSOR_INVALID", "警告", "标记数据无效并通知上位机"),
    ("9", "CRC_RATE_HIGH", "警告", "保持安全限速并检查链路"),
    ("10", "WHEEL_STALL", "严重", "实际轮速与指令持续不符时判定失速，速度置零，"
                                  "禁止驱动，需复位"),
    ("11-31", "RESERVED", "保留", "发送端置 0，接收端忽略未知位并记录"),
], [1.3, 3.6, 2.4, 9.9], font_size=8.4)
add_note(doc, "bit10 WHEEL_STALL 为本版新增。底盘组的失速检测（有指令但编码器不转）"
              "在原故障位表中无处安放，只能映射到含义不符的 OVERCURRENT。"
              "已用位止于 bit9，bit10 为下一个空闲位，新增不破坏既有定义。", kind="plain")

# ---------------------------------------------------------------- p_e_payload.py
add_text(doc, "以下表 6-8 至表 6-12、表 6-14 至表 6-17 为本单元按电气动力与底层控制组"
              "已公布的选型与接线方案代拟的草案，用于补齐原 ICR-001 所列的 9 条缺失消息。"
              "字段的偏移、类型、缩放比例与哨兵取值均需该组按实测确认后方可视为冻结。")
for _t in ["表 6-8   HOST_HEARTBEAT 载荷（MSG_ID 0x01）",
           "表 6-9   CMD_POSTURE 载荷（MSG_ID 0x11）",
           "表 6-10  CMD_SOFT_ESTOP 载荷（MSG_ID 0x12）",
           "表 6-11  CMD_OUTPUT_ENABLE 载荷（MSG_ID 0x13）",
           "表 6-12  ACK_NACK 载荷（MSG_ID 0x7E）",
           "表 6-13  ACK_NACK 错误码",
           "表 6-14  MCU_HEARTBEAT 载荷（MSG_ID 0x81）",
           "表 6-15  IMU_STATE 载荷（MSG_ID 0xA1）",
           "表 6-16  POWER_STATE 载荷（MSG_ID 0xA2）",
           "表 6-17  ULTRASONIC_STATE 载荷（MSG_ID 0xA4）"]:
    pass  # 占位，逐个输出见下

add_caption(doc, "表 6-8   HOST_HEARTBEAT 载荷（MSG_ID 0x01，上位机到 MCU，10 Hz）")
add_table(doc, ["偏移", "类型", "字段", "单位与范围"], [
    ("0", "uint8", "mode", "系统模式枚举，见表 2-2，取值 0 至 6"),
    ("1", "uint8", "flags", "bit0 请求使能，bit1 请求软件急停，其余保留必须为 0"),
    ("2", "uint16", "host_time_ms", "上位机单调时钟低 16 位，ms；仅用于打点与丢帧判断，"
                                    "MCU 不得据此定时"),
], [1.3, 2.0, 3.6, 10.3], font_size=8.4)
add_note(doc, "LENGTH = 4。代拟草案，待电气动力与底层控制组确认。", kind="plain")

add_caption(doc, "表 6-9   CMD_POSTURE 载荷（MSG_ID 0x11，上位机到 MCU，事件）")
add_table(doc, ["偏移", "类型", "字段", "单位与范围"], [
    ("0", "uint8", "target", "0 保持，1 坐下，2 站立；对应 ChangePosture.action 的 target"),
    ("1", "uint8", "speed_ratio", "速度比例，0 至 100，单位 %；0 视为非法并以 "
                                  "INVALID_VALUE 拒绝"),
    ("2", "uint16", "timeout_ms", "命令有效期，推荐 2000"),
], [1.3, 2.0, 3.6, 10.3], font_size=8.4)
add_note(doc, "LENGTH = 4。代拟草案，待电气动力与底层控制组确认。", kind="plain")

add_caption(doc, "表 6-10  CMD_SOFT_ESTOP 载荷（MSG_ID 0x12，上位机到 MCU，事件）")
add_table(doc, ["偏移", "类型", "字段", "单位与范围"], [
    ("0", "uint8", "action", "0 提出解除请求（仍需满足硬件与故障条件），1 锁存软件急停"),
    ("1", "uint8", "reserved", "保留，必须为 0"),
], [1.3, 2.0, 3.6, 10.3], font_size=8.4)
add_note(doc, "LENGTH = 2。代拟草案，待电气动力与底层控制组确认。", kind="plain")

add_caption(doc, "表 6-11  CMD_OUTPUT_ENABLE 载荷（MSG_ID 0x13，上位机到 MCU，事件）")
add_table(doc, ["偏移", "类型", "字段", "单位与范围"], [
    ("0", "uint8", "enable", "0 禁止执行机构输出，1 请求使能；自检未通过时 MCU 以 "
                             "NOT_READY 拒绝"),
    ("1", "uint8", "reserved", "保留，必须为 0"),
], [1.3, 2.0, 3.6, 10.3], font_size=8.4)
add_note(doc, "LENGTH = 2。代拟草案，待电气动力与底层控制组确认。", kind="plain")

add_caption(doc, "表 6-12  ACK_NACK 载荷（MSG_ID 0x7E，双向，响应）")
add_table(doc, ["偏移", "类型", "字段", "说明"], [
    ("0", "uint16", "ack_seq", "被确认命令的 SEQ"),
    ("2", "uint8", "ack_msg_id", "被确认命令的 MSG_ID"),
    ("3", "uint8", "result", "0 成功；非 0 为错误码，见表 6-13"),
    ("4", "uint16", "detail", "错误补充信息，无补充时为 0"),
], [1.3, 2.0, 3.6, 10.3], font_size=8.4)
add_note(doc, "LENGTH = 6。本条为内部草案已有定义，本版仅补上偏移列。", kind="plain")

add_caption(doc, "表 6-13  ACK_NACK 错误码")
add_table(doc, ["错误码", "名称", "含义"], [
    ("0", "OK", "命令已接收并通过合法性检查"),
    ("1", "BAD_LENGTH", "载荷长度不符合消息定义"),
    ("2", "UNSUPPORTED", "版本或消息编号不支持"),
    ("3", "INVALID_VALUE", "字段越界或保留位非零"),
    ("4", "NOT_READY", "自检未通过或设备未就绪"),
    ("5", "SAFETY_LOCKED", "急停、倾斜或故障锁存导致拒绝"),
    ("6", "BUSY", "已有互斥动作正在执行"),
    ("7", "TIMEOUT", "命令已过有效期"),
    ("8", "INTERNAL_ERROR", "固件内部错误"),
], [1.6, 3.6, 12.0], font_size=8.4)

add_caption(doc, "表 6-14  MCU_HEARTBEAT 载荷（MSG_ID 0x81，MCU 到上位机，10 Hz）")
add_table(doc, ["偏移", "类型", "字段", "单位与说明"], [
    ("0", "uint32", "uptime_ms", "MCU 启动后的毫秒数"),
    ("4", "uint16", "firmware_version", "版本号，高 8 位为主版本、低 8 位为次版本"),
    ("6", "uint32", "valid_rx_frames", "累计有效接收帧数"),
    ("10", "uint32", "crc_error_frames", "累计 CRC 错误帧数，第 9 章 IF 验收的核查项"),
    ("14", "uint32", "timeout_count", "累计通信超时次数"),
    ("18", "uint16", "last_rx_seq", "最近一次有效接收帧的 SEQ"),
    ("20", "uint8", "controller_state", "0 初始化，1 就绪，2 运行，3 故障"),
    ("21", "uint8", "reserved", "保留，必须为 0"),
], [1.3, 2.0, 3.8, 10.1], font_size=8.4)
add_note(doc, "LENGTH = 22。代拟草案，待电气动力与底层控制组确认。"
              "本条是上位机侧唯一的固件健康通道，第 9 章 IF-05 与 IF-06 "
              "依赖其 crc_error_frames 计数，应优先冻结。")

add_caption(doc, "表 6-15  IMU_STATE 载荷（MSG_ID 0xA1，MCU 到上位机，50 Hz）")
add_table(doc, ["偏移", "类型", "字段", "单位与量程"], [
    ("0", "uint32", "mcu_time_ms", "MCU 启动后的毫秒数"),
    ("4", "int16[3]", "accel_mg", "三轴加速度，mg，量程 ±2 g 即 ±2000 mg；轴序 x, y, z"),
    ("10", "int16[3]", "gyro_mrad_s",
     "三轴角速度，mrad/s，量程 ±32767 mrad/s；BMI088 满量程 ±2000 度每秒"
     "（合 ±34.9 rad/s），超出部分按量程饱和；轴序 x, y, z"),
    ("16", "int16", "roll_mrad", "横滚角，mrad"),
    ("18", "int16", "pitch_mrad", "俯仰角，mrad"),
    ("20", "int16", "yaw_mrad", "偏航角，mrad；未做姿态融合时为 0"),
    ("22", "uint8", "calibration", "标定状态：0 未标定，1 已标定，2 标定中"),
    ("23", "uint8", "reserved", "保留，必须为 0"),
], [1.3, 2.0, 3.5, 10.4], font_size=8.4)
add_note(doc, "LENGTH = 24。代拟草案，待电气动力与底层控制组确认。"
              "该传感器为博世 BMI088 六轴惯性测量单元，经 SPI 连接 STM32。")

add_caption(doc, "表 6-16  POWER_STATE 载荷（MSG_ID 0xA2，MCU 到上位机，1 Hz）")
add_table(doc, ["偏移", "类型", "字段", "单位与量程"], [
    ("0", "uint32", "mcu_time_ms", "MCU 启动后的毫秒数"),
    ("4", "uint16", "bus_voltage_mv", "母线电压，mV，缩放 1 mV；按 0 至 60000 mV"
                                      "（不高于 60 V）量程预留，与母线电压定标结果无关"),
    ("6", "int16", "current_ma", "母线电流，mA；放电为正，充电为负"),
    ("8", "uint8", "soc_percent", "剩余电量，0 至 100；未知为 0xFF"),
    ("9", "uint8", "reserved", "保留，必须为 0"),
    ("10", "int16", "temperature_dc", "电池温度，0.1 摄氏度，量程 -400 至 1250"),
    ("12", "uint16", "bms_flags", "bit0 过压，bit1 欠压，bit2 过流，bit3 过温，"
                                  "bit4 充电中，bit5 放电中；其余保留"),
    ("14", "uint8", "cell_count", "串数"),
    ("15", "uint8", "reserved", "保留，必须为 0"),
], [1.3, 2.0, 3.5, 10.4], font_size=8.4)
add_note(doc, "LENGTH = 16。代拟草案，待电气动力与底层控制组确认。"
              "母线电压的标称值本身为待定项，见 6.8 节 T1。"
              "该消息对应 16S 磷酸铁锂电池组与 100 A BMS 的遥测方案。")

add_caption(doc, "表 6-17  ULTRASONIC_STATE 载荷（MSG_ID 0xA4，MCU 到上位机，50 Hz）")
add_table(doc, ["偏移", "类型", "字段", "单位与说明"], [
    ("0", "uint32", "mcu_time_ms", "MCU 启动后的毫秒数"),
    ("4", "uint8", "sensor_count", "本次上报的传感器路数 N，1 至 16"),
    ("5", "uint8", "scan_seq", "环形扫描序号，用于判断哪几路在本帧被刷新"),
    ("6", "uint16[N]", "range_mm", "各路距离，mm，按 sensor_names 顺序；"
                                   "未知为 0xFFFF 哨兵，serial_bridge 必须转换为 NaN"),
    ("6+2N", "uint8[N]", "quality", "各路回波质量 0 至 100，0 表示无有效回波；"
                                    "LENGTH 不足时可缺省，订阅方按未知处理"),
], [1.4, 2.1, 3.4, 10.3], font_size=8.4)
add_note(doc, "LENGTH = 6 + 3N。代拟草案，待电气动力与底层控制组确认。"
              "本车在车身四周部署 HC-SR04 构成环形探测阵列；"
              "传感器数量与安装方位尚未定标（T3），"
              "RangeArray.sensor_names 的命名与顺序未固定前不得发布该话题。")

# ---------------------------------------------------------------- p_f_ch678.py
add_heading(doc, "6.5 ACK NACK 与错误码", 2)
add_text(doc, "ACK 与 NACK 共用 0x7E 一条消息，通过 FLAGS 的 IS_ACK 与 IS_ERROR 位区分，"
              "载荷见表 6-12，错误码见表 6-13。")

add_heading(doc, "6.6 超时与重试策略", 2)
for t in [
    "MCU 连续 200 ms 未收到有效 HOST_HEARTBEAT 或 CMD_VEL 时，立即把底盘速度置零。",
    "连续 1000 ms 未收到上位机有效帧时，置 COMM_TIMEOUT 故障并禁止驱动，"
    "直至通信恢复且收到合规复位。",
    "CMD_VEL 不重发旧命令；上位机持续发送最新值。配置、推杆、急停和使能等离散命令"
    "设置 ACK_REQ，100 ms 无响应可重试 2 次。",
    "重复 SEQ 的离散命令只执行一次，并再次返回相同 ACK，避免重试造成重复动作。",
    "CRC 错误帧直接丢弃并计数；CRC 错误率 10 秒内超过 1% 时设置 CRC_RATE_HIGH。",
]:
    add_bullet(doc, t)
add_note(doc, "本版把第一条的超时由 300 ms 收紧为 200 ms。底盘运动控制单元给出的"
              "看门狗指标为 200 ms 内强制停车，按 3.4 节第 3 条"
              "「以更严格者为准」取严者。IF-07 的验收条件同步收紧。", kind="plain")

add_heading(doc, "6.7 完整帧示例", 2)
add_text(doc, "以下示例表示 SEQ=42、线速度 200 mm/s、角速度 0、有效期 200 ms 的 CMD_VEL 帧，"
              "并请求 ACK：")
_frame = bytes([0x01, 0x10, 0x01, 0x2A, 0x00, 0x06, 0x00,
                0xC8, 0x00, 0x00, 0x00, 0xC8, 0x00])
_crc = crc16_modbus(_frame)
add_code(doc, ["AA 55 01 10 01 2A 00 06 00 C8 00 00 00 C8 00 "
               f"{_crc & 0xFF:02X} {_crc >> 8:02X}"], size=10)
add_text(doc, f"CRC-16/MODBUS = 0x{_crc:04X}，低字节先发送。"
              "本帧的 CRC 由脚本在生成文档时按帧内容重新计算，"
              "与表 6-2 的覆盖范围一致。")

add_heading(doc, "6.8 待定标项（TBD）", 2)
add_text(doc, "以下四项依赖硬件选型、实测数据或采购结论，本版不代为裁定，"
              "但先冻结其接口名称与帧结构，避免后续返工。")
for t in [
    "T1 母线电压。底盘组按 24 V 采购电机与电池，动力与供电安全单元建议按 51.2 V"
    "（16S 磷酸铁锂）做安全回路验证，两者尚未合流。解除条件：由峰值电流、线束长度"
    "与驱动器电容共同定标。本版已把 POWER_STATE 的电压字段按不高于 60 V 量程预留，"
    "缩放 1 mV，标称值回填不影响帧结构。责任组：电气动力与底层控制组。",
    "T2 下位机通信路线。系统环境配置单元建议短期用 ros2_serial、长期迁移 micro-ROS。"
    "本版冻结上位机侧的串口帧协议，使其不因传输实现变化而变；micro-ROS 仅作长期"
    "评估项，本版不引入任何接口。责任组：电气动力与底层控制组、系统环境配置单元。",
    "T3 超声波阵列的数量与命名。阵列路数与安装方位未定，"
    "RangeArray.sensor_names 的命名与顺序未固定前不得发布该话题。"
    "责任组：电气动力与底层控制组。",
    "T4 臂端相机型号与手眼外参。机械臂视觉与抓取控制组倾向臂端用 RealSense D455、"
    "轮椅顶部用 OAK-D Pro。arm_camera 相关的 frame 名与话题本版先定，"
    "外参数值待手眼标定报告回填。责任组：机械臂视觉与抓取控制组。",
]:
    add_bullet(doc, t)

# ================================================================ 7 网络
add_heading(doc, "7 网络和时间同步标准", 1)

add_heading(doc, "7.1 以太网地址规划", 2)
add_caption(doc, "表 7-1  以太网地址规划")
add_table(doc, ["对象", "主机名", "建议地址", "说明"], [
    ("核心计算机", "wheelchair-core", "192.168.50.10",
     "ROS 2 核心节点与时间源；基线平台为香橙派 5（8 GB）"),
    ("激光雷达", "wheelchair-lidar", "192.168.50.20", "如设备只支持固定地址"),
    ("RGB-D 或视觉计算节点", "wheelchair-vision", "192.168.50.30", "可与核心计算机合并"),
    ("开发机", "wheelchair-dev-NN", "192.168.50.100-199", "优先 DHCP 保留"),
    ("网关或路由器", "wheelchair-router", "192.168.50.1", "仅提供局域网与受控外网"),
], [3.6, 4.0, 4.2, 5.4], font_size=8.4)
add_text(doc, "使用独立的 192.168.50.0/24 私有网段。若实验室网络策略不允许自建网段，"
              "由架构组统一替换地址表；任何成员不得单独修改设备地址。"
              "ROS 2 DDS 只在受控局域网中发现，不跨校园公共网络直接广播。")

add_heading(doc, "7.2 网络服务约定", 2)
for t in [
    "SSH 使用 TCP 22，仅允许密钥登录或实验室统一账号策略。",
    "云端大模型 API 使用 HTTPS TCP 443。API 密钥通过环境变量或密钥文件注入，不得提交 Git。",
    "DDS 使用默认 UDP 发现和数据端口。路由器、防火墙或 Docker 配置必须允许同一 "
    "ROS_DOMAIN_ID 内通信。",
    "相机和点云大流量数据不得通过不稳定无线网络承担安全控制；必要时在本机处理后"
    "发布降频结果。",
    "语音以离线识别为基线能力，不依赖网络；若启用云端意图解析，必须可整体关闭，"
    "关闭后语音功能完整可用。语音原始数据默认不出本机。",
]:
    add_bullet(doc, t)

add_heading(doc, "7.3 时间同步", 2)
add_numbered(doc, "实物系统以 wheelchair-core 为局域网时间参考，其他计算节点使用 chrony "
                  "或 systemd-timesyncd 同步。")
add_numbered(doc, "启动联调前，各计算节点时间偏差应小于 20 ms；视觉抓取和多传感器融合"
                  "建议小于 5 ms。")
add_numbered(doc, "MCU 上报 mcu_time_ms，由 serial_bridge 在接收时转换为 ROS 时间并监测漂移。"
                  "不得把 MCU 启动时间直接填入 ROS epoch 时间戳。")
add_numbered(doc, "仿真只使用 /clock；同一仿真进程中不得混用系统时间和仿真时间。")

# ================================================================ 8 Git
add_heading(doc, "8 Git 仓库与接口变更管理", 1)

add_heading(doc, "8.1 仓库目录", 2)
add_code(doc, [
    "wheelchair-project/",
    "  wheelchair_ws/src/wheelchair_interfaces/",
    "  wheelchair_ws/src/wheelchair_description/",
    "  wheelchair_ws/src/wheelchair_base/",
    "  wheelchair_ws/src/wheelchair_navigation/",
    "  wheelchair_ws/src/wheelchair_manipulation/",
    "  wheelchair_ws/src/wheelchair_voice/",
    "  wheelchair_ws/src/wheelchair_supervisor/",
    "  wheelchair_ws/src/wheelchair_simulation/",
    "  firmware/base_controller/",
    "  config/sim/   config/real/",
    "  docs/interfaces/   docs/tests/",
    "  tests/interface/   tools/",
], size=8.8)

add_heading(doc, "8.2 分支与提交规则", 2)
add_caption(doc, "表 8-1  分支与提交规则")
add_table(doc, ["分支或对象", "命名", "规则"], [
    ("主分支", "main", "只保存可演示、可回退的版本；禁止直接 push"),
    ("集成分支", "develop", "各组联调入口；通过构建和接口测试后合并"),
    ("功能分支", "feature/gN-issue-short-name", "N 为大组编号，一个分支对应一个任务"),
    ("修复分支", "fix/gN-issue-short-name", "修复缺陷，不夹带无关重构"),
    ("文档分支", "docs/short-name", "接口文档、标准与注册表变更"),
    ("发布分支", "release/vX.Y", "冻结接口，允许修复阻断问题"),
    ("标签", "vX.Y.Z", "阶段验收、仿真验收和实物验收必须打标签"),
    ("提交信息", "type(scope): summary", "例 feat(interface): add safety status message"),
], [2.6, 4.8, 9.8], font_size=8.4)

add_heading(doc, "8.3 Pull Request 门禁", 2)
for t in [
    "至少一名代码所有者和一名受影响大组接口负责人评审。",
    "colcon build 无错误，接口包生成成功，相关单元测试和接口测试通过。",
    "涉及 Topic、Service、Action、TF、串口或参数的改动必须同步更新 "
    "docs/interfaces/interface_registry.yaml。",
    "PR 描述列出变更原因、影响范围、兼容性、验证命令、测试结果和回退方法。",
    "不得提交 build、install、log、模型大文件、录制数据、API 密钥、密码或个人绝对路径。",
]:
    add_bullet(doc, t)

add_heading(doc, "8.4 接口变更流程", 2)
add_numbered(doc, "提出：在 Git Issue 创建 ICR 接口变更申请，说明现状、目标、受影响接口"
                  "和替代方案。")
add_numbered(doc, "评估：接口所有者、架构组和所有受影响组确认兼容性、安全影响与联调成本。")
add_numbered(doc, "批准：V1.x 兼容性新增由架构组批准；破坏性修改须经六大组接口负责人"
                  "共同确认。")
add_numbered(doc, "实现：先更新 wheelchair_interfaces 与接口注册表，再更新发布方和订阅方。")
add_numbered(doc, "验证：执行接口自动测试、仿真闭环测试和必要的实物低速测试。")
add_numbered(doc, "发布：更新版本记录并打标签。废弃接口至少保留一个阶段，"
                  "运行时输出 deprecation 警告。")

add_heading(doc, "8.5 版本规则", 2)
add_caption(doc, "表 8-2  版本规则")
add_table(doc, ["变更", "版本示例", "处理方式"], [
    ("修正文档错字、实现缺陷，不改变接口", "1.0.0 -> 1.0.1", "补丁版本"),
    ("新增兼容 Topic、可选字段或诊断项", "1.0 -> 1.1", "次版本，旧调用仍可工作"),
    ("修改类型、字段顺序、单位、语义或删除接口", "1.x -> 2.0", "主版本，必须迁移评审"),
], [5.2, 3.2, 8.8], font_size=8.4)
add_note(doc, "本版的版本号重新起算，与已归档的内部草案序号无继承关系。"
              "本版相对草案同时包含新增兼容接口与文档结构性修正，"
              "按上表应分别对应次版本与补丁版本；因草案从未正式发布，"
              "故合并为一次正式首发，版本号取 1.0。", kind="plain")

# ---------------------------------------------------------------- p_g_end.py
# ================================================================ 9 验收
add_heading(doc, "9 联调验收与问题处置", 1)

add_heading(doc, "9.1 第一版接口验收", 2)
add_caption(doc, "表 9-1  第一版接口验收")
add_table(doc, ["编号", "验收项", "通过条件", "证据"], [
    ("IF-01", "接口包构建", "wheelchair_interfaces 在干净工作空间 colcon build 成功",
     "构建日志"),
    ("IF-02", "Topic 名称与类型", "ros2 topic list 与 ros2 topic type 与表 4-3 一致，"
                                  "无重复私有替代接口", "命令输出"),
    ("IF-03", "QoS 兼容", "所有订阅连接成功，无 QoS incompatibility 警告；"
                           "重点核查 /tf 的 TF 档", "节点日志"),
    ("IF-04", "TF 完整性", "TF 单树连通、唯一发布、时间戳有效", "view_frames 与 tf2_echo"),
    ("IF-05", "串口正常帧", "连续 10000 帧无解析错误，字段缩放一致", "自动测试报告"),
    ("IF-06", "串口异常帧", "CRC、超长和截断帧被丢弃且不执行", "故障注入日志"),
    ("IF-07", "通信超时", "200 ms 内速度归零，1000 ms 内进入通信故障", "波形或日志"),
    ("IF-08", "急停链路", "物理急停独立生效，ROS 状态正确锁存", "测试记录"),
    ("IF-09", "速度仲裁", "多速度源竞争时优先级和超时符合 4.5 节", "rosbag 与曲线"),
    ("IF-10", "仿真实物一致", "sim 和 real 配置仅实现不同，公开接口相同", "接口 diff"),
], [1.3, 3.0, 8.4, 4.5], font_size=8.0)

add_heading(doc, "9.2 问题等级", 2)
add_caption(doc, "表 9-2  问题等级")
add_table(doc, ["等级", "定义", "处置时限", "示例"], [
    ("P0", "危及人身或可能造成执行机构失控", "立即停止测试", "急停无效、失联仍运动"),
    ("P1", "阻断多组联调或造成主要功能不可用", "当日给出负责人和方案",
     "TF 断树、接口类型不一致"),
    ("P2", "功能降级但有临时绕行方案", "下个集成节点前解决", "传感器频率不足、诊断缺失"),
    ("P3", "文档、命名或体验问题", "纳入迭代", "说明不完整、日志格式不统一"),
], [1.3, 5.2, 3.4, 7.3], font_size=8.2)

add_heading(doc, "9.3 故障现场保留", 2)
for t in [
    "记录版本标签、提交哈希、运行模式、参数文件、硬件连接、发生时间和复现步骤。",
    "保存 /diagnostics、/wheelchair/safety/status、/tf、/cmd_vel、/wheelchair/base/odom "
    "等关键数据的 rosbag。",
    "保存 serial_bridge 原始帧十六进制日志，但不得在正常运行中无限增长。",
    "安全故障复现必须使用架空轮、仿真或沙袋，未通过安全门禁前禁止人员乘坐。",
]:
    add_bullet(doc, t)

# ================================================================ 10 AI 记录
add_heading(doc, "10 AI 工具应用记录", 1)
add_text(doc, "依据课程任务书的学术诚信要求，本项目在代码、故障排查、数学推导和文档撰写中"
              "使用 AI 工具时，必须区分 AI 建议与团队最终工程决策。"
              "AI 输出不得未经验证直接进入安全关键控制链路；"
              "接口所有者仍对定义、实现、测试和安全后果负责。")
add_caption(doc, "表 10-1  本文档 AI 工具应用记录")
add_table(doc, ["应用环节", "AI 辅助内容", "团队自主审查与重构", "责任人"], [
    ("文档框架", "根据课程任务形成接口规范章节结构",
     "对照任务书确认适用范围、交付要求和安全红线", "第六大组 · 架构与接口规范单元"),
    ("跨组对表", "辅助比对五组方案汇报与内部草案，提取冲突与缺口清单",
     "逐条复核两组原话与幻灯片出处，由本单元裁定可定项、"
     "把依赖实测的项标为 TBD，不替其他组做电气与机械设计决策",
     "第六大组 · 架构与接口规范单元"),
    ("ROS 2 接口草案", "辅助整理 Topic、Service、Action、QoS 和 TF 命名建议",
     "结合项目模块划分统一所有者、频率、坐标系和安全边界；"
     "新增条目逐条对照五组汇报的实际选型", "接口负责人待填写"),
    ("串口协议草案", "辅助设计帧结构、CRC、ACK、错误码与超时策略；"
                     "辅助代拟 9 条缺失消息的载荷表",
     "电气动力与底层控制组需在 MCU 上实测资源占用、字节序、错误恢复和电机停止时延；"
     "代拟载荷表须逐条确认后方可冻结", "电气接口负责人待填写"),
    ("表号重编", "辅助按章节重编 39 张表的编号并补全题注",
     "以脚本正则校验全文表号引用均可解析到题注，另出表号映射表备查",
     "第六大组 · 架构与接口规范单元"),
    ("文档排版", "辅助生成表格、标题层级和验收清单",
     "逐页检查内容完整性和可读性，含渲染成 PDF 后的目视复核",
     "第六大组 · 架构与接口规范单元"),
], [2.2, 4.4, 7.2, 3.4], font_size=7.6)

add_heading(doc, "10.1 后续 AI 使用登记要求", 2)
for t in [
    "每次提交 AI 生成或显著修改的代码时，在 PR 中填写工具名称、输入目的、采用内容、"
    "人工修改和验证结果。",
    "涉及速度、急停、推杆、姿态保护、路径规划或机械臂运动的 AI 建议，"
    "必须通过仿真、单元测试和安全工况测试后使用。",
    "不得向外部 AI 服务提交 API 密钥、密码、个人信息、校园内网地址或未经许可的敏感数据。",
    "最终工程文档应保留本章节，并由各模块负责人补充真实使用记录，不得仅保留模板文字。",
]:
    add_bullet(doc, t)

# ---------------------------------------------------------------- p_h_appendix.py
# ================================================================ 附录 A
add_heading(doc, "附录 A 自定义消息与动作定义", 1)
add_text(doc, "以下定义为第一版接口草案。实际文件应放置于 wheelchair_interfaces 包，"
              "由接口包单独版本管理，不得依赖任何业务实现包。"
              "字段不得在未发起接口变更申请（ICR）的情况下改序、改名或改单位。"
              "各定义中常量声明一律前置，符合 ROS 2 对 .msg 与 .action 的语法要求。")
add_caption(doc, "表 A-1  自定义消息与动作总览")
add_table(doc, ["类型", "名称", "使用者", "载体接口"], [
    ("msg", "SafetyStatus", "安全监督节点、状态机、监控节点",
     "/wheelchair/safety/status（STATE 档）"),
    ("msg", "McuState", "serial_bridge、监控与测试节点",
     "/wheelchair/base/mcu_state（STATE 档）"),
    ("msg", "RangeArray", "serial_bridge、安全与避障节点",
     "/wheelchair/ultrasonic/ranges（SENSOR 档）"),
    ("msg", "VoiceIntent", "意图解析节点、状态机",
     "/wheelchair/voice/intent（EVENT 档）"),
    ("msg", "StandState", "推杆控制节点、状态机与安全节点",
     "/wheelchair/stand/state（STATE 档）"),
    ("msg", "SystemMode", "状态机、全系统订阅",
     "/wheelchair/system/mode（STATE 档）"),
    ("action", "GraspObject", "抓取执行节点（服务端）、状态机（客户端）",
     "/wheelchair/arm/grasp_object"),
    ("action", "ChangePosture", "推杆控制节点（服务端）、状态机（客户端）",
     "/wheelchair/stand/change_posture"),
], [1.5, 3.0, 6.6, 6.1], font_size=8.0)

add_heading(doc, "A.1 SafetyStatus.msg", 2)
add_code(doc, [
    "std_msgs/Header header",
    "uint8 ESTOP_RELEASED=0",
    "uint8 ESTOP_PHYSICAL=1",
    "uint8 ESTOP_SOFTWARE=2",
    "uint8 ESTOP_BOTH=3",
    "uint8 estop_state",
    "bool drive_enabled",
    "bool posture_enabled",
    "uint32 fault_bits",
    "# fault_bits 位定义统一见表 6-7",
    "float32 roll_rad",
    "float32 pitch_rad",
    "float32 min_obstacle_distance_m",
    "string summary",
], size=8.8)

add_heading(doc, "A.2 McuState.msg", 2)
add_code(doc, [
    "std_msgs/Header header",
    "string firmware_version",
    "uint32 uptime_ms",
    "uint32 valid_rx_frames",
    "uint32 crc_error_frames",
    "uint32 timeout_count",
    "uint16 last_rx_seq",
    "uint8 controller_state",
], size=8.8)

add_heading(doc, "A.3 RangeArray.msg", 2)
add_code(doc, [
    "std_msgs/Header header",
    "string[] sensor_names",
    "float32[] ranges_m",
    "float32 min_range_m",
    "float32 max_range_m",
    "# ranges_m / min_range_m / max_range_m 允许用 NaN 表示距离未知",
    "# 串口哨兵 0xFFFF 须在 serial_bridge 中转为 NaN，不得直接缩放",
    "# sensor_names 的命名与顺序未固定前不得发布该话题，见 6.8 节 T3",
], size=8.8)

add_heading(doc, "A.4 VoiceIntent.msg", 2)
add_code(doc, [
    "std_msgs/Header header",
    "string intent",
    "# intent 取值见附录 C 表 C-1",
    "string[] parameter_names",
    "string[] parameter_values",
    "float32 confidence",
    "string original_text",
    "string request_id",
], size=8.8)

add_heading(doc, "A.5 StandState.msg", 2)
add_code(doc, [
    "std_msgs/Header header",
    "uint8 UNKNOWN=0",
    "uint8 SEATED=1",
    "uint8 MOVING_TO_STAND=2",
    "uint8 STANDING=3",
    "uint8 MOVING_TO_SEAT=4",
    "uint8 FAULT=5",
    "uint8 state",
    "float32 position_ratio",
    "bool lower_limit",
    "bool upper_limit",
    "uint32 fault_bits",
    "# 复用表 6-7 位定义；本消息仅 bit7 ACTUATOR_LIMIT、bit8 SENSOR_INVALID 适用",
], size=8.8)

add_heading(doc, "A.6 SystemMode.msg", 2)
add_code(doc, [
    "std_msgs/Header header",
    "uint8 INIT=0",
    "uint8 SIMULATION=1",
    "uint8 MANUAL=2",
    "uint8 AUTONOMOUS=3",
    "uint8 STANDING=4",
    "uint8 FAULT=5",
    "uint8 ESTOP=6",
    "uint8 mode",
    "string reason",
], size=8.8)

add_heading(doc, "A.7 GraspObject.action", 2)
add_code(doc, [
    "# Goal",
    "string object_id",
    "geometry_msgs/PoseStamped target_pose",
    "float32 approach_distance_m",
    "---",
    "# Result",
    "bool success",
    "uint16 error_code",
    "string message",
    "---",
    "# Feedback",
    "uint8 stage",
    "float32 progress",
    "string message",
], size=8.8)

add_heading(doc, "A.8 ChangePosture.action", 2)
add_code(doc, [
    "# Goal",
    "uint8 HOLD=0",
    "uint8 SEAT=1",
    "uint8 STAND=2",
    "uint8 target",
    "float32 speed_ratio",
    "---",
    "# Result",
    "bool success",
    "uint16 error_code",
    "string message",
    "---",
    "# Feedback",
    "uint8 current_state",
    "float32 position_ratio",
], size=8.8)
add_note(doc, "本附录 6 个消息与 2 个动作已按上述定义写入 wheelchair_interfaces 包，"
              "但该包尚未在真实 ROS 2 环境完成独立构建，"
              "状态一律记为「待验证」，不得记为已完成。")

# ================================================================ 附录 B
add_heading(doc, "附录 B 第一版交付检查表", 1)
add_caption(doc, "表 B-1  第一版交付检查表")
add_table(doc, ["状态", "交付项", "责任人", "完成标准"], [
    ("待确认", "六大组接口负责人名单", "第六大组 · 架构与接口规范单元",
     "每组至少指定 1 名固定接口联系人"),
    ("已完成（评审意见已成文并由 Git 留痕）", "IW-IF-STD-001 评审",
     "六大组接口负责人", "完成评审意见并签字或在 Git 留痕"),
    ("已完成（main 与 develop 均受保护，develop 经 PR 合并）",
     "wheelchair-project Git 仓库", "仓库管理员", "main 受保护，develop 可通过 PR 合并"),
    ("待验证（6 个 msg 与 2 个 action 已定义；Service 复用 std_srvs，"
     "其中 /arm_controller/follow_joint_trajectory 为新增；独立构建待验证）",
     "wheelchair_interfaces ROS 2 包", "接口开发负责人", "msg srv action 可独立构建"),
    ("已完成（Topic／Service／Action／TF／串口全量条目已登记，含本版新增 11 项）",
     "interface_registry.yaml", "接口文档负责人",
     "登记名称、类型、所有者、频率、QoS 和版本"),
    ("已完成（表 4-3、表 4-4、表 5-1 已补齐所有者，ICR-002 闭环）",
     "公开接口所有者归属", "第六大组 · 架构与接口规范单元",
     "每个公开接口有唯一所有者且已登记"),
    ("待创建", "串口编解码测试", "电气接口负责人",
     "含正常帧、CRC 错误、截断、超长和重复序号"),
    ("待创建（URDF／XACRO 尚未提交至 wheelchair_description）", "TF 树初版",
     "机械与导航接口负责人", "URDF 在 RViz 2 加载且主链连通"),
    ("待验证（config/sim 与 config/real 已建；统一镜像或虚拟机交付物尚无）",
     "统一开发环境", "各组接口负责人", "Ubuntu 22.04、ROS 2 与 ROS_DOMAIN_ID 一致"),
    ("已完成（本版第 10 章已建立 AI 工具应用记录）", "AI 工具应用记录",
     "文档负责人", "记录 AI 生成内容与团队自主审查、调试和重构内容"),
], [4.6, 3.4, 3.4, 5.8], font_size=7.6)

add_heading(doc, "B.1 第一版发布会议建议议程", 2)
for t in [
    "确认六大组接口联系人和公开接口所有者。",
    "逐项审议表 4-3 Topic、表 4-4 Service 与 Action、表 5-1 TF 定义。",
    "由电气动力与底层控制组确认串口字段是否满足固件资源和传感器接线方案，"
    "并确认表 6-8 至表 6-17 代拟载荷表。",
    "由自动导航与 SLAM 算法组确认 frame 名称与传感器频率；"
    "由机械臂视觉与抓取控制组确认 arm_camera 相关 frame 与手眼外参回填时间。",
    "由语音交互与多模态控制组确认附录 C 语音意图枚举表。",
    "确定第一版生效时间、下次接口冻结时间和首轮仿真联调日期。",
]:
    add_numbered(doc, t)

# ================================================================ 附录 C
add_heading(doc, "附录 C 语音意图枚举表", 1)
add_text(doc, "本附录回应原 ICR-002 与语音交互与多模态控制组的指令词方案："
              "原标准把语音意图完全交给 /wheelchair/voice/intent 的字符串字段，"
              "既没有枚举约定，也没有规定与安全状态的联动，"
              "导致「前进」「停止」「起立」「抓取」四类指令无法跨组验证。"
              "本版以一版枚举冻结取值集合、目标接口、优先级与安全关键属性。")
add_caption(doc, "表 C-1  语音意图枚举")
add_table(doc, ["intent 取值", "中文示例", "目标接口", "优先级", "安全关键"], [
    ("STOP", "停止、别动、急停", "/wheelchair/safety/set_soft_estop 或直接置零速度",
     "最高（等同人工接管）", "是"),
    ("CANCEL", "取消、算了", "取消当前 Action 目标或导航目标", "最高", "是"),
    ("MOVE_FORWARD", "前进、往前走", "经速度复用器发布不超过 2 s 的限时低速 Twist",
     "低于手柄人工接管", "是"),
    ("MOVE_BACKWARD", "后退、往后", "同上", "低于手柄人工接管", "是"),
    ("TURN_LEFT", "左转、往左", "同上", "低于手柄人工接管", "是"),
    ("TURN_RIGHT", "右转、往右", "同上", "低于手柄人工接管", "是"),
    ("STAND_UP", "起立、站起来", "/wheelchair/stand/change_posture（target=STAND）",
     "低于手柄人工接管", "是"),
    ("SIT_DOWN", "坐下、放下", "/wheelchair/stand/change_posture（target=SEAT）",
     "低于手柄人工接管", "是"),
    ("GRASP", "抓取、拿起来", "/wheelchair/arm/grasp_object", "低于手柄人工接管", "是"),
    ("RELEASE", "松开、放下东西", "/wheelchair/arm/grasp_object 的释放分支",
     "低于手柄人工接管", "是"),
    ("NAVIGATE_TO", "去、到某地", "/navigate_to_pose", "低于手柄人工接管", "否"),
], [2.9, 2.6, 5.4, 3.0, 1.6], font_size=7.6)
add_text(doc, "约束：语音优先级低于手柄人工接管；急停锁存或故障锁存期间，"
              "除 STOP 与 CANCEL 外的全部意图必须被拒绝并回报拒绝原因。"
              "MOVE_FORWARD、MOVE_BACKWARD、TURN_LEFT、TURN_RIGHT 不得持续发布 Twist，"
              "必须由意图解析节点翻译为定距或限时的低速动作，"
              "经速度复用器以不超过 2 s 的时效发布，见 4.5 节第 7 条。"
              "NAVIGATE_TO 的目标点须转化为 Nav2 目标，语音节点不得直接发布路径。")
add_note(doc, "本表为本单元代拟的第一版枚举，需语音交互与多模态控制组会签确认。"
              "确认后 intent 字段的取值集合即为冻结接口，"
              "新增意图须走接口变更流程。", kind="plain")

# ================================================================ 附录 D
add_heading(doc, "附录 D 评审签署页", 1)
add_text(doc, "本文档的接口定义、表号体系与本版变更清单需经六大组接口负责人评审。"
              "评审结论分为「同意」「有条件同意」和「退回」三类；"
              "「有条件同意」须在备注中写明附条件项与关闭时间。"
              "签署完成后，本文档状态由「正式发布稿」转为「已发布」，"
              "并作为后续接口变更的兼容性判定基线。")
add_caption(doc, "表 D-1  评审签署表")
add_table(doc, ["大组", "接口负责人", "评审结论", "日期", "备注"], [
    ("机械结构与物理装配组", "", "同意  有条件同意  退回", "", ""),
    ("电气动力与底层控制组", "", "同意  有条件同意  退回", "", ""),
    ("自动导航与 SLAM 算法组", "", "同意  有条件同意  退回", "", ""),
    ("机械臂视觉与抓取控制组", "", "同意  有条件同意  退回", "", ""),
    ("语音交互与多模态控制组", "", "同意  有条件同意  退回", "", ""),
    ("系统集成测试与项目管理组", "", "同意  有条件同意  退回", "", ""),
], [4.4, 2.6, 4.4, 2.2, 3.6], font_size=8.0)
add_text(doc, "编制单位：第六大组 · 架构与接口规范单元　　"
              "文档编号：IW-IF-STD-001　　版本：V1.0　　发布日期：第四周")

doc.save(OUT)
print("saved ->", OUT)
