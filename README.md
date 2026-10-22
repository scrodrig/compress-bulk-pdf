# compress-bulk-pdf

Compress every PDF in a folder and drop the lighter copies into `~/Downloads`.
Built for scanned receipts and invoices that eat disk space.

## Quick path

1. `mise install` (pins Python from `mise.toml`)
2. `python -m venv .venv`
3. `source .venv/bin/activate.fish` (bash: `source .venv/bin/activate`)
4. `pip install -r requirements.txt`
5. `python comprimir.py /path/to/pdfs`
6. Pick up the results from `~/Downloads/pdfs-comprimidos-<date>/`

## Usage

```bash
python comprimir.py /path/to/pdfs
python comprimir.py /path/to/pdfs -o ~/Downloads/my-pdfs
python comprimir.py /path/to/pdfs --quality high
```

| Option | What it does |
|--------|--------------|
| `input_dir` | Folder with the PDFs to compress (required). |
| `-o, --output-dir` | Where to write the results (default: `~/Downloads/pdfs-comprimidos-<date>/`). |
| `--quality` | `high`, `medium` (default), or `low`. See presets below. |

Originals are never touched; compressed copies keep the same file names.

## Quality presets

| Preset | JPEG quality | Downsample above | Downsample to |
|--------|--------------|------------------|---------------|
| `high` | 85 | 300 DPI | 200 DPI |
| `medium` | 70 | 225 DPI | 150 DPI |
| `low` | 55 | 180 DPI | 120 DPI |

Start with `medium` (typically ~90% smaller on scans). If small print looks
blurry, re-run with `--quality high`.

## How it works

Scanned PDFs are usually one big already-encoded image per page, so plain
re-saving shrinks nothing. The script re-encodes images as JPEG and
downsamples hi-res scans (`rewrite_images`), then rebuilds the file with
garbage collection, deflate, and content-stream cleanup. Each file reports
`original -> compressed (-%)`, plus a total at the end.

## Project files

| File | Purpose |
|------|---------|
| `comprimir.py` | The compressor script. |
| `requirements.txt` | Python dependency (`pymupdf`). |
| `mise.toml` | Pinned Python toolchain. |
| `opencode.json` | Python language server for opencode. |
