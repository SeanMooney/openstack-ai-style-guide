# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#      Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Generate the deterministic changed-file list used by teim-review."""

import argparse
import pathlib
import subprocess
import sys
from typing import Iterable, List, Optional


def _git(project_dir: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(  # noqa: S603
        ['git', *args],  # noqa: S607
        cwd=str(project_dir),
        text=True,
        capture_output=True,
        check=False,
    )


def _git_stdout(project_dir: pathlib.Path, *args: str) -> str:
    result = _git(project_dir, *args)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or 'git command failed')
    return result.stdout


def _ref_exists(project_dir: pathlib.Path, ref: str) -> bool:
    return _git(project_dir, 'rev-parse', '--verify', '--quiet', ref).returncode == 0


def _normalize_paths(paths: Iterable[str]) -> List[str]:
    changed_files = set()
    for path in paths:
        path = path.strip()
        if path:
            changed_files.add(path)
    return sorted(changed_files)


def detect_changed_files(
    project_dir: pathlib.Path,
    base_ref: Optional[str] = None,
    uncommitted_only: bool = False,
    allow_root_commit: bool = False,
) -> List[str]:
    """Return sorted changed files for the requested review scope."""
    project_dir = project_dir.resolve()
    if not (project_dir / '.git').exists():
        _git_stdout(project_dir, 'rev-parse', '--show-toplevel')

    if uncommitted_only:
        output = _git_stdout(
            project_dir, 'diff', '--name-only', '--diff-filter=ACMR', 'HEAD'
        )
        untracked = _git_stdout(
            project_dir,
            'ls-files',
            '--others',
            '--exclude-standard',
        )
        return _normalize_paths([*output.splitlines(), *untracked.splitlines()])

    if base_ref:
        if not _ref_exists(project_dir, base_ref):
            raise RuntimeError(f'base ref not found: {base_ref}')
        merge_base = _git_stdout(project_dir, 'merge-base', 'HEAD', base_ref).strip()
        output = _git_stdout(
            project_dir,
            'diff',
            '--name-only',
            '--diff-filter=ACMR',
            f'{merge_base}..HEAD',
        )
        return _normalize_paths(output.splitlines())

    if _ref_exists(project_dir, 'HEAD^'):
        output = _git_stdout(
            project_dir,
            'diff',
            '--name-only',
            '--diff-filter=ACMR',
            'HEAD^..HEAD',
        )
        return _normalize_paths(output.splitlines())

    if allow_root_commit:
        output = _git_stdout(project_dir, 'ls-files')
        return _normalize_paths(output.splitlines())

    raise RuntimeError(
        'cannot determine changed files because HEAD^ is not available; '
        'use --allow-root-commit only when treating all tracked files as '
        'intentionally in scope'
    )


def write_changed_files(changed_files: List[str], output_file: Optional[pathlib.Path]):
    """Write changed files to output_file, or stdout when output_file is unset."""
    content = ''.join(f'{path}\n' for path in changed_files)
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content)
    else:
        sys.stdout.write(content)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Write a sorted newline-delimited changed-file list.'
    )
    parser.add_argument('project_dir', type=pathlib.Path)
    parser.add_argument(
        '-o',
        '--output',
        type=pathlib.Path,
        help='Output file. Defaults to stdout.',
    )
    parser.add_argument(
        '--base-ref',
        help='Optional base ref. If present locally, diff from merge-base.',
    )
    parser.add_argument(
        '--uncommitted-only',
        action='store_true',
        help='Use staged, unstaged, and untracked files instead of commit history.',
    )
    parser.add_argument(
        '--allow-root-commit',
        action='store_true',
        help='Allow a root commit to report all tracked files as changed.',
    )
    return parser.parse_args()


def main() -> int:
    """Run changed-file detection from the command line."""
    args = parse_args()
    try:
        changed_files = detect_changed_files(
            args.project_dir,
            base_ref=args.base_ref,
            uncommitted_only=args.uncommitted_only,
            allow_root_commit=args.allow_root_commit,
        )
        write_changed_files(changed_files, args.output)
    except RuntimeError as exc:
        sys.stderr.write(f'Error: {exc}\n')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
