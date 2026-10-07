#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Assemble extracted page images and optionally OCR them using Windows WinRT."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


class BmpError(RuntimeError):
    pass


@dataclass(frozen=True)
class PageImage:
    page_id: str
    sort_key: tuple[int, int]
    path: Path
    source_root: Path


def _roman_to_int(s: str) -> int:
    s = s.strip().lower()
    if not s:
        raise ValueError("empty roman numeral")
    values = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
    total = 0
    prev = 0
    for ch in reversed(s):
        v = values.get(ch)
        if v is None:
            raise ValueError(f"invalid roman numeral: {s!r}")
        if v < prev:
            total -= v
        else:
            total += v
            prev = v
    return total


def _find_page_text_bmps(roots: Iterable[Path]) -> list[PageImage]:
    pattern = re.compile(r"^(?:\d+_)?imgPage(\d+|[ivxlcdm]+)Text(?:__1)?\.bmp$", re.IGNORECASE)
    found: list[PageImage] = []
    for root in roots:
        resources_dir = root / "resources"
        if not resources_dir.is_dir():
            continue
        for bmp in resources_dir.iterdir():
            if not bmp.is_file():
                continue
            m = pattern.match(bmp.name)
            if not m:
                continue
            raw = m.group(1)
            if raw.isdigit():
                page_num = int(raw)
                page_id = str(page_num)
                sort_key = (1, page_num)
            else:
                page_id = raw.lower()
                sort_key = (0, _roman_to_int(page_id))
            found.append(PageImage(page_id=page_id, sort_key=sort_key, path=bmp, source_root=root))
    found.sort(key=lambda x: (x.sort_key, str(x.path).lower()))
    ids = [image.page_id for image in found]
    if len(set(ids)) != len(ids):
        raise BmpError("Duplicate page IDs; supply non-overlapping extraction roots")
    return found


def _u16le(b: bytes, off: int) -> int:
    return int.from_bytes(b[off : off + 2], "little", signed=False)


def _u32le(b: bytes, off: int) -> int:
    return int.from_bytes(b[off : off + 4], "little", signed=False)


def _i32le(b: bytes, off: int) -> int:
    return int.from_bytes(b[off : off + 4], "little", signed=True)


