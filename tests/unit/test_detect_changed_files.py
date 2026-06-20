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

"""Tests for deterministic teim-review changed-file detection."""

import pathlib
import subprocess
import tempfile

from testtools import matchers

from tests import test


class TestDetectChangedFiles(test.NoDBTestCase):
    """Test cases for the skill-bundled changed-file helper."""

    def setUp(self):
        super().setUp()
        self.detect_changed_files = test.load_script(
            'skills/teim-review/scripts/detect_changed_files.py'
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

    def test_detects_last_commit_files_sorted(self):
        repo = self._make_repo()
        self._write(repo, 'unchanged.txt', 'base\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'base')

        self._write(repo, 'zeta.txt', 'new\n')
        self._write(repo, 'alpha.txt', 'new\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'change')

        result = self.detect_changed_files.detect_changed_files(repo)

        self.assertThat(result, matchers.Equals(['alpha.txt', 'zeta.txt']))

    def test_detects_uncommitted_and_untracked_files(self):
        repo = self._make_repo()
        self._write(repo, 'tracked.txt', 'base\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'base')

        self._write(repo, 'tracked.txt', 'changed\n')
        self._write(repo, 'new.txt', 'new\n')

        result = self.detect_changed_files.detect_changed_files(
            repo, uncommitted_only=True
        )

        self.assertThat(result, matchers.Equals(['new.txt', 'tracked.txt']))

    def test_root_commit_requires_explicit_allow(self):
        repo = self._make_repo()
        self._write(repo, 'b.txt', 'base\n')
        self._write(repo, 'a.txt', 'base\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'base')

        self.assertRaises(
            RuntimeError,
            self.detect_changed_files.detect_changed_files,
            repo,
        )

    def test_root_commit_can_explicitly_use_tracked_files(self):
        repo = self._make_repo()
        self._write(repo, 'b.txt', 'base\n')
        self._write(repo, 'a.txt', 'base\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'base')

        result = self.detect_changed_files.detect_changed_files(
            repo,
            allow_root_commit=True,
        )

        self.assertThat(result, matchers.Equals(['a.txt', 'b.txt']))

    def test_missing_base_ref_fails(self):
        repo = self._make_repo()
        self._write(repo, 'tracked.txt', 'base\n')
        self._run(repo, 'add', '.')
        self._run(repo, 'commit', '-m', 'base')

        self.assertRaises(
            RuntimeError,
            self.detect_changed_files.detect_changed_files,
            repo,
            base_ref='origin/missing',
        )
