#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Extract observed OMT page/resource containers from The Road Ahead CD-ROM."""
from __future__ import annotations

import argparse
import dataclasses
import json
import io
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable, Optional


class OmtFormatError(RuntimeError):
    pass


def _read_exact(f: BinaryIO, n: int) -> bytes:
    data = f.read(n)
    if len(data) != n:
        raise OmtFormatError(f"Unexpected EOF: wanted {n} bytes, got {len(data)}")
    return data


def _read_c_string(f: BinaryIO, *, max_len: int = 4096) -> str:
    buf = bytearray()
    while True:
        b = f.read(1)
        if not b:
            raise OmtFormatError("Unexpected EOF while reading C-string")
        if b == b"\x00":
            break
        buf += b
        if len(buf) > max_len:
            raise OmtFormatError(f"C-string exceeded max_len={max_len}")
    try:
        return buf.decode("ascii")
    except UnicodeDecodeError:
        return buf.decode("latin-1")


def _u24le(b: bytes) -> int:
    if len(b) != 3:
        raise ValueError("u24 requires 3 bytes")
    return b[0] | (b[1] << 8) | (b[2] << 16)


def _sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w.\- ]+", "_", name, flags=re.ASCII)
    name = name.replace(" ", "_")
    name = re.sub(r"_+", "_", name)
    name = name.strip("._")
    return name or "unnamed"


@dataclass(frozen=True)
class OmtHeader:
    page_count: int
    page_table_size: int
    page_table_offset: int
    resource_count: int
    resource_table_size: int
    resource_table_offset: int
    dll_count: int
    dll_list_offset: int
    trailer_size: int
    trailer_offset: int
    unknown_0x28: int


@dataclass(frozen=True)
class PageEntry:
    index: int
    name: str
    flags: int
    offset: int
    size: int


@dataclass(frozen=True)
class ResourceEntry:
    index: int
    name: str
    kind: int
    unk1: int
    offset1: int
    size1: int
    offset2: Optional[int] = None
    size2: Optional[int] = None


def parse_header(f: BinaryIO) -> OmtHeader:
    f.seek(0)
    raw = _read_exact(f, 0x2C)
    vals = struct.unpack("<11I", raw)
    return OmtHeader(
        page_count=vals[0],
        page_table_size=vals[1],
        page_table_offset=vals[2],
        resource_count=vals[3],
        resource_table_size=vals[4],
        resource_table_offset=vals[5],
        dll_count=vals[6],
        dll_list_offset=vals[7],
        trailer_size=vals[8],
        trailer_offset=vals[9],
        unknown_0x28=vals[10],
    )


def validate_header(hdr: OmtHeader, file_size: int) -> None:
    """Reject out-of-file tables before parsing counts or writing output."""
    for label, offset, size in (
        ("page table", hdr.page_table_offset, hdr.page_table_size),
        ("resource table", hdr.resource_table_offset, hdr.resource_table_size),
        ("trailer", hdr.trailer_offset, hdr.trailer_size),
        ("DLL list", hdr.dll_list_offset, hdr.dll_count),
    ):
        if offset + size > file_size:
            raise OmtFormatError(f"{label} points outside file")
    if hdr.page_count > hdr.page_table_size // 9:
        raise OmtFormatError("Page count cannot fit in page table")
    if hdr.resource_count > hdr.resource_table_size // 11:
        raise OmtFormatError("Resource count cannot fit in resource table")


def parse_dll_list(f: BinaryIO, hdr: OmtHeader) -> list[str]:
    f.seek(hdr.dll_list_offset)
    dlls: list[str] = []
    for _ in range(hdr.dll_count):
        dlls.append(_read_c_string(f, max_len=512))
    return dlls


def parse_page_table(f: BinaryIO, hdr: OmtHeader, file_size: int) -> list[PageEntry]:
    f.seek(hdr.page_table_offset)
    f = io.BytesIO(_read_exact(f, hdr.page_table_size))
    start_pos = f.tell()
    pages: list[PageEntry] = []
    for idx in range(hdr.page_count):
        name = _read_c_string(f)
        meta = _read_exact(f, 8)
        flags = meta[0]
        off = _u24le(meta[1:4]) << 8
        size = struct.unpack_from("<I", meta, 4)[0]
        if off + size > file_size:
            raise OmtFormatError(
                f"Page {idx} {name!r} points outside file: off=0x{off:X} size={size}"
            )
        pages.append(PageEntry(index=idx, name=name, flags=flags, offset=off, size=size))
    end_pos = f.tell()
    consumed = end_pos - start_pos
    if consumed != hdr.page_table_size:
        raise OmtFormatError(
            f"Page table size mismatch: header={hdr.page_table_size} parsed={consumed}"
        )
    return pages