def bmp_to_rgb(bmp: bytes) -> tuple[int, int, bytes]:
    if len(bmp) < 26:
        raise BmpError("BMP too small")
    if bmp[0:2] != b"BM":
        raise BmpError("Not a BMP (missing BM)")
    pixel_off = _u32le(bmp, 10)
    dib_size = _u32le(bmp, 14)

    if dib_size == 12:
        if len(bmp) < 14 + 12:
            raise BmpError("BITMAPCOREHEADER truncated")
        width = _u16le(bmp, 18)
        height = _u16le(bmp, 20)
        planes = _u16le(bmp, 22)
        bpp = _u16le(bmp, 24)
        compression = 0
        palette_off = 14 + 12
        palette_entry_size = 3
        palette_count = (1 << bpp) if bpp <= 8 else 0
    elif dib_size >= 40:
        if len(bmp) < 14 + dib_size:
            raise BmpError("BITMAPINFOHEADER/Vx truncated")
        width = _i32le(bmp, 18)
        height = _i32le(bmp, 22)
        planes = _u16le(bmp, 26)
        bpp = _u16le(bmp, 28)
        compression = _u32le(bmp, 30)
        clr_used = _u32le(bmp, 46) if dib_size >= 36 else 0
        # For our extracted files we expect BI_RGB
        palette_off = 14 + dib_size
        palette_entry_size = 4
        palette_count = 0
        if bpp <= 8:
            palette_count = clr_used if clr_used != 0 else (1 << bpp)
    else:
        raise BmpError(f"Unsupported DIB header size: {dib_size}")

    if planes != 1:
        raise BmpError(f"Unsupported planes={planes}")
    if bpp not in (8, 24):
        raise BmpError(f"Unsupported bpp={bpp} (expected 8 or 24)")
    if compression not in (0, 1):
        raise BmpError(f"Unsupported compression={compression}")
    if compression == 1 and bpp != 8:
        raise BmpError("BI_RLE8 only supported for 8bpp BMPs")

    top_down = False
    if isinstance(height, int) and height < 0:
        top_down = True
        height = -height
    if width <= 0 or height <= 0:
        raise BmpError(f"Invalid dimensions {width}x{height}")

    if pixel_off >= len(bmp):
        raise BmpError("Pixel offset beyond file")
    if pixel_off < palette_off + palette_count * palette_entry_size:
        raise BmpError("Pixel data overlaps header or palette")

    palette: Optional[list[tuple[int, int, int]]] = None
    if bpp == 8:
        palette = []
        needed = palette_count * palette_entry_size
        if palette_off + needed > len(bmp):
            raise BmpError("Palette exceeds file")
        for i in range(palette_count):
            o = palette_off + i * palette_entry_size
            b = bmp[o + 0]
            g = bmp[o + 1]
            r = bmp[o + 2]
            palette.append((r, g, b))

    pixel_bytes = bmp[pixel_off:]

    def write_rgb_from_indices(indices_topdown: bytes) -> bytes:
        assert palette is not None
        if len(indices_topdown) != width * height:
            raise BmpError("Decoded index buffer has wrong size")
        out = bytearray(width * height * 3)
        for i, idx in enumerate(indices_topdown):
            if idx >= len(palette):
                raise BmpError("Pixel index exceeds palette")
            r, g, b = palette[idx]
            o = i * 3
            out[o : o + 3] = bytes((r, g, b))
        return bytes(out)

    if compression == 1 and bpp == 8:
        assert palette is not None
        indices = bytearray(width * height)

        def set_px(x: int, y: int, v: int) -> None:
            if x < 0 or y < 0 or x >= width or y >= height:
                return
            row = y if top_down else (height - 1 - y)
            indices[row * width + x] = v & 0xFF

        x = 0
        y = 0
        i = 0
        while i + 1 < len(pixel_bytes):
            count = pixel_bytes[i]
            val = pixel_bytes[i + 1]
            i += 2
            if count:
                for _ in range(count):
                    set_px(x, y, val)
                    x += 1
                continue

            # Escape codes
            if val == 0:  # end of line
                x = 0
                y += 1
                if y >= height:
                    break
            elif val == 1:  # end of bitmap
                break
            elif val == 2:  # delta
                if i + 1 >= len(pixel_bytes):
                    break
                dx = pixel_bytes[i]
                dy = pixel_bytes[i + 1]
                i += 2
                x += dx
                y += dy
                if y >= height:
                    break
            else:
                n = val
                if i + n > len(pixel_bytes):
                    n = max(0, len(pixel_bytes) - i)
                for j in range(n):
                    set_px(x, y, pixel_bytes[i + j])
                    x += 1
                i += n
                if (val & 1) == 1:
                    i += 1  # pad to word boundary
        return width, height, write_rgb_from_indices(bytes(indices))

    row_stride_raw = ((width * bpp + 31) // 32) * 4
    needed = row_stride_raw * height
    if len(pixel_bytes) < needed:
        raise BmpError("Pixel data truncated")

    out = bytearray(width * height * 3)
    for row in range(height):
        src_row = row if top_down else (height - 1 - row)
        src_off = src_row * row_stride_raw
        if bpp == 24:
            for x in range(width):
                b = pixel_bytes[src_off + x * 3 + 0]
                g = pixel_bytes[src_off + x * 3 + 1]
                r = pixel_bytes[src_off + x * 3 + 2]
                dst = (row * width + x) * 3
                out[dst : dst + 3] = bytes((r, g, b))
        else:
            assert palette is not None
            for x in range(width):
                idx = pixel_bytes[src_off + x]
                if idx >= len(palette):
                    raise BmpError("Pixel index exceeds palette")
                r, g, b = palette[idx]
                dst = (row * width + x) * 3
                out[dst : dst + 3] = bytes((r, g, b))

    return width, height, bytes(out)


class PdfBuilder:
    def __init__(self) -> None:
        self._objects: list[bytes] = []
        self._root_obj: Optional[int] = None

    def add_object(self, body: bytes) -> int:
        self._objects.append(body)
        return len(self._objects)

    def set_root(self, obj_num: int) -> None:
        self._root_obj = obj_num

    def build(self) -> bytes:
        if self._root_obj is None:
            raise RuntimeError("PDF root not set")
        out = bytearray()
        out += b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"
        offsets = [0]
        for i, obj in enumerate(self._objects, start=1):
            offsets.append(len(out))
            out += f"{i} 0 obj\n".encode("ascii")
            out += obj
            if not obj.endswith(b"\n"):
                out += b"\n"
            out += b"endobj\n"

        xref_start = len(out)
        out += b"xref\n"
        out += f"0 {len(self._objects) + 1}\n".encode("ascii")
        out += b"0000000000 65535 f \n"
        for off in offsets[1:]:
            out += f"{off:010d} 00000 n \n".encode("ascii")
        out += b"trailer\n"
        out += f"<< /Size {len(self._objects) + 1} /Root {self._root_obj} 0 R >>\n".encode("ascii")
        out += b"startxref\n"
        out += f"{xref_start}\n".encode("ascii")
        out += b"%%EOF\n"
        return bytes(out)


def build_pdf_from_bmps(images: list[PageImage], out_pdf: Path) -> None:
    pdf = PdfBuilder()
    page_obj_nums: list[int] = []

    # Placeholder Pages object; we fill it later once we have all page objects.
    pages_obj_num = pdf.add_object(b"<< /Type /Pages /Kids [] /Count 0 >>\n")

    for img in images:
        bmp = img.path.read_bytes()
        width, height, rgb = bmp_to_rgb(bmp)
        compressed = zlib.compress(rgb, level=6)

        img_dict = (
            f"<< /Type /XObject /Subtype /Image /Name /Im0 /Width {width} /Height {height} "
            f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(compressed)} >>\n"
        ).encode("ascii")
        img_obj_num = pdf.add_object(img_dict + b"stream\n" + compressed + b"\nendstream\n")

        content = f"q {width} 0 0 {height} 0 0 cm /Im0 Do Q\n".encode("ascii")
        content_obj_num = pdf.add_object(
            f"<< /Length {len(content)} >>\n".encode("ascii") + b"stream\n" + content + b"endstream\n"
        )

        resources = f"<< /XObject << /Im0 {img_obj_num} 0 R >> >>"
        page_body = (
            f"<< /Type /Page /Parent {pages_obj_num} 0 R /Resources {resources} "
            f"/MediaBox [0 0 {width} {height}] /Contents {content_obj_num} 0 R >>\n"
        ).encode("ascii")
        page_obj_nums.append(pdf.add_object(page_body))

    kids = " ".join(f"{n} 0 R" for n in page_obj_nums)
    pages_body = f"<< /Type /Pages /Kids [ {kids} ] /Count {len(page_obj_nums)} >>\n".encode("ascii")
    pdf._objects[pages_obj_num - 1] = pages_body

    catalog_obj_num = pdf.add_object(f"<< /Type /Catalog /Pages {pages_obj_num} 0 R >>\n".encode("ascii"))
    pdf.set_root(catalog_obj_num)

    out_pdf.write_bytes(pdf.build())


