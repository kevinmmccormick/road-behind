# Publication preparation: 2026-10-07

Project name: **Road Behind**. Published public repository:
[kevinmmccormick/road-behind](https://github.com/kevinmmccormick/road-behind).
License: MIT for project source, synthetic tests, and documentation.

## Scope and provenance

This cleanup follows the source-only publication approach used for
[zipdrivesacar](https://github.com/kevinmmccormick/zipdrivesacar): inspect the
existing workspace, assess dependencies, document actual capabilities and
limits, verify locally, and publish only reviewed source. The original extractor
had no Git history or license and carried a December 2025 filesystem timestamp.
No third-party Python package or bundled library was found. See the
[license assessment](../THIRD_PARTY_NOTICES.md).

Included: OMT extractor, the existing PDF/Windows OCR companion utility, a new
mounted-disc reproduction script, synthetic tests, CI, and documentation.
Excluded: unrelated formats/components and all disc content or derivatives.
The README includes a revised essay based on the owner-supplied December 2025
conversation, with dated primary sources for the October 2026 comparison. The
source conversation PDF and its extracted text remain under local-only; no
book excerpts or conversation dump are in the publication inventory.

## Local material boundary

Before Git initialization, the original four OMT containers, 17 XVD files,
one COL file, three extraction trees, six PDFs, and six generated Markdown
files were moved intact under local-only/copyrighted. Original source/README
copies and the original companion utility are preserved under local-only too.
The new reproduction and OCR verification outputs remain there as well.
This is organizational separation and Git exclusion, not encryption or an
access-control boundary.

.gitignore denies new paths by default and permits only named project files.
scripts/check_publication.py independently checks the approved inventory,
ignore behavior, and (after staging) all locally reachable commit trees.
No source media was staged or committed. Do not force-add files from local-only,
attach them to issues, or upload local reproduction reports as release assets.

## Changes and validation

Extraction now refuses existing output directories, uses indexed resource names
to prevent collisions, sanitizes RIFF form names, and bounds table parsing.
The PDF utility recognizes indexed and legacy filenames, rejects duplicate
page IDs and output overwrites, checks palette indices, and reports OCR errors.
Reproduction discovers the three book containers, records local hashes, and
marks its report complete only after requested outputs are successfully written.
[Testing notes](testing.md) record actual results and outstanding checks.

## Publication status

Published publicly on October 7, 2026. After the owner revised the permission
model, Git staging and authenticated GitHub access succeeded. Initial source
commit: `e0c419dcee24d9c1b2f00db08c5c07476d45b7c7`.

The index and reachable history audit passed with exactly 19 approved project
files. GitHub's published tree was checked; local-only, original media, extracted
assets, PDFs, and OCR text are absent. GitHub identifies the license as MIT.

The initial [Verify run](https://github.com/kevinmmccormick/road-behind/actions/runs/37658607025)
passed on Windows and Linux with Python 3.10 and 3.14. Each job runs syntax
compilation, the 15 synthetic tests, and the publication inventory/history check.
The repository has no stable release tag or bundled media release.

For subsequent publication, run the checks documented in testing.md, inspect
the staged diff, commit only reviewed changes, and push main. Keep release
artifacts source-only. The fixed allowlist must be deliberately updated when
adding a new project file; never bypass it to include local source media.
