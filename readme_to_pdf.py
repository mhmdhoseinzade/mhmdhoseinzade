#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


DEFAULT_CSS = """
@page { size: A4; margin: 18mm 16mm; }
html, body { font-size: 11.5pt; line-height: 1.45; }
body { font-family: DejaVu Sans, Arial, Helvetica, sans-serif; color: #111; direction: ltr; text-align: left; }
.ltr { direction: ltr; text-align: left; }
code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
pre { padding: 10px 12px; background: #f6f8fa; border: 1px solid #e5e7eb; border-radius: 8px; overflow-x: auto; }
blockquote { margin: 10px 0; padding: 6px 12px; border-left: 3px solid #d1d5db; color: #374151; background: #fafafa; }
hr { border: 0; border-top: 1px solid #e5e7eb; margin: 16px 0; }
h1, h2, h3, h4 { margin: 14px 0 8px; }
ul { margin: 6px 0 10px 18px; }

/* Persian section */
.rtl { direction: rtl; unicode-bidi: plaintext; text-align: right; line-height: 1.55; }
.rtl, .rtl * {
  font-family:
    "Vazirmatn",
    "Vazir",
    "Shabnam",
    "Sahel",
    "Samim",
    "IRANSans",
    "Noto Naskh Arabic",
    "Noto Sans Arabic",
    "Geeza Pro",
    "Tahoma",
    "DejaVu Sans",
    Arial,
    sans-serif;
}
.rtl p, .rtl li { text-align: right; }
.rtl ul, .rtl ol { padding-right: 18px; padding-left: 0; direction: rtl; }
.rtl li { direction: rtl; }
.rtl ul { list-style-position: inside; }
.rtl blockquote { border-left: none; border-right: 3px solid #d1d5db; }
.rtl h1, .rtl h2, .rtl h3, .rtl h4 { letter-spacing: 0; }
"""


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            f"  {' '.join(cmd)}\n\n"
            f"stdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}"
        )


def _render_with_pandoc(src_md: Path, dst_pdf: Path) -> None:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise FileNotFoundError("pandoc not found")

    # Pandoc's PDF backend typically requires a TeX engine (e.g., xelatex).
    cmd = [pandoc, str(src_md), "-o", str(dst_pdf)]
    _run(cmd)

def _build_font_face_css(font_dir: Path | None) -> str:
    """
    Optionally embed a nicer Persian font if a TTF/OTF file exists locally.

    Supported filenames (place inside --font-dir, default ./fonts):
      - Vazirmatn-Regular.ttf / .otf
      - Vazir.ttf / Vazir-Regular.ttf
      - Shabnam.ttf / Shabnam-Regular.ttf
      - Sahel.ttf / Sahel-Regular.ttf
      - Samim.ttf / Samim-Regular.ttf
    """
    if not font_dir:
        return ""

    candidates = [
        ("Vazirmatn", ["Vazirmatn-Regular.ttf", "Vazirmatn-Regular.otf", "Vazirmatn.ttf"]),
        ("Vazir", ["Vazir-Regular.ttf", "Vazir.ttf"]),
        ("Shabnam", ["Shabnam-Regular.ttf", "Shabnam.ttf"]),
        ("Sahel", ["Sahel-Regular.ttf", "Sahel.ttf"]),
        ("Samim", ["Samim-Regular.ttf", "Samim.ttf"]),
    ]

    for family, names in candidates:
        for name in names:
            p = font_dir / name
            if p.exists() and p.is_file():
                url = p.resolve().as_uri()
                return (
                    "@font-face {"
                    f" font-family: '{family}';"
                    f" src: url('{url}');"
                    " font-weight: normal;"
                    " font-style: normal;"
                    "}\n"
                )

    return ""


def _wrap_bilingual_markdown_to_html(md_text: str, *, font_dir: Path | None) -> str:
    """
    Converts bilingual README.md (EN then '---' then FA) to an HTML string.
    The Persian half is wrapped in a container with RTL direction.
    """
    try:
        import markdown  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency: markdown. Install with:\n"
            "  python3 -m pip install markdown\n"
        ) from e

    # README.md now starts with a language selector and has anchors:
    #   <a id="en"></a>   ... English ...
    #   <a id="fa"></a>   ... Persian ...
    # Splitting on the first '---' would incorrectly classify the English body as Persian.
    fa_marker = '\n<a id="fa"></a>\n'
    if fa_marker in md_text:
        en_md, fa_md = md_text.split(fa_marker, 1)
        fa_md = '<a id="fa"></a>\n' + fa_md
    else:
        # Backward-compatible: older README format used a single '---' separator.
        parts = md_text.split("\n---\n", 1)
        en_md = parts[0]
        fa_md = parts[1] if len(parts) == 2 else ""

    en_html = markdown.markdown(en_md, extensions=["extra", "sane_lists", "tables", "fenced_code"])
    en_html = f'<div class="ltr">{en_html}</div>'
    if fa_md.strip():
        fa_html = markdown.markdown(fa_md, extensions=["extra", "sane_lists", "tables", "fenced_code"])
        fa_html = f'<div class="rtl">{fa_html}</div>'
        body = en_html + "<hr/>" + fa_html
    else:
        body = en_html

    font_face_css = _build_font_face_css(font_dir)

    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>{font_face_css}{DEFAULT_CSS}</style>
  </head>
  <body>{body}</body>
</html>
"""


def _render_with_weasyprint(src_md: Path, dst_pdf: Path, *, font_dir: Path | None) -> None:
    try:
        from weasyprint import HTML  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency: weasyprint. Install with:\n"
            "  python3 -m pip install weasyprint\n\n"
            "On macOS you may need system libs; if install fails, use pandoc instead."
        ) from e

    md_text = src_md.read_text(encoding="utf-8")
    html_text = _wrap_bilingual_markdown_to_html(md_text, font_dir=font_dir)
    HTML(string=html_text, base_url=str(src_md.parent)).write_pdf(str(dst_pdf))


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert README.md to PDF.")
    parser.add_argument("--input", "-i", default="README.md", help="Input markdown file (default: README.md)")
    parser.add_argument("--output", "-o", default="README.pdf", help="Output PDF file (default: README.pdf)")
    parser.add_argument(
        "--engine",
        choices=["auto", "pandoc", "weasyprint"],
        default="auto",
        help="Rendering engine (default: auto)",
    )
    parser.add_argument(
        "--font-dir",
        default="fonts",
        help="Directory containing optional Persian font files (default: ./fonts)",
    )
    args = parser.parse_args()

    src = Path(args.input).expanduser().resolve()
    dst = Path(args.output).expanduser().resolve()

    if not src.exists():
        print(f"Input file not found: {src}", file=sys.stderr)
        return 2

    dst.parent.mkdir(parents=True, exist_ok=True)

    engine = args.engine
    if engine == "auto":
        engine = "pandoc" if shutil.which("pandoc") else "weasyprint"

    font_dir = Path(args.font_dir).expanduser().resolve()
    if not font_dir.exists():
        font_dir = None

    try:
        if engine == "pandoc":
            _render_with_pandoc(src, dst)
        else:
            _render_with_weasyprint(src, dst, font_dir=font_dir)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1

    print(f"PDF generated: {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

