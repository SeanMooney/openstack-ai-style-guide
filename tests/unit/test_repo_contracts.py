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

"""Repository contracts for portable review and standalone skills."""

import json
import pathlib
import re
import shlex

import yaml
from testtools import matchers

from tests import test


class TestRepoContracts(test.NoDBTestCase):
    """Verify installable resources and CI delivery contracts."""

    def setUp(self):
        super().setUp()
        self.repo_root = pathlib.Path(__file__).resolve().parents[2]
        self.skill_root = self.repo_root / 'skills' / 'teim-review'

    def _read_json(self, path):
        return json.loads((self.repo_root / path).read_text())

    def test_plugins_expose_the_same_skill_tree(self):
        """Native metadata must resolve to the same portable sources."""
        portable = self._read_json('plugin.json')
        self.assertEqual('https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
                         portable['$schema'])
        for directory in ('.claude-plugin', '.codex-plugin', '.cursor-plugin'):
            plugin = self._read_json(directory + '/plugin.json')
            self.assertEqual(portable['name'], plugin['name'])
            self.assertEqual(portable['version'], plugin['version'])
            skills_path = plugin.get('skills', './skills/')
            self.assertEqual(self.skill_root.parent,
                             (self.repo_root / skills_path).resolve())
        pi = self._read_json('package.json')
        self.assertEqual(['./skills'], pi['pi']['skills'])

    def test_marketplaces_resolve_the_plugin_root(self):
        """Both marketplace identities and source paths stay usable."""
        claude = self._read_json('.claude-plugin/marketplace.json')
        codex = self._read_json('.agents/plugins/marketplace.json')
        for marketplace in (claude, codex):
            self.assertEqual('openstack-ai-style-guide', marketplace['name'])
            self.assertEqual('teim-review', marketplace['plugins'][0]['name'])
        self.assertEqual('./', claude['plugins'][0]['source'])
        codex_source = codex['plugins'][0]['source']['path']
        self.assertEqual(self.repo_root,
                         (self.repo_root / codex_source).resolve())

    def test_skill_frontmatter_is_portable(self):
        """Every sibling has standard routing and no model settings."""
        for skill in self.skill_root.parent.iterdir():
            if not skill.is_dir():
                continue
            body = (skill / 'SKILL.md').read_text()
            frontmatter = yaml.safe_load(body.split('---', 2)[1])
            self.assertEqual(skill.name, frontmatter['name'])
            self.assertTrue(frontmatter['description'])
            self.assertLessEqual(len(frontmatter['description']), 1024)
            self.assertNotIn('model', frontmatter)
            self.assertNotIn('context', frontmatter)
            self.assertNotIn('agent', frontmatter)

    def test_standalone_invocation_policy(self):
        """Audits need explicit invocation; conversion stays discoverable."""
        for name in ('security-auditor', 'code-maintainability-auditor',
                     'doc-to-markdown'):
            skill = self.skill_root.parent / name
            frontmatter = yaml.safe_load(
                (skill / 'SKILL.md').read_text().split('---', 2)[1])
            explicit_only = name != 'doc-to-markdown'
            self.assertEqual(explicit_only,
                             frontmatter.get('disable-model-invocation', False))
            metadata_path = skill / 'agents/openai.yaml'
            metadata = (yaml.safe_load(metadata_path.read_text())
                        if metadata_path.exists() else {})
            self.assertEqual(not explicit_only,
                             metadata.get('policy', {}).get(
                                 'allow_implicit_invocation', True))
        self.assertFalse((self.repo_root / 'agents').exists())
        for alias in ('.claude/agents', '.opencode/agent'):
            self.assertFalse((self.repo_root / alias).is_symlink())

    def test_skill_links_resolve_inside_the_package(self):
        """Each skill stays usable when installed independently."""
        for skill in self.skill_root.parent.iterdir():
            if not skill.is_dir():
                continue
            for path in skill.rglob('*.md'):
                for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                    if '://' in target or target.startswith('#'):
                        continue
                    resource = (path.parent / target.split('#', 1)[0]).resolve()
                    self.assertTrue(resource.is_relative_to(skill),
                                    f'{path}: resource escapes skill: {target}')
                    self.assertTrue(resource.exists(),
                                    f'{path}: missing {target}')

    def test_required_runtime_resources_are_bundled(self):
        """Installing one skill includes both review roles and report tools."""
        for path in (
            'references/workflow.md', 'references/finding-policy.md',
            'references/reviewer.md', 'references/validator.md',
            'references/quick-rules.md', 'references/comprehensive-guide.md',
            'references/knowledge/README.md',
            'references/schemas/candidate-findings-schema.json',
            'references/schemas/validated-findings-schema.json',
            'references/schemas/review-report-schema.json',
            'scripts/detect_changed_files.py',
            'scripts/detect_changed_lines.py',
            'scripts/prepare_review_artifacts.py',
            'scripts/build_review_report.py',
            'scripts/normalize_review_report.py',
            'scripts/render_html_from_json.py',
        ):
            self.assertTrue((self.skill_root / path).is_file(), path)
        self.assertFalse((self.repo_root / 'plugins/teim-review/skills/teim-review/SKILL.md').exists())
        self.assertFalse((self.repo_root / 'config/tool-profiles.json').exists())

    def test_ci_uses_one_claude_call_and_the_portable_entrypoint(self):
        """CI keeps Claude delivery and deterministic report assembly."""
        role = yaml.safe_load((self.repo_root / 'roles/ai_code_review/tasks/main.yaml').read_text())
        invocations = [task for task in role
                       if task.get('ansible.builtin.include_role', {}).get('name')
                       == 'run_claude_code']
        self.assertEqual(1, len(invocations))
        variables = invocations[0]['vars']
        self.assertEqual('{{ ai_code_review_model }}',
                         variables['run_claude_code_model_name'])
        self.assertEqual('{{ ai_code_review_validated_findings_schema }}',
                         variables['run_claude_code_json_schema'])
        prompt = next(task['ansible.builtin.set_fact']['ai_code_review_review_prompt']
                      for task in role if 'ansible.builtin.set_fact' in task)
        self.assertThat(prompt, matchers.Contains('{{ ai_code_review_skill_root }}/SKILL.md'))
        self.assertThat(prompt, matchers.Contains('findings_only: true'))
        self.assertNotIn('@teim-review-agent', prompt)
        playbook = (self.repo_root / 'playbooks/teim-code-review/run.yaml').read_text()
        for tool in ('build_review_report.py', 'normalize_review_report.py'):
            self.assertThat(playbook, matchers.Contains('skills/teim-review/scripts/' + tool))

    def test_claude_review_can_delegate_without_interactive_approval(self):
        """Headless review exposes delegation instead of forcing fallback."""
        defaults = yaml.safe_load((self.repo_root / 'roles/ai_code_review/defaults/main.yaml').read_text())
        self.assertFalse(defaults['ai_code_review_claude_bare'])
        tasks = yaml.safe_load((self.repo_root / 'roles/run_claude_code/tasks/main.yaml').read_text())
        commands = [task['ansible.builtin.set_fact']['run_claude_code_command']
                    for task in tasks if 'run_claude_code_command'
                    in task.get('ansible.builtin.set_fact', {})]
        self.assertEqual(2, len(commands))
        for command in commands:
            args = shlex.split(command)
            tools = args[args.index('--allowedTools') + 1].split(',')
            self.assertIn('Agent', tools)
            self.assertIn('Task', tools)
