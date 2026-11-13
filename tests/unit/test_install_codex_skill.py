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
import sys

import fixtures
import jsonschema
import yaml
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
        skills = self.codex_home / 'plugins/teim-review/skills'
        expected = {'teim-review', 'security-auditor',
                    'code-maintainability-auditor', 'doc-to-markdown'}
        self.assertEqual(expected, {p.name for p in skills.iterdir()})
        for name in ('security-auditor', 'code-maintainability-auditor'):
            skill = skills / name
            metadata = yaml.safe_load((skill / 'agents/openai.yaml').read_text())
            self.assertFalse(metadata['policy']['allow_implicit_invocation'])
            frontmatter = yaml.safe_load(
                (skill / 'SKILL.md').read_text().split('---', 2)[1])
            self.assertTrue(frontmatter['disable-model-invocation'])
        conversion = yaml.safe_load(
            (skills / 'doc-to-markdown/SKILL.md').read_text().split('---', 2)[1])
        self.assertFalse(conversion.get('disable-model-invocation', False))


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

    def test_installed_skill_runs_without_the_source_checkout(self):
        """A copied package can prepare and render a different repository."""
        installed = self._run_installer()
        self.assertEqual(0, installed.returncode, installed.stderr)
        skill = self.codex_home / 'plugins/teim-review/skills/teim-review'
        project = self.tempdir / 'separate project'
        project.mkdir()
        output = self.tempdir / 'review output'

        def run(*args):
            result = subprocess.run(  # noqa: S603
                list(args), cwd=project, capture_output=True, text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            return result.stdout

        run('git', 'init')
        run('git', 'config', 'user.name', 'Test User')
        run('git', 'config', 'user.email', 'test@example.com')
        project.joinpath('service.py').write_text('value = 1\n')
        project.joinpath('AGENTS.md').write_text('Use project-specific guidance.\n')
        run('git', 'add', '.')
        run('git', 'commit', '-m', 'base')
        project.joinpath('service.py').write_text('value = 2\n')
        run('git', 'add', '.')
        run('git', 'commit', '-m', 'change')

        def script(name, *args):
            return run(sys.executable, str(skill / 'scripts' / name), *args)

        changed = output / 'changed-files.txt'
        script('detect_changed_files.py', str(project), '--output', str(changed))
        self.assertEqual('service.py\n', changed.read_text())
        script(
            'prepare_review_artifacts.py',
            '--project-dir', str(project), '--output-dir', str(output),
            '--changed-files', str(changed),
            '--quick-rules', str(skill / 'references/quick-rules.md'),
            '--comprehensive-guide', str(skill / 'references/comprehensive-guide.md'),
            '--finding-policy', str(skill / 'references/finding-policy.md'),
            '--knowledge-root', str(skill / 'references/knowledge'),
            '--candidate-schema', str(skill / 'references/schemas/candidate-findings-schema.json'),
            '--validated-schema', str(skill / 'references/schemas/validated-findings-schema.json'),
        )
        context = json.loads(output.joinpath('review-context.json').read_text())
        for path in context['context_paths'].values():
            if path and str(skill) in path:
                self.assertTrue(pathlib.Path(path).exists(), path)
        self.assertIn('Use project-specific guidance.',
                      output.joinpath('project-guidelines.md').read_text())

        # Model reasoning is supplied as fixture data; run the actual installed
        # assembly, normalization, schema validation, and renderer around it.
        finding_context = {
            'change': 'Change service value', 'scope': 'service.py',
            'review_basis': 'Fixture review of the prepared change',
        }
        finding = {
            'id': 'CF-001', 'category': 'correctness',
            'title': 'Changed service behavior',
            'description': 'The changed value alters the service behavior.',
            'evidence': 'The patch changes the configured service value.',
            'source_basis': 'service.py',
            'relation_to_change': 'The value is modified in this patch.',
            'location': None, 'impact': 'Existing callers receive a new value.',
            'recommendation': 'Verify the changed value matches the intended behavior.',
            'severity': 'warnings', 'confidence': 0.9,
            'anchor_kind': 'patch_level',
        }
        candidates = {'context': finding_context, 'findings': [finding]}
        validated = {
            'context': finding_context,
            'accepted_findings': [dict(finding, validation_rationale='Fixture evidence confirms the changed behavior.')],
            'rejected_findings': [],
        }
        for filename, data, schema in (
            ('candidate-findings.json', candidates, 'candidate-findings-schema.json'),
            ('validated-findings.json', validated, 'validated-findings-schema.json'),
        ):
            jsonschema.validate(data, json.loads((skill / 'references/schemas' / schema).read_text()))
            output.joinpath(filename).write_text(json.dumps(data))

        raw = output / 'review-report.raw.json'
        report_path = output / 'review-report.json'
        schema_path = skill / 'references/schemas/review-report-schema.json'
        script('build_review_report.py',
               '--validated-findings', str(output / 'validated-findings.json'),
               '--review-context', str(output / 'review-context.json'),
               '--output', str(raw))
        script('normalize_review_report.py', '--raw-report', str(raw),
               '--candidate-findings', str(output / 'candidate-findings.json'),
               '--validated-findings', str(output / 'validated-findings.json'),
               '--changed-files', str(changed), '--schema', str(schema_path),
               '--output', str(report_path),
               '--diagnostics', str(output / 'review-validation.json'))
        report = json.loads(report_path.read_text())
        jsonschema.validate(report, json.loads(schema_path.read_text()))
        self.assertEqual(1, report['statistics_html_only']['total'])
        html = output / 'review-report.html'
        script('render_html_from_json.py', str(report_path), str(html),
               '--schema', str(schema_path))
        self.assertIn(finding['description'], html.read_text())
