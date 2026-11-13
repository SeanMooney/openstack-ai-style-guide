# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Collect only transcripts belonging to this CI review's Claude attempts."""

import argparse
import json
import shutil
import uuid
from pathlib import Path


def collect(config_dir: Path, diagnostics_dir: Path) -> dict:
    """Copy indexed session transcripts, tolerating missing/partial sessions."""
    diagnostics_dir.mkdir(parents=True, exist_ok=True)
    index = diagnostics_dir / 'session-ids.txt'
    ids = index.read_text().splitlines() if index.is_file() else []
    projects = config_dir / 'projects'
    summary = {'sessions': [], 'invalid_session_ids': []}
    for session in dict.fromkeys(ids):
        try:
            if str(uuid.UUID(session)) != session:
                raise ValueError('non-canonical UUID')
        except ValueError:
            summary['invalid_session_ids'].append(session)
            continue
        copied = []
        for project in sorted(projects.glob('*')):
            if not project.is_dir() or project.is_symlink():
                continue
            candidates = [project / f'{session}.jsonl']
            subagents = project / session / 'subagents'
            if not (project / session).is_symlink() and not subagents.is_symlink():
                candidates.extend(sorted(subagents.glob('agent-*.jsonl')))
                candidates.extend(sorted(subagents.glob('agent-*.meta.json')))
            for source in candidates:
                if not source.is_file() or source.is_symlink():
                    continue
                relative = source.relative_to(projects)
                destination = diagnostics_dir / 'sessions' / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
                copied.append(str(relative))
        summary['sessions'].append({'session_id': session, 'files': copied})
    (diagnostics_dir / 'collection.json').write_text(
        json.dumps(summary, indent=2) + '\n', encoding='utf-8'
    )
    return summary


def main():
    """Collect transcripts in post-run, even without a final Claude result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-dir', type=Path, required=True)
    parser.add_argument('--diagnostics-dir', type=Path, required=True)
    args = parser.parse_args()
    summary = collect(args.config_dir, args.diagnostics_dir)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
