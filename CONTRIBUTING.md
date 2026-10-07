# Contributing

Use Python 3.10+ and run the README verification commands before submitting.
Keep changes focused on OMT extraction. Add synthetic regression tests for
parser changes, especially offsets, truncation, naming, and output safety.

Do not commit disc files, extracted assets, OCR text, PDFs, screenshots of book
pages, or real-data manifests. Reproduce issues with fabricated minimal inputs.
The Git ignore list and publication checker must be deliberately updated when
adding a reviewed source file. Do not use `git add -f` to bypass the quarantine.
Contributions are under the project's MIT license.