def parse_resource_table(f: BinaryIO, hdr: OmtHeader, file_size: int) -> list[ResourceEntry]:
    f.seek(hdr.resource_table_offset)
    f = io.BytesIO(_read_exact(f, hdr.resource_table_size))
    start_pos = f.tell()
    resources: list[ResourceEntry] = []
    for idx in range(hdr.resource_count):
        name = _read_c_string(f)
        meta = _read_exact(f, 10)
        kind = struct.unpack_from("<H", meta, 0)[0]
        unk1 = meta[2]
        off1 = _u24le(meta[3:6]) << 8
        size1 = struct.unpack_from("<I", meta, 6)[0]
        off2 = size2 = None
        if (kind >> 8) == 0x04:
            meta2 = _read_exact(f, 8)
            _unk2 = meta2[0]
            off2 = _u24le(meta2[1:4]) << 8
            size2 = struct.unpack_from("<I", meta2, 4)[0]
        if off1 + size1 > file_size:
            raise OmtFormatError(
                f"Resource {idx} {name!r} points outside file: off=0x{off1:X} size={size1}"
            )
        if off2 is not None and size2 is not None and off2 + size2 > file_size:
            raise OmtFormatError(
                f"Resource {idx} {name!r} secondary points outside file: off=0x{off2:X} size={size2}"
            )
        resources.append(
            ResourceEntry(
                index=idx,
                name=name,
                kind=kind,
                unk1=unk1,
                offset1=off1,
                size1=size1,
                offset2=off2,
                size2=size2,
            )
        )
    end_pos = f.tell()
    consumed = end_pos - start_pos
    if consumed != hdr.resource_table_size:
        raise OmtFormatError(
            f"Resource table size mismatch: header={hdr.resource_table_size} parsed={consumed}"
        )
    return resources


def _dib_to_bmp(dib: bytes) -> bytes:
    if len(dib) < 4:
        raise OmtFormatError("DIB too small")
    dib_header_size = struct.unpack_from("<I", dib, 0)[0]
    if dib_header_size == 12:  # BITMAPCOREHEADER
        if len(dib) < 12:
            raise OmtFormatError("COREHEADER too small")
        bpp = struct.unpack_from("<H", dib, 10)[0]
        colors = (1 << bpp) if bpp <= 8 else 0
        palette_size = colors * 3
        bits_off = 12 + palette_size
    elif dib_header_size in (40, 108, 124):  # BITMAPINFOHEADER/V4/V5
        if len(dib) < dib_header_size:
            raise OmtFormatError("INFOHEADER too small")
        bpp = struct.unpack_from("<H", dib, 14)[0]
        compression = struct.unpack_from("<I", dib, 16)[0]
        clr_used = struct.unpack_from("<I", dib, 32)[0]
        palette_entries = 0
        if bpp <= 8:
            palette_entries = clr_used if clr_used != 0 else (1 << bpp)
        palette_size = palette_entries * 4
        masks_size = 0
        if dib_header_size == 40 and compression in (3, 6):  # BI_BITFIELDS / BI_ALPHABITFIELDS
            masks_size = 12 if compression == 3 else 16
        bits_off = dib_header_size + masks_size + palette_size
    else:
        raise OmtFormatError(f"Unknown DIB header size: {dib_header_size}")

    if bits_off <= 0 or bits_off > len(dib):
        raise OmtFormatError(f"Computed bits offset out of range: {bits_off}")

    bf_type = b"BM"
    bf_size = 14 + len(dib)
    bf_reserved1 = 0
    bf_reserved2 = 0
    bf_off_bits = 14 + bits_off
    file_hdr = struct.pack("<2sIHHI", bf_type, bf_size, bf_reserved1, bf_reserved2, bf_off_bits)
    return file_hdr + dib


def try_extract_dib_bmp(chunk: bytes) -> Optional[bytes]:
    if len(chunk) < 8:
        return None
    # Common pattern: u32 payload_len, then DIB payload, then trailing bytes.
    payload_len = struct.unpack_from("<I", chunk, 0)[0]
    if 0 < payload_len <= len(chunk) - 4:
        dib = chunk[4 : 4 + payload_len]
        if len(dib) >= 4:
            dib_header_size = struct.unpack_from("<I", dib, 0)[0]
            if dib_header_size in (12, 40, 108, 124):
                try:
                    return _dib_to_bmp(dib)
                except OmtFormatError:
                    return None
    # Fallback: direct DIB
    dib_header_size = struct.unpack_from("<I", chunk, 0)[0]
    if dib_header_size in (12, 40, 108, 124):
        try:
            return _dib_to_bmp(chunk)
        except OmtFormatError:
            return None
    return None


