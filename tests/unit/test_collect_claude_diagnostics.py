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

"""Tests for session-scoped Claude CI diagnostic collection."""

import json
import tempfile
import uuid
from pathlib import Path

from tests import test


class TestCollectClaudeDiagnostics(test.NoDBTestCase):
    """Retain partial and retried sessions without copying unrelated files."""

    def setUp(self):
        super().setUp()
        self.collector = test.load_script(
            'roles/ai_code_review/files/collect_claude_diagnostics.py'
        )
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.config = self.root / 'config'
        self.project = self.config / 'projects' / '-work-project'
        self.project.mkdir(parents=True)
        self.output = self.root / 'output'
        self.output.mkdir()
        self.session = str(uuid.uuid4())

    def _write(self, path, content='partial transcript'):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def _index(self, *sessions):
        self._write(self.output / 'session-ids.txt', '\n'.join(sessions) + '\n')

    def test_collects_only_current_session_and_subagents(self):
        self._index(self.session)
        self._write(self.project / f'{self.session}.jsonl')
        subagents = self.project / self.session / 'subagents'
        self._write(subagents / 'agent-abc.jsonl')
        self._write(subagents / 'agent-abc.meta.json', '{}')
        self._write(subagents / 'unrelated.txt')
        self._write(self.project / f'{uuid.uuid4()}.jsonl')
        self._write(self.config / 'settings.json', 'private settings')
        self._write(self.config / '.credentials.json', 'credentials')

        summary = self.collector.collect(self.config, self.output)

        self.assertEqual(3, len(summary['sessions'][0]['files']))
        files = [p for p in (self.output / 'sessions').rglob('*') if p.is_file()]
        self.assertEqual(3, len(files))
        self.assertEqual(
            'partial transcript',
            (self.output / 'sessions' / self.project.name
             / f'{self.session}.jsonl').read_text(),
        )

    def test_retains_retry_sessions_and_partial_json(self):
        retry = str(uuid.uuid4())
        self._index(self.session, retry, retry)
        self._write(self.project / f'{self.session}.jsonl', '{unfinished')
        self._write(self.project / f'{retry}.jsonl', '{}\n')

        summary = self.collector.collect(self.config, self.output)

        self.assertEqual(2, len(summary['sessions']))
        self.assertTrue(all(s['files'] for s in summary['sessions']))

    def test_missing_transcripts_are_reported_without_failing(self):
        self._index(self.session)

        summary = self.collector.collect(self.config, self.output)

        self.assertEqual(
            [{'session_id': self.session, 'files': []}], summary['sessions']
        )

    def test_collection_before_claude_started_is_empty(self):
        summary = self.collector.collect(self.config, self.output)

        self.assertEqual([], summary['sessions'])
        self.assertEqual(
            summary, json.loads((self.output / 'collection.json').read_text())
        )

    def test_invalid_session_ids_cannot_escape_projects(self):
        self._index('../settings', self.session)
        self._write(self.config / 'settings.json', 'private settings')

        summary = self.collector.collect(self.config, self.output)

        self.assertEqual(['../settings'], summary['invalid_session_ids'])
        self.assertEqual(1, len(summary['sessions']))
        self.assertEqual([], summary['sessions'][0]['files'])

    def test_symlinked_transcripts_are_not_copied(self):
        self._index(self.session)
        private = self.config / '.credentials.json'
        self._write(private, 'credentials')
        (self.project / f'{self.session}.jsonl').symlink_to(private)
        (self.project / self.session).symlink_to(self.config, target_is_directory=True)

        summary = self.collector.collect(self.config, self.output)

        self.assertEqual([], summary['sessions'][0]['files'])
