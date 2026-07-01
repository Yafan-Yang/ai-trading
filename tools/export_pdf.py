"""ai-trading 工具：Markdown 研报导出 PDF（weasyprint，处理中文字体）。

用法:
    python export_pdf.py <input.md> [-o output.pdf]

纯 pip 依赖（weasyprint + markdown），无需 pandoc / wkhtmltopdf。
中文字体依赖系统已安装的 CJK 字体（macOS 自带 PingFang SC / STHeiti）。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

CSS = """
@page { size: A4; margin: 1.8cm 1.6cm; }
* { font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
    "Noto Sans CJK SC", "STHeiti", "SimHei", Arial, sans-serif; }
body { font-size: 11pt; line-height: 1.6; color: #1a1a1a; }
h1 { font-size: 20pt; border-bottom: 2px solid #c0392b; padding-bottom: 6px; }
h2 { font-size: 15pt; color: #c0392b; margin-top: 18px;
     border-left: 4px solid #c0392b; padding-left: 8px; }
h3 { font-size: 13pt; color: #2c3e50; margin-top: 14px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0;
        page-break-inside: avoid; }
th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 10pt; }
th { background: #f5eaea; }
tr:nth-child(even) { background: #fafafa; }
blockquote { color: #666; border-left: 3px solid #ddd; padding-left: 12px;
             font-size: 9.5pt; }
code { background: #f4f4f4; padding: 1px 4px; border-radius: 3px; }
"""


def convert(md_path: Path, out_path: Path) -> None:
    import markdown as md
    from weasyprint import CSS as WCSS
    from weasyprint import HTML

    text = md_path.read_text(encoding="utf-8")
    html_body = md.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    html = (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            f"</head><body>{html_body}</body></html>")
    HTML(string=html).write_pdf(str(out_path), stylesheets=[WCSS(string=CSS)])


def main() -> int:
    ap = argparse.ArgumentParser(description="Markdown -> PDF (中文)")
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()

    md_path = Path(args.input)
    if not md_path.exists():
        print(f"❌ 找不到文件: {md_path}")
        return 1
    out_path = Path(args.output) if args.output else md_path.with_suffix(".pdf")
    try:
        convert(md_path, out_path)
    except OSError as e:
        if "pango" in str(e).lower() or "cairo" in str(e).lower():
            print("❌ 缺少系统图形库（weasyprint 依赖）。macOS 请先执行:\n"
                  "   brew install pango gdk-pixbuf libffi\n"
                  f"原始错误: {e}")
        else:
            print(f"❌ 导出失败: {e}")
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"❌ 导出失败: {e}")
        return 1
    print(f"✅ 已导出 PDF: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
