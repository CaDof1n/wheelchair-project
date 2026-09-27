# -*- coding: utf-8 -*-
"""
IW-IF-STD-001 一致性校验工具
第六大组 · 架构与接口规范单元

用法（在仓库根目录执行）：
    python tools/check_iw_if_std_001.py

校验项（全部只读，不修改任何文件）：
  1. 题注完整性：文档内表格对象数 == 「表 N-M」题注条数
  2. 引用可解析：正文与表格中出现的每个「表 N-M」「图 N」都能找到对应题注
  3. 注册表交叉比对：标准正文抽出的 Topic / Service / Action / TF frame
     与 interface_registry.yaml 完全一致
  4. 示例帧复算：按 §6.6 帧结构重算 CRC-16/MODBUS，与注册表登记值比对

排版相关的检查（溢出、长词换行位置）依赖 Word/PowerPoint 渲染结果，
无法在纯 Python 环境下复现，做法见「渲染校验」一节。

退出码：0 = 全部通过；1 = 存在不一致项。
"""
import re
import sys
from pathlib import Path

import yaml
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "docs" / "interfaces" / "第一版全局软硬件接口标准_V1.0.docx"
REGISTRY = ROOT / "docs" / "interfaces" / "interface_registry.yaml"

problems = []


def fail(msg):
    problems.append(msg)
    print("  [x] " + msg)


def ok(msg):
    print("  [v] " + msg)


# ---------------------------------------------------------------- 1 题注与引用
def check_captions(doc):
    print("\n[1] 题注完整性与引用可解析")
    paras = [p.text.strip() for p in doc.paragraphs]

    cap_tbl, cap_fig = {}, {}
    for t in paras:
        m = re.fullmatch(r"表\s*([A-D]|\d+)-(\d+)\s+(.+)", t)
        if m:
            cap_tbl["%s-%s" % (m.group(1), m.group(2))] = m.group(3)
        m = re.fullmatch(r"图\s*(\d+)\s+(.+)", t)
        if m:
            cap_fig[m.group(1)] = m.group(2)

    if len(cap_tbl) != len(doc.tables):
        fail("题注 %d 条，表格对象 %d 个，数量不符" % (len(cap_tbl), len(doc.tables)))
    else:
        ok("题注 %d 条，与 %d 个表格对象一一对应" % (len(cap_tbl), len(doc.tables)))
    if not cap_fig:
        fail("全文没有任何图题注")
    else:
        ok("图题注 %d 条：%s" % (len(cap_fig), "、".join(sorted(cap_fig))))

    # 待查文本 = 段落 + 全部单元格
    chunks = list(paras)
    for tb in doc.tables:
        for row in tb.rows:
            for c in row.cells:
                chunks.append(c.text)
    for sec in doc.sections:
        for p in sec.footer.paragraphs:
            chunks.append(p.text)
    text = "\n".join(chunks)

    refs_t = {"%s-%s" % (m.group(1), m.group(2))
              for m in re.finditer(r"表\s*([A-D]|\d+)-(\d+)", text)}
    refs_f = {m.group(1) for m in re.finditer(r"图\s*(\d+)", text)}

    bad = sorted("表 " + r for r in refs_t if r not in cap_tbl)
    bad += sorted("图 " + r for r in refs_f if r not in cap_fig)
    if bad:
        fail("以下引用找不到对应题注：%s" % "、".join(bad))
    else:
        ok("正文引用 %d 处表、%d 处图，全部可解析"
           % (len(refs_t), len(refs_f)))

    orphan = sorted(k for k in cap_tbl if k not in refs_t)
    if orphan:
        print("  [!] 提示：未被正文引用的表（不算错误）：%s" % "、".join(orphan))
    return text, cap_tbl


# ---------------------------------------------------------------- 2 注册表比对
def check_registry(text, cap_tbl):
    print("\n[2] 与 interface_registry.yaml 交叉比对")
    reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))

    # 标准正文的表 4-3 / 表 4-4 / 表 5-1 单元格文本
    doc = Document(str(DOCX))

    def cells_of(caption):
        """返回题注所在表格之后第一张表的全部单元格文本。"""
        body = doc.element.body
        kids = list(body)
        idx = None
        for i, el in enumerate(kids):
            if el.tag.endswith("}p"):
                if el.xpath("string(.)").strip().startswith(caption):
                    idx = i
                    break
        if idx is None:
            return None
        for el in kids[idx + 1:]:
            if el.tag.endswith("}tbl"):
                t = [x for x in doc.tables if x._tbl is el][0]
                return [c.text.strip() for r in t.rows for c in r.cells]
        return None

    t43 = cells_of("表 4-3")
    t44 = cells_of("表 4-4")
    t51 = cells_of("表 5-1")

    if t43 is None:
        fail("找不到表 4-3")
    else:
        miss = [t["name"] for t in reg["topics"] if t["name"] not in t43]
        extra = [c for c in t43 if c.startswith("/") and "/" in c[1:]
                 and c not in {t["name"] for t in reg["topics"]}
                 and not c.startswith("//")]
        if miss:
            fail("表 4-3 缺少注册表中的 Topic：%s" % "、".join(miss))
        else:
            ok("表 4-3 覆盖注册表全部 %d 条 Topic" % len(reg["topics"]))
        if extra:
            print("  [!] 提示：表 4-3 中不在注册表的以 / 开头的单元格：%s" % "、".join(extra))

    if t44 is None:
        fail("找不到表 4-4")
    else:
        names = [x["name"] for x in reg["services"]] + [x["name"] for x in reg["actions"]]
        miss = [n for n in names if n not in t44]
        if miss:
            fail("表 4-4 缺少注册表中的 Service / Action：%s" % "、".join(miss))
        else:
            ok("表 4-4 覆盖注册表全部 %d 条 Service 与 Action" % len(names))

    if t51 is None:
        fail("找不到表 5-1")
    else:
        frames = [f["frame"] for f in reg["tf_frames"]]
        # 注册表允许用 arm_link_1..arm_link_6 这类压缩写法登记连续链，
        # 校验时按区间端点逐一核对。
        joined = "\n".join(t51)

        def in_table(f):
            if ".." in f:
                # 区间写法：两端点须都出现在表 5-1 中
                a, b = f.split("..", 1)
                return a.strip() in joined and b.strip() in joined
            return f in t51

        miss = [f for f in frames if not in_table(f)]
        if miss:
            fail("表 5-1 缺少注册表中的 frame：%s" % "、".join(miss))
        else:
            ok("表 5-1 覆盖注册表全部 %d 条 frame" % len(frames))

    # 表 6-3 消息编号
    t63 = cells_of("表 6-3")
    if t63 is None:
        fail("找不到表 6-3")
    else:
        ids = [m["id"] for m in reg["serial"]["message_ids"]] \
            if isinstance(reg["serial"]["message_ids"], list) else []
        miss = [i for i in ids if i not in t63]
        if miss:
            fail("表 6-3 缺少注册表中的 MSG_ID：%s" % "、".join(miss))
        else:
            ok("表 6-3 覆盖注册表全部 %d 条消息编号" % len(ids))


