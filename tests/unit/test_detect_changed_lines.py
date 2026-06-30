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

"""Tests for inter-patchset changed-line detection."""

import pathlib
import subprocess
import tempfile

from testtools import matchers

from tests import test


class TestDetectChangedLines(test.NoDBTestCase):
    """Test cases for detect_changed_lines.py."""

    def setUp(self):
        super().setUp()
        self.mod = test.load_script(
            'skills/teim-review/scripts/detect_changed_lines.py'
        )

    def _run(self, repo, *args):
        subprocess.run(  # noqa: S603
            ['git', *args],  # noqa: S607
            cwd=str(repo),
            text=True,
            capture_output=True,
            check=True,
        )

    def _write(self, repo, path, content):
        file_path = repo / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    def _make_repo(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        repo = pathlib.Path(tmpdir.name)
        self._run(repo, 'init')
        self._run(repo, 'config', 'user.email', 'test@example.com')
        self._run(repo, 'config', 'user.name', 'Test User')
        return repo

    def test_single_file_single_hunk(self):
        repo = self._make_repo()
        self._write(repo, 'a.py', 'line1\nline2\nline3\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'base')
        base_ref = subprocess.run(  # noqa: S603
            ['git', 'rev-parse', 'HEAD'],  # noqa: S607
            cwd=str(repo), text=True, capture_output=True, check=True,
        ).stdout.strip()

        self._write(repo, 'a.py', 'line1\nchanged\nline3\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'change')

        result = self.mod.detect_changed_lines(repo, ref1=base_ref)
        self.assertIn('a.py', result)
        self.assertThat(result['a.py'], matchers.Equals([[2, 2]]))

    def test_multiple_files(self):
        repo = self._make_repo()
        self._write(repo, 'a.py', 'aaa\n')
        self._write(repo, 'b.py', 'bbb\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'base')
        base_ref = subprocess.run(  # noqa: S603
            ['git', 'rev-parse', 'HEAD'],  # noqa: S607
            cwd=str(repo), text=True, capture_output=True, check=True,
        ).stdout.strip()

        self._write(repo, 'a.py', 'AAA\n')
        self._write(repo, 'b.py', 'BBB\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'change')

        result = self.mod.detect_changed_lines(repo, ref1=base_ref)
        self.assertIn('a.py', result)
        self.assertIn('b.py', result)

    def test_file_added(self):
        repo = self._make_repo()
        self._write(repo, 'existing.py', 'ok\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'base')
        base_ref = subprocess.run(  # noqa: S603
            ['git', 'rev-parse', 'HEAD'],  # noqa: S607
            cwd=str(repo), text=True, capture_output=True, check=True,
        ).stdout.strip()

        self._write(repo, 'new.py', 'line1\nline2\nline3\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'add')

        result = self.mod.detect_changed_lines(repo, ref1=base_ref)
        self.assertIn('new.py', result)
        self.assertThat(result['new.py'], matchers.Equals([[1, 3]]))
        self.assertNotIn('existing.py', result)

    def test_file_deleted_not_in_output(self):
        repo = self._make_repo()
        self._write(repo, 'a.py', 'content\n')
        self._write(repo, 'b.py', 'content\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'base')
        base_ref = subprocess.run(  # noqa: S603
            ['git', 'rev-parse', 'HEAD'],  # noqa: S607
            cwd=str(repo), text=True, capture_output=True, check=True,
        ).stdout.strip()

        self._run(repo, 'rm', 'a.py')
        self._run(repo, 'commit', '-m', 'delete')

        result = self.mod.detect_changed_lines(repo, ref1=base_ref)
        self.assertNotIn('a.py', result)

    def test_multiple_hunks(self):
        repo = self._make_repo()
        lines = [f'line{i}\n' for i in range(1, 11)]
        self._write(repo, 'a.py', ''.join(lines))
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'base')
        base_ref = subprocess.run(  # noqa: S603
            ['git', 'rev-parse', 'HEAD'],  # noqa: S607
            cwd=str(repo), text=True, capture_output=True, check=True,
        ).stdout.strip()

        lines[1] = 'CHANGED2\n'
        lines[7] = 'CHANGED8\n'
        self._write(repo, 'a.py', ''.join(lines))
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'change')

        result = self.mod.detect_changed_lines(repo, ref1=base_ref)
        self.assertIn('a.py', result)
        self.assertThat(result['a.py'], matchers.Equals([[2, 2], [8, 8]]))

    def test_no_changes(self):
        repo = self._make_repo()
        self._write(repo, 'a.py', 'content\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'base')
        base_ref = subprocess.run(  # noqa: S603
            ['git', 'rev-parse', 'HEAD'],  # noqa: S607
            cwd=str(repo), text=True, capture_output=True, check=True,
        ).stdout.strip()

        result = self.mod.detect_changed_lines(repo, ref1=base_ref)
        self.assertThat(result, matchers.Equals({}))
