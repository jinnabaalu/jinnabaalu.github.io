# Resume HTML → PDF Generator

Generates `JinnaBalu-Resume.pdf` from `JinnaBalu-Resume.html` using [WeasyPrint](https://weasyprint.org/).

## Prerequisites

- **Python 3.9+**
- **WeasyPrint system dependencies** (varies by OS)

### macOS

```bash
brew install python pango libffi
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv \
  libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
  libffi-dev libcairo2
```

## Setup

```bash
cd assets/docs
# Install weasyprint
pip install weasyprint
```

## Generate PDF

```bash
# With venv activated
python3 generate_pdf.py
```


## Files

| File | Description |
|------|-------------|
| `JinnaBalu-Resume.html` | Source resume (standalone HTML with embedded CSS) |
| `JinnaBalu-Resume.pdf` | Generated PDF output |
| `generate_pdf.py` | Python script that converts HTML → PDF |
| `.venv/` | Virtual environment (gitignored) |

## Notes

- Edit `JinnaBalu-Resume.html` to update content, then re-run `generate_pdf.py`.
- The HTML file mirrors the profile page at [jinnabalu.com/profile](https://jinnabalu.com/profile).
- WeasyPrint warnings about `overflow-x` and media queries are harmless and can be ignored.