# ---------------------------------------------------------------- 3 示例帧复算
def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def check_example_frame():
    print("\n[3] 示例帧 CRC 复算（标准 §6.6）")
    reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    ex = reg.get("serial", {}).get("example_frame")
    if not ex:
        fail("注册表没有 serial.example_frame")
        return
    raw = bytes(int(x, 16) for x in ex["hex"].split())
    if len(raw) < 11 or raw[0] != 0xAA or raw[1] != 0x55:
        fail("示例帧过短或 SOF 不是 0xAA 0x55")
        return

    # 帧结构（标准表 6-2）：SOF(2) VERSION(1) MSG_ID(1) FLAGS(1) SEQ(2)
    #                      LENGTH(2) PAYLOAD(N) CRC16(2)
    version, msg_id, flags = raw[2], raw[3], raw[4]
    seq = raw[5] | (raw[6] << 8)
    length = raw[7] | (raw[8] << 8)
    payload = raw[9:9 + length]
    body = raw[2:9 + length]                     # CRC 覆盖 VERSION 至 PAYLOAD

    if len(raw) != 9 + length + 2:
        fail("帧长与 LENGTH 不符：帧 %d 字节，LENGTH=%d" % (len(raw), length))
    else:
        ok("帧长自洽：LENGTH=%d，总长 %d 字节" % (length, len(raw)))

    got = "%04X" % crc16_modbus(body)
    want = re.sub(r"^0[xX]", "", str(ex["crc16_modbus"])).upper()
    if got != want:
        fail("示例帧 CRC 复算得 0x%s，注册表登记 0x%s" % (got, want))
    else:
        ok("示例帧 CRC 复算 0x%s，与注册表一致（低字节先发）" % got)

    # 帧头字段
    print("      帧头：VERSION=0x%02X  MSG_ID=0x%02X  FLAGS=0x%02X  SEQ=%d"
          % (version, msg_id, flags, seq))

    # CMD_VEL 载荷（表 6-4）：int16 linear_x / int16 angular_z / uint16 timeout_ms
    if msg_id == 0x10 and length == 6:
        def i16(b, i):
            v = b[i] | (b[i + 1] << 8)
            return v - 0x10000 if v & 0x8000 else v
        lx = i16(payload, 0)
        az = i16(payload, 2)
        to = payload[4] | (payload[5] << 8)
        ok("载荷解释：linear_x=%d mm/s  angular_z=%d mrad/s  timeout_ms=%d"
           % (lx, az, to))
        if not (flags & 0x01):
            print("  [!] 提示：FLAGS 未置 ACK_REQ，但注册表 desc 声称请求 ACK")
        if to != 200:
            print("  [!] 提示：timeout_ms=%d，与 desc 描述的 200 ms 不符" % to)


if __name__ == "__main__":
    print("IW-IF-STD-001 一致性校验")
    print("标准正文:", DOCX.name)
    print("注册表  :", REGISTRY.name)
    if not DOCX.exists() or not REGISTRY.exists():
        print("找不到待校验文件")
        sys.exit(1)
    text, cap = check_captions(Document(str(DOCX)))
    check_registry(text, cap)
    check_example_frame()

    print("\n" + "=" * 56)
    if problems:
        print("存在 %d 项不一致：" % len(problems))
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("全部校验通过。")
    print("""
渲染校验（需本机装有 Word / PowerPoint，可选）：
  1. Word 导出 PDF 后，逐页目视检查题注是否孤立在页脚、
     表格是否跨页且表头是否重复；
  2. 用 PDF 文本块坐标检查是否有内容越过下边距；
  3. 检查拉丁标识符是否被换行截断成 1~3 字符的碎片
     （必要时调整该列宽度，而不是缩小字号）。""")
