"""Synthetic fixtures only: no bytes or text from the companion disc."""
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import shutil
import uuid
import unittest

import omt_extract as omt


def dib():
    return struct.pack('<IiiHHIIiiII', 40, 1, 1, 1, 24, 0, 4, 0, 0, 0, 0) + b'\x00\x00\xff\x00'


def fixture():
    data = bytearray(1536)
    page = b'synthetic\0' + bytes([1, 3, 0, 0]) + struct.pack('<I', 4)
    image = dib()
    first = b'../same\0' + struct.pack('<H', 0x400) + bytes([0, 4, 0, 0]) + struct.pack('<I', len(image))
    first += bytes([0, 5, 0, 0]) + struct.pack('<I', 4)
    second = b'../same\0' + struct.pack('<H', 0) + bytes([0, 5, 0, 0]) + struct.pack('<I', 4)
    table = first + second
    data[:44] = struct.pack('<11I', 1, len(page), 128, 2, len(table), 256, 1, 64, 0, 0, 0)
    data[64:73] = b'fake.dll\0'
    data[128:128+len(page)] = page
    data[256:256+len(table)] = table
    data[768:772] = b'PAGE'
    data[1024:1024+len(image)] = image
    data[1280:1284] = b'RAW!'
    data[1408:1424] = b'RIFF' + struct.pack('<I', 8) + b'WAVEtest'
    return bytes(data)


class ExtractorTests(unittest.TestCase):
    def setUp(self):
        base = (Path(__file__).resolve().parents[1] / 'local-only' / 'tests').resolve()
        self.root = base / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        self.addCleanup(self.cleanup_root, base)
        self.source = self.root / 'synthetic.omt'
        self.source.write_bytes(fixture())
        self.out = self.root / 'out'

    def cleanup_root(self, base):
        if self.root.resolve().parent != base:
            raise RuntimeError('Unexpected test cleanup path')
        shutil.rmtree(self.root)

    def test_end_to_end(self):
        omt.extract_omt(self.source, self.out)
        manifest = json.loads((self.out / 'manifest.json').read_text())
        self.assertEqual(manifest['dlls'], ['fake.dll'])
        self.assertEqual(len(manifest['resources']), 2)
        self.assertEqual(next((self.out / 'pages').glob('*.bin')).read_bytes(), b'PAGE')
        files = list((self.out / 'resources').iterdir())
        self.assertEqual(len(files), 3)
        bmp = next((self.out / 'resources').glob('*.bmp')).read_bytes()
        self.assertEqual(bmp[14:], dib())
        self.assertEqual(struct.unpack_from('<I', bmp, 10)[0], 54)
        self.assertEqual(next((self.out / 'carved').glob('*.wav')).read_bytes(), fixture()[1408:1424])

    def test_raw_flags(self):
        omt.extract_omt(self.source, self.out, carve_riff=False, convert_bmp=False)
        self.assertEqual(len(list((self.out / 'resources').glob('*.bin'))), 3)
        self.assertEqual(list((self.out / 'carved').iterdir()), [])

    def test_existing_output_refused(self):
        self.out.mkdir()
        marker = self.out / 'keep'
        marker.write_text('unchanged')
        with self.assertRaises(omt.OmtFormatError):
            omt.extract_omt(self.source, self.out)
        self.assertEqual(marker.read_text(), 'unchanged')

    def test_corrupt_tables_and_offsets(self):
        for offset, value in [(8, 999999), (4, 1), (0, 999), (16, 1), (12, 999), (36, 999999), (28, 999999), (142, 999999)]:
            with self.subTest(offset=offset):
                data = bytearray(fixture())
                struct.pack_into('<I', data, offset, value)
                self.source.write_bytes(data)
                with self.assertRaises(omt.OmtFormatError):
                    omt.extract_omt(self.source, self.out)
                self.assertFalse(self.out.exists())

    def test_truncated_header(self):
        self.source.write_bytes(b'bad')
        with self.assertRaises(omt.OmtFormatError):
            omt.extract_omt(self.source, self.out)
        self.assertFalse(self.out.exists())

    def test_strings(self):
        self.assertEqual(omt._read_c_string(io.BytesIO(b'\xff\0')), '\xff')
        for value in [b'unterminated', b'abcd\0']:
            with self.assertRaises(omt.OmtFormatError):
                omt._read_c_string(io.BytesIO(value), max_len=3)

    def test_image_detection(self):
        image = dib()
        self.assertEqual(omt.try_extract_dib_bmp(image)[14:], image)
        self.assertEqual(omt.try_extract_dib_bmp(struct.pack('<I', len(image)) + image)[14:], image)
        for raw in [b'', b'garbage!', struct.pack('<I', 40) + b'\0'*8]:
            self.assertIsNone(omt.try_extract_dib_bmp(raw))
        core = struct.pack('<IHHHH', 12, 1, 1, 1, 24) + b'\0'*4
        self.assertEqual(struct.unpack_from('<I', omt._dib_to_bmp(core), 10)[0], 26)

    def test_riff_truncation_and_safe_forms(self):
        self.assertEqual(omt.carve_riff_waves(b'RIFF' + struct.pack('<I', 100) + b'WAVE'), [])
        data = bytearray(fixture())
        data[1416:1420] = b'/../'
        self.source.write_bytes(data)
        omt.extract_omt(self.source, self.out)
        self.assertEqual(len(list((self.out / 'carved').glob('*.riff'))), 1)

    def test_cli(self):
        script = str(Path(omt.__file__).resolve())
        success = subprocess.run([sys.executable, script, str(self.source), '--out', str(self.out), '--no-bmp', '--no-carve'], capture_output=True, text=True)
        self.assertEqual(success.returncode, 0, success.stderr)
        failed = subprocess.run([sys.executable, script, str(self.source), '--out', str(self.out)], capture_output=True, text=True)
        self.assertEqual(failed.returncode, 1)
        self.assertIn('error:', failed.stderr)
        self.assertNotIn('Traceback', failed.stderr)


if __name__ == '__main__':
    unittest.main()
