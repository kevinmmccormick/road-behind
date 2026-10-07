# Publication preparation: 2026-10-07

Project name: **Road Behind**. Intended repository:
`kevinmmccormick/road-behind`. GitHub name availability has not been confirmed.
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

The initial session blocked Git staging and outbound GitHub access. After the
owner revised the permission model, staging and authenticated GitHub access
succeeded. The staged inventory contains exactly 19 approved source and
documentation files; no local-only material is included. Publication is in
progress; the result and hosted validation will be recorded after the push.

When running in a session that permits Git metadata writes and GitHub access:

```powershell
python scripts/check_publication.py --workspace-only
python -m unittest discover -s tests -v
git add --all
python scripts/check_publication.py
git diff --cached --check
git diff --cached
git commit -m "Prepare Road Behind extractor and reproduction tools"
python scripts/check_publication.py
gh repo create kevinmmccormick/road-behind --public --source . --remote origin --push --description "Extract and revisit the OMT contents of The Road Ahead companion CD-ROM"
```

Review the staged diff before committing. If the intended repository already
exists, inspect its ownership and contents before selecting a remote or another
name. After pushing, verify repository visibility, published file inventory,
and the Windows/Linux CI results. Keep release artifacts source-only. There
is no stable release tag in this cleanup.
