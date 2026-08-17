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

"""Tests for deterministic teim-review artifact preparation."""

import json
import pathlib
import subprocess

import fixtures
from testtools import matchers

from tests import test


class TestPrepareReviewArtifacts(test.NoDBTestCase):
    """Test deterministic context artifact generation."""

    def setUp(self):
        super().setUp()
        self.preparer = test.load_script('tools/prepare_review_artifacts.py')

    def test_cli_writes_prepared_context_artifacts(self):
        """The CLI writes all prepared artifacts and full context paths."""
        tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        project = tempdir / 'project'
        output = tempdir / 'out'
        project.mkdir()
        (project / 'AGENTS.md').write_text(
            '# Repo Guidance\n\nKeep review findings actionable.\n',
            encoding='utf-8',
        )
        long_hacking_text = 'A' * 4500 + 'important exception at end'
        (project / 'HACKING.rst').write_text(long_hacking_text, encoding='utf-8')
        inventory = tempdir / 'inventory.yaml'
        inventory.write_text(
            'all:\n'
            '  vars:\n'
            '    zuul:\n'
            '      change: "12345"\n'
            '      patchset: "2"\n'
            '      project: openstack/nova\n'
            '      branch: master\n',
            encoding='utf-8',
        )
        changed = tempdir / 'changed-files.txt'
        changed.write_text('nova/compute/manager.py\n', encoding='utf-8')
        quick = tempdir / 'quick-rules.md'
        comprehensive = tempdir / 'comprehensive-guide.md'
        policy = tempdir / 'finding-policy.md'
        knowledge = tempdir / 'knowledge'
        candidate_schema = tempdir / 'candidate.json'
        validated_schema = tempdir / 'validated.json'
        for path in [quick, comprehensive, policy, candidate_schema,
                     validated_schema]:
            path.write_text('{}\n', encoding='utf-8')
        knowledge.mkdir()

        self.useFixture(
            fixtures.MonkeyPatch(
                'sys.argv',
                [
                    'prepare_review_artifacts.py',
                    '--project-dir',
                    str(project),
                    '--output-dir',
                    str(output),
                    '--inventory-file',
                    str(inventory),
                    '--changed-files',
                    str(changed),
                    '--quick-rules',
                    str(quick),
                    '--comprehensive-guide',
                    str(comprehensive),
                    '--finding-policy',
                    str(policy),
                    '--knowledge-root',
                    str(knowledge),
                    '--candidate-schema',
                    str(candidate_schema),
                    '--validated-schema',
                    str(validated_schema),
                ],
            )
        )

        result = self.preparer.main()

        self.assertThat(result, matchers.Equals(0))
        self.assertTrue(output.joinpath('zuul-context.md').exists())
        self.assertTrue(output.joinpath('commit-summary.md').exists())
        self.assertTrue(output.joinpath('project-guidelines.md').exists())
        context = json.loads(
            output.joinpath('review-context.json').read_text(encoding='utf-8')
        )
        self.assertThat(context['mode'], matchers.Equals('zuul'))
        self.assertThat(context['zuul']['change'], matchers.Equals('12345'))
        self.assertThat(
            context['changed_files'],
            matchers.Equals(['nova/compute/manager.py']),
        )
        self.assertThat(
            context['context_paths']['finding_policy'],
            matchers.Equals(str(policy)),
        )
        self.assertThat(context['impact'], matchers.Contains('Review impact'))
        self.assertThat(context['review']['scope_mode'], matchers.Equals('local'))
        guidelines = output.joinpath('project-guidelines.md').read_text(
            encoding='utf-8'
        )
        self.assertThat(guidelines, matchers.Contains('important exception at end'))

    def test_load_yaml_parses_nested_zuul_inventory(self):
        """CI prep parses real Zuul inventory shape with PyYAML."""
        tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        inventory = tempdir / 'inventory.yaml'
        inventory.write_text(
            'all:\n'
            '  vars:\n'
            '    zuul:\n'
            '      change: "12345"\n'
            '      patchset: "2"\n'
            '      project: openstack/nova\n'
            '      branch: master\n',
            encoding='utf-8',
        )

        data = self.preparer.load_yaml(inventory)
        zuul = self.preparer.find_zuul_vars(data)

        self.assertThat(zuul['change'], matchers.Equals('12345'))
        self.assertThat(zuul['patchset'], matchers.Equals('2'))
        self.assertThat(zuul['project'], matchers.Equals('openstack/nova'))

    def test_git_context_stat_uses_explicit_review_base(self):
        """GitHub branch summaries cover every commit after the PR base."""
        root = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        project = root / 'project'
        project.mkdir()

        def run_git(*args):
            return subprocess.run(  # noqa: S603
                ['git', *args],  # noqa: S607
                cwd=str(project),
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()

        run_git('init', '-b', 'master')
        run_git('config', 'user.email', 'test@example.com')
        run_git('config', 'user.name', 'Test User')
        project.joinpath('base.txt').write_text('base\n', encoding='utf-8')
        run_git('add', '.')
        run_git('commit', '-m', 'base')
        review_base = run_git('rev-parse', 'HEAD')

        project.joinpath('first.txt').write_text('first\n', encoding='utf-8')
        run_git('add', '.')
        run_git('commit', '-m', 'first PR commit')
        project.joinpath('second.txt').write_text('second\n', encoding='utf-8')
        run_git('add', '.')
        run_git('commit', '-m', 'second PR commit')

        context = self.preparer.collect_git_context(project, review_base)

        self.assertThat(context['commits'], matchers.Contains('first PR commit'))
        self.assertThat(context['commits'], matchers.Contains('second PR commit'))
        self.assertThat(context['stat'], matchers.Contains('first.txt'))
        self.assertThat(context['stat'], matchers.Contains('second.txt'))

        output = root / 'output'
        output.mkdir()
        self.preparer.write_commit_summary(
            output,
            {
                'change': 'Multi-commit pull request',
                'git': context,
            },
        )
        summary = output.joinpath('commit-summary.md').read_text(
            encoding='utf-8'
        )
        self.assertThat(summary, matchers.Contains('Head subject:'))
        self.assertThat(summary, matchers.Contains('Commits In Reviewed Range'))
        self.assertThat(summary, matchers.Contains('Reviewed Range Diff Stat'))
