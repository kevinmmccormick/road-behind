"""Fail closed if the Git index or history contains an unreviewed path."""
from pathlib import Path
import argparse
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    '.gitignore', '.gitattributes', 'omt_extract.py', 'README.md', 'LICENSE',
    'COPYRIGHT', 'THIRD_PARTY_NOTICES.md', 'CONTRIBUTING.md', 'SECURITY.md',
    'tests/test_omt_extract.py', 'scripts/check_publication.py',
    'docs/format.md', 'docs/testing.md', 'docs/publication.md',
    'omt_imgtext_to_pdf_ocr_md.py', 'reproduce.py', 'docs/reproduction.md',
    'tests/test_pipeline.py', '.github/workflows/test.yml',
}


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args]).decode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace-only', action='store_true', help='Check publishable files and ignores before staging; does not audit history')
    args = parser.parse_args()
    for name in ALLOWED:
        path = ROOT / name
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise SystemExit(f'Missing or unsafe publication source: {name}')
    probes = ['local-only/copyrighted/BOOK.OMT', 'BOOK.OMT', 'book.pdf', 'extracted_BOOK/manifest.json', 'unreviewed.md']
    for path in probes:
        subprocess.run(['git', '-C', str(ROOT), 'check-ignore', '-q', path], check=True)
    if args.workspace_only:
        visible = set(filter(None, git('ls-files', '--cached', '--others', '--exclude-standard', '-z').split('\0')))
        if visible != ALLOWED:
            raise SystemExit(f'Workspace inventory mismatch: extra={sorted(visible-ALLOWED)}, missing={sorted(ALLOWED-visible)}')
        print(f'PASS: {len(visible)} publishable paths; quarantine ignored. Index/history not audited.')
        return
    indexed = set(filter(None, git('ls-files', '-z').split('\0')))
    if indexed != ALLOWED:
        raise SystemExit(f'Publication inventory mismatch: extra={sorted(indexed-ALLOWED)}, missing={sorted(ALLOWED-indexed)}')
    commits = git('rev-list', '--all').splitlines()
    for commit in commits:
        names = set(filter(None, git('ls-tree', '-r', '--name-only', '-z', commit).split('\0')))
        if names - ALLOWED:
            raise SystemExit(f'Unapproved paths in history: {commit}: {sorted(names-ALLOWED)}')
    print(f'PASS: {len(indexed)} reviewed paths; {len(commits)} commits checked; quarantine ignored.')
    print('Path checks supplement manual staged-content review; they do not prove provenance.')


if __name__ == '__main__':
    main()
