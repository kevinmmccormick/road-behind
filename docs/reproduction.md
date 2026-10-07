# Reproducing the local outputs

Use your own original companion CD-ROM image. Mount it with your operating
system or unpack it using a tool you trust, then provide the resulting directory.
This script does not download media, mount images, execute the disc software,
or bypass access controls. A raw ISO/BIN/CUE file is not accepted directly.

```powershell
python reproduce.py 'D:\' --out local-only/reproduced
```

The script recursively locates exactly one of each of BOOK.OMT, BOOK2.OMT, and
BOOK3.OMT, extracts them, orders page-text images (Roman-numbered front matter
first, followed by Arabic page numbers), writes pages.pdf, and uses local Windows
OCR to write pages.md. Duplicate or missing book containers and duplicate page
IDs are errors. The output directory must be new and outside the source tree.
OTHER.OMT and unrelated disc files are not part of this book reconstruction;
the standalone extractor can inspect additional OMT containers separately.

On Windows, OCR requires Windows PowerShell 5.1 (`powershell.exe`), WinRT
Windows.Media.Ocr, and an installed recognizer language matching the user
profile. It does not call an online OCR service. OCR quality and exact text
can vary with Windows version and installed language packs.

For an image PDF without OCR, on Windows, Linux, or macOS:

```sh
python reproduce.py /path/to/mounted-disc --out local-only/reproduced --no-ocr
```

`--no-ocr` produces placeholder Markdown. `--extract-only` skips both PDF and
Markdown. The PDF contains page images, not searchable OCR text. For direct
control of existing extraction roots:

```powershell
python omt_imgtext_to_pdf_ocr_md.py --roots local-only/reproduced/extracted_BOOK local-only/reproduced/extracted_BOOK2 local-only/reproduced/extracted_BOOK3 --out-pdf local-only/another.pdf --out-md local-only/another.md --no-ocr
```

The utility accepts both legacy imgPage1Text.bmp filenames and the extractor's
new indexed names. --limit N selects the first N ordered pages for a smoke test.

reproduction.json records input SHA-256 values, Python/platform information,
options, and hashes of all resulting files. Status changes to complete only
after the whole requested pipeline succeeds. Failures can leave partial output;
retain it for diagnosis and use a new directory when retrying. This record and
all output stay local. Paths in manifests and Markdown, OCR engine versions,
and source editions can affect byte-for-byte comparisons. No canonical disc
hash or universal edition compatibility is asserted.
