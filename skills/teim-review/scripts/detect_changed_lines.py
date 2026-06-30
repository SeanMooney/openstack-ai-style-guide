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

"""Detect changed line ranges between two git refs.

Used for incremental patchset review: on PS2+, only post inline
comments on lines that changed since the previous patchset.
"""

import argparse
import json
import pathlib
import re
import subprocess
import sys
from typing import Dict, List, Optional


HUNK_RE = re.compile(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@')


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


def detect_changed_lines(
    project_dir: pathlib.Path,
    ref1: str,
    ref2: str = 'HEAD',
) -> Dict[str, List[List[int]]]:
    """Return a mapping of file paths to changed line ranges.

    Each range is [start, end] inclusive.  Runs ``git diff -U0``
    between *ref1* and *ref2* and parses the unified-diff hunk
    headers to extract the new-file line ranges.
    """
    project_dir = project_dir.resolve()
    output = _git_stdout(
        project_dir,
        'diff', '-U0', '--diff-filter=ACMR',
        f'{ref1}..{ref2}',
    )

    changed_lines: Dict[str, List[List[int]]] = {}
    current_file: Optional[str] = None

    for line in output.splitlines():
        if line.startswith('+++ b/'):
            current_file = line[6:]
        elif line.startswith('+++ /dev/null'):
            current_file = None
        else:
            match = HUNK_RE.match(line)
            if match and current_file is not None:
                start = int(match.group(1))
                count = int(match.group(2)) if match.group(2) else 1
                if count == 0:
                    # Pure deletion at this position, no new lines
                    continue
                end = start + count - 1
                changed_lines.setdefault(current_file, []).append(
                    [start, end]
                )

    return changed_lines


def write_changed_lines(
    changed_lines: Dict[str, List[List[int]]],
    output_file: Optional[pathlib.Path],
):
    """Write changed lines to *output_file* as JSON, or stdout."""
    content = json.dumps(changed_lines, indent=2, sort_keys=True) + '\n'
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content)
    else:
        sys.stdout.write(content)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            'Detect changed line ranges between two git refs. '
            'Outputs a JSON mapping of file paths to lists of '
            '[start, end] line ranges.'
        ),
    )
    parser.add_argument('project_dir', type=pathlib.Path)
    parser.add_argument(
        '--ref1',
        required=True,
        help='Base ref (e.g. FETCH_HEAD for previous patchset).',
    )
    parser.add_argument(
        '--ref2',
        default='HEAD',
        help='Target ref (default: HEAD).',
    )
    parser.add_argument(
        '-o',
        '--output',
        type=pathlib.Path,
        help='Output file. Defaults to stdout.',
    )
    return parser.parse_args()


def main() -> int:
    """Run changed-line detection from the command line."""
    args = parse_args()
    try:
        changed_lines = detect_changed_lines(
            args.project_dir,
            ref1=args.ref1,
            ref2=args.ref2,
        )
        write_changed_lines(changed_lines, args.output)
    except RuntimeError as exc:
        sys.stderr.write(f'Error: {exc}\n')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
