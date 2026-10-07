# Verification and limits

There is no compilation or packaging step: these are standalone Python scripts.
The supported syntax baseline is Python 3.10. No pip install is needed.

```powershell
python -m py_compile omt_extract.py omt_imgtext_to_pdf_ocr_md.py reproduce.py
python -m unittest discover -s tests -v
python scripts/check_publication.py --workspace-only
```

After staging, also run `python scripts/check_publication.py` to check the index
and all locally reachable commits. Inspect `git diff --cached` before committing.
The checker enforces a fixed path inventory, not the semantic contents of files.
The allowlist never authorizes putting source-media contents into a source file.

## Automated coverage

Fifteen standard-library unittest cases generate artificial data locally. They
cover page/resource extraction, secondary payloads, BMP wrapping and decoding,
RIFF bounds, filename collisions, unsafe RIFF form names, header/table bounds,
truncated strings, existing-output refusal, CLI success/failure, legacy/indexed
page filenames, Roman/Arabic ordering, duplicate page detection, PDF xref
structure, RLE palette bounds, missing/duplicate disc files, reproduction hashes,
and incomplete status after a failed pipeline stage.

Temporary test files use unique directories under ignored local-only/tests and
are removed after each test. No fixture contains copied CD-ROM content. OCR is
not exercised by the portable suite. The [GitHub workflow](https://github.com/kevinmmccormick/road-behind/actions/runs/37658607025)
passed all four Windows/Linux and Python 3.10/3.14 combinations on October 7, 2026.

## Local verification: 2026-10-07

- Python 3.14.2: syntax compilation and all 15 tests passed.
- Python 3.12.8: all 15 tests passed.
- All four local OMT files passed header/table/payload-span checks.
- Full three-book extraction plus PDF assembly with --no-ocr passed: 280 page
  images, 1,159 output files recorded in the local reproduction report, and a
  16,938,022-byte image PDF. These outputs remain in local-only.
- Windows OCR engine smoke: one real page recognized, yielding 1,091 characters.
  No recognized text is included in this repository.
- The sandbox denies access to Python TemporaryDirectory folders on this
  machine. The engine smoke substituted a precreated workspace directory for
  temporary storage in the test harness only. The production utility still
  uses private temporary storage. Ordinary end-to-end OCR and a full-book OCR
  run have not been verified in this session.
- A separately cached PyMuPDF installation independently opened the rebuilt
  PDF as 280 pages with 280 images. First, middle, and final page renders were
  visually inspected; no rendering defect was observed in those samples. This
  was a sampled check, not proofreading or visual review of all 280 pages.
  PyMuPDF was used only for local verification; it is not a project dependency.

These checks do not establish support for every CD-ROM edition, every OMT
variant, or accurate OCR. The BMP decoder has limited format support and the
RLE decoder tolerates some truncated streams; use trusted source media. Memory
use scales with payload and image sizes, with no hard resource limits. The
image PDF has no searchable text layer. Review generated OCR before quoting it.
