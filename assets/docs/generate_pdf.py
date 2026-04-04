#!/usr/bin/env python3
"""Generate PDF resume from the HTML resume file using WeasyPrint."""

import sys
from pathlib import Path

def main():
    script_dir = Path(__file__).resolve().parent
    html_path = script_dir / "JinnaBalu-Resume.html"
    pdf_path = script_dir / "JinnaBalu-Resume.pdf"

    if not html_path.exists():
        print(f"ERROR: HTML resume not found at {html_path}", file=sys.stderr)
        sys.exit(1)

    try:
        from weasyprint import HTML
    except ImportError:
        print(
            "ERROR: weasyprint is not installed.\n"
            "Install it with: pip install weasyprint\n"
            "See README.md for full setup instructions.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Reading  : {html_path}")
    print(f"Writing  : {pdf_path}")

    HTML(filename=str(html_path)).write_pdf(str(pdf_path))

    size_kb = pdf_path.stat().st_size / 1024
    print(f"Done     : {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