def _read_chunk(f: BinaryIO, offset: int, size: int) -> bytes:
    f.seek(offset)
    return _read_exact(f, size)


def carve_riff_waves(data: bytes) -> list[tuple[int, str, bytes]]:
    out: list[tuple[int, str, bytes]] = []
    i = 0
    while True:
        i = data.find(b"RIFF", i)
        if i < 0:
            break
        if i + 12 > len(data):
            break
        size = struct.unpack_from("<I", data, i + 4)[0]
        form = data[i + 8 : i + 12]
        total = size + 8
        if total >= 12 and i + total <= len(data) and all(32 <= b < 127 for b in form):
            form_s = form.decode("ascii", errors="replace")
            out.append((i, form_s, data[i : i + total]))
        i += 4
    return out


def write_manifest(
    out_dir: Path,
    hdr: OmtHeader,
    dlls: list[str],
    pages: list[PageEntry],
    resources: list[ResourceEntry],
) -> None:
    manifest = {
        "header": dataclasses.asdict(hdr),
        "dlls": dlls,
        "pages": [dataclasses.asdict(p) for p in pages],
        "resources": [dataclasses.asdict(r) for r in resources],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def extract_omt(path: Path, out_dir: Path, *, carve_riff: bool = True, convert_bmp: bool = True) -> None:
    file_size = path.stat().st_size
    if out_dir.exists():
        raise OmtFormatError(f"Output directory already exists: {out_dir}; choose a new directory")

    with path.open("rb") as f:
        hdr = parse_header(f)
        validate_header(hdr, file_size)
        dlls = parse_dll_list(f, hdr)
        pages = parse_page_table(f, hdr, file_size)
        resources = parse_resource_table(f, hdr, file_size)

        out_dir.mkdir(parents=True, exist_ok=False)
        for folder in ("pages", "resources", "carved"):
            (out_dir / folder).mkdir()
        write_manifest(out_dir, hdr, dlls, pages, resources)

        # Pages: raw dump
        for p in pages:
            safe = _sanitize_filename(p.name)
            out_path = out_dir / "pages" / f"{p.index:03d}_{safe}.bin"
            out_path.write_bytes(_read_chunk(f, p.offset, p.size))

        # Resources: try DIB->BMP, else raw
        for r in resources:
            for which, off, size in (
                ("1", r.offset1, r.size1),
                ("2", r.offset2, r.size2),
            ):
                if off is None or size is None:
                    continue
                chunk = _read_chunk(f, off, size)
                safe = _sanitize_filename(r.name)
                stem = f"{r.index:04d}_{safe}__{which}"
                if convert_bmp:
                    bmp = try_extract_dib_bmp(chunk)
                    if bmp is not None:
                        (out_dir / "resources" / f"{stem}.bmp").write_bytes(bmp)
                        continue
                (out_dir / "resources" / f"{stem}.bin").write_bytes(chunk)

        if carve_riff:
            f.seek(0)
            data = f.read()
            for off, form, blob in carve_riff_waves(data):
                ext = ".wav" if form == "WAVE" else ".riff"
                (out_dir / "carved" / f"riff_{off:08X}_{_sanitize_filename(form)}{ext}").write_bytes(blob)


def main(argv: Optional[Iterable[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Extract page/resources from .OMT files (1990s OMT container).")
    ap.add_argument("omt", type=Path, help="Input .OMT file (e.g. BOOK.OMT)")
    ap.add_argument("--out", type=Path, default=None, help="Output directory (default: ./extracted_<stem>)")
    ap.add_argument("--no-carve", action="store_true", help="Disable RIFF carving")
    ap.add_argument("--no-bmp", action="store_true", help="Disable DIB->BMP conversion")
    args = ap.parse_args(list(argv) if argv is not None else None)

    out_dir = args.out
    if out_dir is None:
        out_dir = Path(f"extracted_{args.omt.stem}")

    try:
        extract_omt(args.omt, out_dir, carve_riff=not args.no_carve, convert_bmp=not args.no_bmp)
    except (OSError, OmtFormatError) as exc:
        ap.exit(1, f"error: {exc}\n")
    print(f"Wrote extracted data to: {out_dir}")
    print(f"- manifest: {out_dir / 'manifest.json'}")
    print(f"- pages:    {out_dir / 'pages'}")
    print(f"- resources:{out_dir / 'resources'}")
    if not args.no_carve:
        print(f"- carved:   {out_dir / 'carved'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
