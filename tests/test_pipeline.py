from pathlib import Path
import json
import struct
import unittest
from unittest.mock import patch

import omt_extract as omt
import omt_imgtext_to_pdf_ocr_md as pages
import reproduce
import test_omt_extract as extractor_tests
from test_omt_extract import dib, fixture


class PipelineTests(unittest.TestCase):
    setUp = extractor_tests.ExtractorTests.setUp
    cleanup_root = extractor_tests.ExtractorTests.cleanup_root
    def test_pdf_and_page_order(self):
        resources = self.root / 'images' / 'resources'
        resources.mkdir(parents=True)
        bmp = omt._dib_to_bmp(dib())
        for name in ['0001_imgPage10Text__1.bmp', 'imgPage2Text.bmp', '0002_imgPageivText__1.bmp']:
            (resources / name).write_bytes(bmp)
        images = pages._find_page_text_bmps([resources.parent])
        self.assertEqual([p.page_id for p in images], ['iv', '2', '10'])
        self.assertEqual(pages.bmp_to_rgb(bmp), (1, 1, b'\xff\x00\x00'))
        out = self.root / 'pages.pdf'
        pages.build_pdf_from_bmps(images, out)
        data = out.read_bytes()
        self.assertTrue(data.startswith(b'%PDF-1.4'))
        self.assertIn(b'/Count 3', data)
        xref = int(data.split(b'startxref\n')[1].splitlines()[0])
        self.assertTrue(data[xref:].startswith(b'xref\n'))
        lines = data[xref:].splitlines()
        count = int(lines[1].split()[1])
        for i in range(1, count):
            offset = int(lines[2+i].split()[0])
            self.assertTrue(data[offset:].startswith(f'{i} 0 obj'.encode()))
        result = pages.main(['--roots', str(resources.parent), '--out-pdf', str(self.root/'cli.pdf'), '--out-md', str(self.root/'cli.md'), '--no-ocr'])
        self.assertEqual(result, 0)
        self.assertIn('_No text recognized._', (self.root/'cli.md').read_text())

    def test_duplicate_pages(self):
        resources = self.root / 'resources'
        resources.mkdir()
        for name in ['imgPage1Text.bmp', '0000_imgPage1Text__1.bmp']:
            (resources / name).write_bytes(omt._dib_to_bmp(dib()))
        with self.assertRaises(pages.BmpError):
            pages._find_page_text_bmps([self.root])

    def test_reproduction(self):
        source = self.root / 'disc'
        source.mkdir()
        for name in reproduce.BOOK_FILES:
            (source / name.lower()).write_bytes(fixture())
        reproduce.reproduce(source, self.out, extract_only=True)
        record = json.loads((self.out/'reproduction.json').read_text())
        self.assertEqual(record['status'], 'complete')
        self.assertEqual(len(record['inputs']), 3)
        self.assertEqual(len(list(self.out.glob('extracted_*'))), 3)
        for item in record['outputs']:
            self.assertEqual(reproduce.sha256(self.out/item['path']), item['sha256'])
        with self.assertRaises(ValueError):
            reproduce.reproduce(source, self.out, extract_only=True)
        with self.assertRaises(ValueError):
            reproduce.reproduce(source, source/'out', extract_only=True)
        (source/'nested').mkdir()
        (source/'nested'/'BOOK.OMT').write_bytes(fixture())
        with self.assertRaises(ValueError):
            reproduce.find_inputs(source)

    def test_missing_source_files(self):
        with self.assertRaises(ValueError):
            reproduce.find_inputs(self.root)
        with self.assertRaises(ValueError):
            reproduce.find_inputs(self.source)

    def test_reproduction_failure_record(self):
        source = self.root/'disc'
        source.mkdir()
        for name in reproduce.BOOK_FILES:
            (source/name).write_bytes(fixture())
        with patch.object(reproduce.pages, 'main', return_value=2):
            with self.assertRaises(RuntimeError):
                reproduce.reproduce(source, self.out, no_ocr=True)
        record = json.loads((self.out/'reproduction.json').read_text())
        self.assertEqual(record['status'], 'incomplete')

    def test_palette_bounds_and_rle(self):
        header = struct.pack('<IiiHHIIiiII', 40, 2, 1, 1, 8, 1, 4, 0, 0, 2, 0)
        palette = b'\0\0\0\0\0\0\xff\0'
        bmp = omt._dib_to_bmp(header+palette+bytes([2, 1, 0, 1]))
        self.assertEqual(pages.bmp_to_rgb(bmp), (2, 1, b'\xff\0\0'*2))
        bad = omt._dib_to_bmp(header+palette+bytes([2, 3, 0, 1]))
        with self.assertRaises(pages.BmpError):
            pages.bmp_to_rgb(bad)
