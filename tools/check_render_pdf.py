# -*- coding: utf-8 -*-
"""
渲染检查：对 Word / PowerPoint 导出的 PDF 做版面检查（自检清单第 3 节）
第六大组 · 架构与接口规范单元

用法（在仓库根目录执行，先用 render_office_pdf.ps1 导出 PDF）：
    powershell -NoProfile -ExecutionPolicy Bypass -File tools/render_office_pdf.ps1 \
        -InputPath docs/interfaces/<标准正文>.docx -OutputPdf <临时目录>/std.pdf
    python tools/check_render_pdf.py <临时目录>/std.pdf

检查项（只读）：
  1. 压页脚：文本块底边进入页面最下方的安全区（默认 20 pt）。
  2. 标识符断行：上下相接、左端对齐的两行，上一行末尾与下一行开头拼起来
     恰好是全文出现过的拉丁标识符，判为该标识符被换行切断。
     处理办法是调宽所在列，不要缩小字号。

退出码：0 = 无压页脚；1 = 存在压页脚。标识符断行只报告，不影响退出码——
少量断在下划线边界或长标识符尾部的断行可以接受，由人判断。

依赖：pip install pymupdf
"""
import argparse
import collections
import re
import sys

import pymupdf

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_/]{3,}")


def find_overflow(doc, margin):
    """返回 [(页码, 最低文本底边, 页高)]，只列越过安全区的页。"""
    hits = []
    for pno, page in enumerate(doc, 1):
        bottom = max((b[3] for b in page.get_text("blocks")), default=0.0)
        if bottom > page.rect.height - margin:
            hits.append((pno, bottom, page.rect.height))
    return hits


def find_broken_identifiers(doc):
    """返回 [(页码, 上一行末尾, 下一行开头, 拼合后的标识符)]。"""
    vocab = collections.Counter()
    for page in doc:
        vocab.update(IDENT.findall(page.get_text()))

    hits = []
    for pno, page in enumerate(doc, 1):
        lines = []
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                text = "".join(span["text"] for span in line["spans"])
                if text.strip():
                    lines.append((line["bbox"], text))
        lines.sort(key=lambda item: (round(item[0][1], 1), round(item[0][0], 1)))

        for i, (upper_box, upper_text) in enumerate(lines):
            lower = next(
                (text for j, (box, text) in enumerate(lines)
                 if j != i
                 and -1.0 <= box[1] - upper_box[3] <= 3.0    # 上下相接
                 and abs(box[0] - upper_box[0]) <= 4.0),     # 左端对齐（同一列）
                None)
            if lower is None:
                continue
            tail = re.search(r"([A-Za-z0-9_]{2,})$", upper_text.rstrip())
            head = re.match(r"([A-Za-z0-9_]{2,})", lower.lstrip())
            if tail and head and vocab[tail.group(1) + head.group(1)]:
                hits.append((pno, tail.group(1), head.group(1),
                             tail.group(1) + head.group(1)))
    return hits


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="对导出的 PDF 做压页脚与标识符断行检查")
    parser.add_argument("pdf", help="render_office_pdf.ps1 导出的 PDF")
    parser.add_argument("--margin", type=float, default=20.0,
                        help="页面底部安全区，单位 pt（默认 20）")
    args = parser.parse_args()

    doc = pymupdf.open(args.pdf)
    print("PDF: %s（%d 页）" % (args.pdf, doc.page_count))

    print("\n[1] 压页脚（底部安全区 %.0f pt）" % args.margin)
    overflow = find_overflow(doc, args.margin)
    for pno, bottom, height in overflow:
        print("  [x] 第 %d 页：文本底边 %.1f pt，页高 %.1f pt" % (pno, bottom, height))
    if not overflow:
        print("  [v] 全部 %d 页的文本都在安全区以内" % doc.page_count)

    print("\n[2] 标识符断行")
    broken = find_broken_identifiers(doc)
    for pno, tail, head, joined in broken:
        print("  [!] 第 %d 页：%s | %s  =>  %s" % (pno, tail, head, joined))
    print("  共 %d 处（只报告，不影响退出码）" % len(broken))

    print()
    if overflow:
        print("存在压页脚，请调整版面后重新导出。")
        return 1
    print("渲染检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
