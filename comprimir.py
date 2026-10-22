#!/usr/bin/env python3
"""Compress all PDFs in a folder.

Usage:
    python comprimir.py /path/to/pdfs
    python comprimir.py /path/to/pdfs -o ~/Downloads/mis-pdfs
    python comprimir.py /path/to/pdfs --quality low

Creates a folder in Downloads with the compressed files.
Requires: pip install -r requirements.txt
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

QUALITY_PRESETS = {
    "high": (85, 300, 200),
    "medium": (70, 225, 150),
    "low": (55, 180, 120),
}


def find_downloads_dir() -> Path:
    home = Path.home()
    for name in ("Downloads", "Descargas"):
        candidate = home / name
        if candidate.is_dir():
            return candidate
    fallback = home / "Downloads"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def compress_pdf(src: Path, dst: Path, quality: str = "medium") -> tuple[int, int]:
    """Compress one PDF. Returns (original_bytes, compressed_bytes)."""
    import pymupdf

    jpeg_quality, dpi_threshold, dpi_target = QUALITY_PRESETS[quality]
    original = src.stat().st_size
    with pymupdf.open(src) as doc:
        try:
            doc.rewrite_images(
                dpi_threshold=dpi_threshold,
                dpi_target=dpi_target,
                quality=jpeg_quality,
            )
        except Exception:
            pass
        doc.save(
            dst,
            garbage=4,
            deflate=True,
            clean=True,
        )
    return original, dst.stat().st_size


def fmt_mb(num_bytes: int) -> str:
    return f"{num_bytes / (1024 * 1024):.1f} MB"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compress all PDFs in a folder into Downloads."
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Folder containing the PDFs to compress",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Output folder (default: ~/Downloads/pdfs-comprimidos-<date>)",
    )
    parser.add_argument(
        "--quality",
        choices=("high", "medium", "low"),
        default="medium",
        help="Image quality vs size (default: medium)",
    )
    args = parser.parse_args()

    src_dir: Path = args.input_dir.expanduser().resolve()
    if not src_dir.is_dir():
        print(f"Error: not a folder: {src_dir}", file=sys.stderr)
        return 1

    pdfs = sorted(
        [p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    )
    if not pdfs:
        print(f"No PDFs found in {src_dir}")
        return 0

    if args.output_dir:
        out_dir = args.output_dir.expanduser().resolve()
    else:
        stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        out_dir = find_downloads_dir() / f"pdfs-comprimidos-{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        import pymupdf  # noqa: F401
    except ImportError:
        print("Missing dependency: pip install pymupdf", file=sys.stderr)
        return 1

    print(f"Found {len(pdfs)} PDFs in {src_dir} (quality={args.quality})")
    print(f"Output: {out_dir}\n")

    total_orig = 0
    total_new = 0
    failed = 0

    for pdf in pdfs:
        dst = out_dir / pdf.name
        try:
            orig, new = compress_pdf(pdf, dst, quality=args.quality)
            total_orig += orig
            total_new += new
            saved = 100 * (1 - new / orig) if orig else 0
            print(f"OK  {pdf.name}: {fmt_mb(orig)} -> {fmt_mb(new)} (-{saved:.0f}%)")
        except Exception as exc:
            failed += 1
            print(f"FAIL {pdf.name}: {exc}", file=sys.stderr)

    print()
    if total_orig:
        saved_total = 100 * (1 - total_new / total_orig)
        print(
            f"Total: {fmt_mb(total_orig)} -> {fmt_mb(total_new)} "
            f"(-{saved_total:.0f}%) in {out_dir}"
        )
    if failed:
        print(f"{failed} file(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
