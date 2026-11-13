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

"""Molecule Claude fixture: preserve diagnostics, fail once, then succeed."""

import json
import os
import sys
from pathlib import Path


def main():
    """Consume the production role's session and debug arguments."""
    args = sys.argv[1:]
    session = args[args.index('--session-id') + 1]
    debug = Path(args[args.index('--debug-file') + 1])
    debug.write_text(f'Debug output for {session}\n')
    project = Path(os.environ['CLAUDE_CONFIG_DIR']) / 'projects' / '-fixture'
    project.mkdir(parents=True, exist_ok=True)
    (project / f'{session}.jsonl').write_text('{partial main transcript')
    subagents = project / session / 'subagents'
    subagents.mkdir(parents=True)
    (subagents / 'agent-reviewer.jsonl').write_text('reviewer transcript\n')
    attempts = (debug.parent / 'session-ids.txt').read_text().splitlines()
    if len(attempts) == 1:
        sys.stderr.write('Temporary fixture failure\n')
        return 1
    sys.stdout.write(json.dumps({
        'type': 'result', 'session_id': session,
        'structured_output': {'test': 'pass'},
    }) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
