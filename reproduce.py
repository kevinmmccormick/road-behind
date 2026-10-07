#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Rebuild local extraction/PDF/OCR outputs from a mounted companion disc."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import sys

from omt_extract import extract_omt
import omt_imgtext_to_pdf_ocr_md as pages

BOOK_FILES = ('BOOK.OMT', 'BOOK2.OMT', 'BOOK3.OMT')


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def find_inputs(source: Path) -> list[Path]:
    if not source.is_dir():
        raise ValueError('Source must be a mounted CD-ROM or extracted image directory')
    candidates = {name: [] for name in BOOK_FILES}
    for path in source.rglob('*'):
        if path.is_file() and path.name.upper() in candidates:
            resolved = path.resolve()
            if not resolved.is_relative_to(source.resolve()):
                raise ValueError('Input symlink points outside the source directory')
            candidates[path.name.upper()].append(path)
    for name, matches in candidates.items():
        if len(matches) != 1:
            raise ValueError(f'Expected exactly one {name}; found {len(matches)}')
    return [candidates[name][0] for name in BOOK_FILES]


def reproduce(source: Path, output: Path, *, extract_only: bool = False, no_ocr: bool = False) -> None:
    source, output = source.resolve(), output.resolve()
    if output.is_relative_to(source):
        raise ValueError('Output must be outside the source directory')
    if output.exists():
        raise ValueError('Output already exists; choose a fresh destination')
    inputs = find_inputs(source)
    if not extract_only and not no_ocr and sys.platform != 'win32':
        raise ValueError('Windows OCR requires Windows; use --no-ocr or --extract-only')
    output.mkdir(parents=True)
    record = {
        'status': 'incomplete',
        'python': platform.python_version(),
        'platform': platform.platform(),
        'extract_only': extract_only,
        'ocr': not extract_only and not no_ocr,
        'inputs': [{'path': p.relative_to(source).as_posix(), 'sha256': sha256(p)} for p in inputs],
    }
    report = output / 'reproduction.json'
    report.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    roots = []
    for name, path in zip(BOOK_FILES, inputs):
        root = output / f'extracted_{Path(name).stem}'
        extract_omt(path, root)
        roots.append(root)
    if not extract_only:
        args = ['--roots', *map(str, roots), '--out-pdf', str(output / 'pages.pdf'),
                '--out-md', str(output / 'pages.md')]
        if no_ocr:
            args.append('--no-ocr')
        result = pages.main(args)
        if result:
            raise RuntimeError(f'Page assembly failed (exit {result})')
    record['outputs'] = [
        {'path': p.relative_to(output).as_posix(), 'sha256': sha256(p)}
        for p in sorted(output.rglob('*')) if p.is_file() and p != report
    ]
    record['status'] = 'complete'
    report.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Mounted disc or unpacked image directory (not an ISO file)')
    parser.add_argument('--out', type=Path, default=Path('local-only/reproduced'))
    parser.add_argument('--extract-only', action='store_true', help='Only extract the three book containers')
    parser.add_argument('--no-ocr', action='store_true', help='Build image PDF and placeholder Markdown without Windows OCR')
    args = parser.parse_args(argv)
    try:
        reproduce(args.source, args.out, extract_only=args.extract_only, no_ocr=args.no_ocr)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f'error: {exc}\n')
    print(f'Completed local reproduction: {args.out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