def run_windows_ocr(images: list[PageImage]) -> dict[str, str]:
    """
    OCR via Windows.Media.Ocr (WinRT) using a single PowerShell process.
    Returns: {page_num: text}
    """
    payload = [{"page": img.page_id, "path": str(img.path.resolve())} for img in images]
    with tempfile.TemporaryDirectory(prefix="omt_ocr_") as td:
        list_path = Path(td) / "images.json"
        out_path = Path(td) / "ocr_out.json"
        list_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        ps_script = r"""
param(
  [Parameter(Mandatory=$true)][string]$ListPath,
  [Parameter(Mandatory=$true)][string]$OutPath
)

$ErrorActionPreference = "Stop"

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

Add-Type -AssemblyName System.Runtime.WindowsRuntime | Out-Null
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrResult, Windows.Foundation, ContentType=WindowsRuntime]

$asTaskGeneric = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
  $_.Name -eq "AsTask" -and $_.IsGenericMethodDefinition -and $_.GetParameters().Count -eq 1
} | Select-Object -First 1

function Await([object]$op, [Type]$resultType) {
  $m = $asTaskGeneric.MakeGenericMethod($resultType)
  $task = $m.Invoke($null, @($op))
  return $task.GetAwaiter().GetResult()
}

$ocr = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if (-not $ocr) { throw "Windows OCR engine not available (TryCreateFromUserProfileLanguages returned null)" }

$list = Get-Content -Raw -LiteralPath $ListPath | ConvertFrom-Json
$out = New-Object System.Collections.Generic.List[object]

foreach ($item in $list) {
  $p = [string]$item.path
  $page = [string]$item.page
  try {
    $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($p)) ([Windows.Storage.StorageFile])
    $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    try {
      $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
      $bmp = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    } finally {
      try { $stream.Dispose() } catch {}
    }

    $gray = [Windows.Graphics.Imaging.SoftwareBitmap]::Convert($bmp, [Windows.Graphics.Imaging.BitmapPixelFormat]::Gray8)
    $res = Await ($ocr.RecognizeAsync($gray)) ([Windows.Media.Ocr.OcrResult])
$out.Add([pscustomobject]@{ page = $page; path = $p; text = $res.Text }) | Out-Null
  } catch {
    $out.Add([pscustomobject]@{ page = $page; path = $p; error = $_.Exception.Message }) | Out-Null
  }
}

$out | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $OutPath -Encoding UTF8
"""
        script_path = Path(td) / "ocr.ps1"
        script_path.write_text(ps_script, encoding="utf-8")

        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            "-ListPath",
            str(list_path),
            "-OutPath",
            str(out_path),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if proc.returncode != 0:
            raise RuntimeError(
                "OCR PowerShell failed.\n"
                f"STDOUT:\n{proc.stdout}\n\nSTDERR:\n{proc.stderr}\n"
            )
        results = json.loads(out_path.read_text(encoding="utf-8-sig") or "[]")
        if isinstance(results, dict):
            results = [results]
        out: dict[str, str] = {}
        for item in results:
            page = str(item["page"])
            if "text" in item and isinstance(item["text"], str):
                out[page] = item["text"]
            else:
                raise RuntimeError(f"OCR failed on page {page}: {item.get('error', 'Unknown error')}")
        if set(out) != {img.page_id for img in images}:
            raise RuntimeError("OCR returned an incomplete set of pages")
        return out


