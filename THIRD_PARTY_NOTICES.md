# Dependencies and provenance

## Project source

The starting workspace contained one standalone `omt_extract.py`, a short
README, a separate OCR/PDF script, original media, and extracted derivatives.
There was no Git history, license, attribution header, package manifest, or
vendored library in the extractor. Its filesystem timestamp was December 12,
2025; this is evidence about the file, not proof of authorship or creation date.
No copied third-party source was identified by inspection. Complete historical
provenance cannot be independently established from this workspace.

MIT was selected for the owner's extractor code and documentation. The cleanup
follows zipdrivesacar's source-only publication and explicit dependency review.
That project's GPL choice reflected its DASM headers; none are included here.
The [MIT license](https://opensource.org/license/mit) permits reuse subject to
retaining the license and copyright notice.

## Dependency inventory

| Component | Role | Bundled? | License / source |
| --- | --- | --- | --- |
| Python 3.10+ and standard library | Runtime; unittest and py_compile for verification | No | [PSF license and incorporated notices](https://docs.python.org/3/license.html) |
| Git | Publication inventory check and version control | No | [GPLv2](https://git-scm.com/about/free-and-open-source) |
| GitHub CLI | Optional repository publication | No | [MIT](https://github.com/cli/cli/blob/trunk/LICENSE) |

The extractor imports only Python standard-library modules. There are zero
third-party pip requirements and no vendored dependencies. No Python runtime
is redistributed. The included PDF/OCR utility is assessed below.
DLL names read from a container
are metadata, not runtime dependencies.

## Excluded material

All existing OMT, XVD, and COL files; extracted image/audio/raw resource trees;
OCR Markdown; and generated PDFs are retained only under the ignored local
quarantine. They are not covered by the project license or redistributed.
No ownership, trademark clearance, or permission to redistribute those works
is asserted. Synthetic test payloads are authored for this project and do not
contain excerpts or bytes copied from the CD-ROM.

## Included PDF/OCR utility

`omt_imgtext_to_pdf_ocr_md.py` has no third-party Python imports or vendored library. Its BMP decoder and
PDF writer were already present in the workspace, without attribution or
history; the same provenance limits apply as for the extractor. The source is
included under the project's MIT license. PDF generation uses Python zlib;
no PDF engine or font is bundled.

OCR optionally invokes separately installed Windows PowerShell 5.1 and
[Windows.Media.Ocr](https://learn.microsoft.com/en-us/uwp/api/windows.media.ocr.ocrengine).
These are Microsoft system components governed by their own product terms,
not relicensed or redistributed here. Available recognition languages depend
on the local Windows installation. No Tesseract, Pillow, PyMuPDF, or online OCR
service is required. The reproduction script uses the same dependencies.

The CI workflow uses GitHub's actions/checkout and actions/setup-python as
external development services (MIT-licensed upstream actions, not vendored).

## Local verification tools

A separately installed/cached PyMuPDF 1.28.2 was used to read the owner-provided
conversation PDF and independently inspect sample pages of the rebuilt PDF.
Its package metadata identifies dual licensing under GNU AGPL 3.0 or an Artifex
commercial license. It is not imported by the project, installed by its CI,
or bundled in its source or outputs. No PyMuPDF code is copied here; the
project's own PDF writer uses only the Python standard library.

The owner-supplied December 2025 conversation documents AI-assisted creation
of the original extractor and PDF/OCR pipeline. The October 2026 README essay
is an explicitly labeled AI-written adaptation with primary-source links for
current claims. The underlying conversation PDF remains private to this
workspace's ignored local-only directory. Its speculative format attributions
are not treated as an authoritative OMT specification.
