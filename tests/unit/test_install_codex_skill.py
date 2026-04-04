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

"""Tests for the Codex plugin installer helper."""

import json
import pathlib
import subprocess

import fixtures
from testtools import matchers

from tests import test


class TestInstallCodexSkill(test.NoDBTestCase):
    """Verify installer safety and marketplace handling."""

    def setUp(self):
        super().setUp()
        self.repo_root = pathlib.Path(__file__).resolve().parents[2]
        self.script = self.repo_root / 'scripts' / 'install-codex-skill'
        self.tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        self.codex_home = self.tempdir / 'codex-home'
        self.agents_home = self.tempdir / 'agents-home'
        self.marketplace_file = (
            self.agents_home / 'plugins' / 'marketplace.json'
        )

    def _run_installer(self):
        env = {
            'HOME': str(self.tempdir),
            'CODEX_HOME': str(self.codex_home),
            'AGENTS_HOME': str(self.agents_home),
        }
        return subprocess.run(  # noqa: S603
            [str(self.script)],
            cwd=self.repo_root,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_installer_creates_marketplace_with_absolute_plugin_path(self):
        """A fresh install should create a marketplace pointing at the target."""
        result = self._run_installer()

        self.assertThat(result.returncode, matchers.Equals(0))
        marketplace = json.loads(self.marketplace_file.read_text())
        plugin = marketplace['plugins'][0]

        self.assertThat(
            plugin['source']['path'],
            matchers.Equals(str(self.codex_home / 'plugins' / 'teim-review')),
        )
        self.assertTrue((self.codex_home / 'plugins' / 'teim-review').exists())

    def test_installer_preserves_metadata_and_unrelated_plugins(self):
        """Existing marketplace state should be preserved during install."""
        self.marketplace_file.parent.mkdir(parents=True, exist_ok=True)
        other_plugin_path = self.tempdir / 'other-plugin'
        stale_path = self.tempdir / 'stale-path'
        self.marketplace_file.write_text(
            json.dumps(
                {
                    'name': 'custom-marketplace',
                    'interface': {'displayName': 'Custom Plugins'},
                    'plugins': [
                        {
                            'name': 'other-plugin',
                            'source': {
                                'source': 'local',
                                'path': str(other_plugin_path),
                            },
                            'policy': {
                                'installation': 'AVAILABLE',
                                'authentication': 'ON_INSTALL',
                            },
                            'category': 'Developer Tools',
                        },
                        {
                            'name': 'teim-review',
                            'source': {
                                'source': 'local',
                                'path': str(stale_path),
                            },
                            'policy': {
                                'installation': 'AVAILABLE',
                                'authentication': 'ON_INSTALL',
                            },
                            'category': 'Developer Tools',
                        },
                    ],
                },
                indent=2,
            )
            + '\n'
        )

        result = self._run_installer()

        self.assertThat(result.returncode, matchers.Equals(0))
        marketplace = json.loads(self.marketplace_file.read_text())

        self.assertThat(
            marketplace['name'], matchers.Equals('custom-marketplace')
        )
        self.assertThat(
            marketplace['interface']['displayName'],
            matchers.Equals('Custom Plugins'),
        )
        self.assertThat(len(marketplace['plugins']), matchers.Equals(2))

        plugin_names = [plugin['name'] for plugin in marketplace['plugins']]
        self.assertThat(
            plugin_names, matchers.ContainsAll(['other-plugin', 'teim-review'])
        )

        teim_plugin = next(
            plugin
            for plugin in marketplace['plugins']
            if plugin['name'] == 'teim-review'
        )
        self.assertThat(
            teim_plugin['source']['path'],
            matchers.Equals(str(self.codex_home / 'plugins' / 'teim-review')),
        )

    def test_installer_fails_without_rewriting_invalid_json(self):
        """Invalid existing marketplace JSON should block the install safely."""
        self.marketplace_file.parent.mkdir(parents=True, exist_ok=True)
        self.marketplace_file.write_text('{"name":')

        result = self._run_installer()

        self.assertThat(result.returncode, matchers.Equals(1))
        self.assertThat(
            result.stderr,
            matchers.Contains('Existing marketplace file is invalid JSON'),
        )
        self.assertThat(
            self.marketplace_file.read_text(),
            matchers.Equals('{"name":'),
        )
