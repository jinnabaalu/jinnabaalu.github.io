#!/usr/bin/env python3
"""Generate PDF resume from the HTML resume file using WeasyPrint."""

import os
import sys
from pathlib import Path


def maybe_reexec_with_local_venv(script_dir: Path) -> None:
    venv_python = script_dir / ".venv" / "bin" / "python3"
    if not venv_python.exists():
        return

    current_python = Path(sys.executable).resolve()
    if current_python == venv_python.resolve():
        return

    os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve())])

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
        maybe_reexec_with_local_venv(script_dir)
        print(
            "ERROR: weasyprint is not installed.\n"
            "Recommended setup:\n"
            "  python3 -m venv .venv\n"
            "  . .venv/bin/activate\n"
            "  python3 -m pip install weasyprint\n"
            "After that, you can run: python3 generate_pdf.py\n"
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