def write_markdown(images: list[PageImage], ocr_text: dict[str, str], out_md: Path) -> None:
    lines: list[str] = []
    lines.append("# OMT Page Text (OCR)\n")
    roots = sorted({i.source_root for i in images}, key=lambda p: str(p))
    lines.append(
        f"_Generated from {len(images)} `imgPageXXXText.bmp` images across: "
        + ", ".join(f"`{root}`" for root in roots)
        + "_\n"
    )

    for img in images:
        text = ocr_text.get(img.page_id, "").replace("\r\n", "\n").replace("\r", "\n").strip()
        lines.append(f"## Page {img.page_id}\n")
        if not text:
            lines.append("_No text recognized._\n")
        else:
            lines.append(text + "\n")

    out_md.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Combine imgPageXXXText.bmp from extracted OMT dirs into a single PDF, OCR it, and write Markdown."
    )
    ap.add_argument(
        "--roots",
        nargs="*",
        default=["extracted_BOOK", "extracted_BOOK2", "extracted_BOOK3"],
        help="Extraction directories (each must contain a resources/ folder).",
    )
    ap.add_argument("--out-pdf", default="omt_imgPageText_all.pdf", help="Output PDF path.")
    ap.add_argument("--out-md", default="omt_imgPageText_all.md", help="Output Markdown path.")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of pages (0 = no limit).")
    ap.add_argument("--no-ocr", action="store_true", help="Skip OCR (Markdown will be placeholders).")
    args = ap.parse_args(argv)

    roots = [Path(r) for r in args.roots]
    try:
        images = _find_page_text_bmps(roots)
    except (OSError, BmpError) as exc:
        ap.exit(1, f"error: {exc}\n")
    if not images:
        print("No imgPageXXXText.bmp files found under provided roots.", file=sys.stderr)
        return 2

    if args.limit and args.limit > 0:
        images = images[: args.limit]

    out_pdf = Path(args.out_pdf)
    out_md = Path(args.out_md)
    if out_pdf.resolve() == out_md.resolve() or out_pdf.exists() or out_md.exists():
        ap.exit(1, "error: PDF and Markdown need distinct, new output paths\n")

    print(f"Found {len(images)} page-text BMPs.")
    print(f"Writing PDF: {out_pdf}")
    build_pdf_from_bmps(images, out_pdf)

    ocr_text: dict[str, str] = {img.page_id: "" for img in images}
    if args.no_ocr:
        for img in images:
            ocr_text[img.page_id] = ""
    else:
        print("Running Windows OCR (this can take a while)...")
        ocr_text = run_windows_ocr(images)

    print(f"Writing Markdown: {out_md}")
    write_markdown(images, ocr_text, out_md)

    print("Done.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
