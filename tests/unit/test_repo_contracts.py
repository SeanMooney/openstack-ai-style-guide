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

"""Repository contract tests for plugin and workflow wiring."""

import json
import pathlib

from testtools import matchers

from tests import test


class TestRepoContracts(test.NoDBTestCase):
    """Lock active runtime contracts during repository restructuring."""

    def setUp(self):
        super().setUp()
        self.repo_root = pathlib.Path(__file__).resolve().parents[2]

    def _read_text(self, relative_path):
        return (self.repo_root / relative_path).read_text()

    def _read_json(self, relative_path):
        with (self.repo_root / relative_path).open() as fh:
            return json.load(fh)

    def test_plugin_and_marketplace_metadata_stay_aligned(self):
        """The plugin and marketplace must describe the same plugin contract."""
        plugin = self._read_json('.claude-plugin/plugin.json')
        marketplace = self._read_json('.claude-plugin/marketplace.json')

        self.assertThat(plugin['name'], matchers.Equals('teim-review'))
        self.assertThat(
            marketplace['name'], matchers.Equals('openstack-ai-style-guide')
        )
        self.assertThat(len(marketplace['plugins']), matchers.Equals(1))

        listed_plugin = marketplace['plugins'][0]
        self.assertThat(listed_plugin['name'], matchers.Equals(plugin['name']))
        self.assertThat(
            listed_plugin['version'], matchers.Equals(plugin['version'])
        )
        self.assertThat(listed_plugin['source'], matchers.Equals('./'))

    def test_codex_plugin_and_marketplace_metadata_stay_aligned(self):
        """Codex plugin metadata should match the repo marketplace entry."""
        plugin = self._read_json('plugins/teim-review/.codex-plugin/plugin.json')
        marketplace = self._read_json('.agents/plugins/marketplace.json')

        self.assertThat(plugin['name'], matchers.Equals('teim-review'))
        self.assertThat(plugin['skills'], matchers.Equals('./skills/'))
        self.assertThat(
            marketplace['plugins'][0]['name'], matchers.Equals(plugin['name'])
        )
        self.assertThat(
            marketplace['plugins'][0]['source']['path'],
            matchers.Equals('../../plugins/teim-review'),
        )
        resolved_path = (
            self.repo_root
            / '.agents'
            / 'plugins'
            / marketplace['plugins'][0]['source']['path']
        ).resolve()
        self.assertThat(
            resolved_path,
            matchers.Equals((self.repo_root / 'plugins' / 'teim-review').resolve()),
        )

    def test_shared_core_and_tool_profiles_exist(self):
        """The shared workflow and semantic profiles are stable contracts."""
        prompt = self._read_text('prompts/teim-review-core.md')
        profiles = self._read_json('config/tool-profiles.json')

        self.assertThat(
            prompt,
            matchers.Contains('authoritative provider-neutral review workflow'),
        )
        self.assertThat(
            profiles['profiles']['fast']['codex']['context_model'],
            matchers.Equals('gpt-5.4-mini'),
        )
        self.assertThat(
            profiles['profiles']['fast']['codex']['interactive_review_model'],
            matchers.Equals('inherit'),
        )
        self.assertThat(
            profiles['profiles']['deep']['codex']['interactive_review_model'],
            matchers.Equals('inherit'),
        )
        self.assertThat(
            profiles['profiles']['deep']['claude']['review_model'],
            matchers.Equals('inherit'),
        )

    def test_codex_plugin_references_mirror_shared_core_files(self):
        """Codex plugin mirrors should stay aligned with shared sources."""
        shared_prompt = self._read_text('prompts/teim-review-core.md')
        plugin_prompt = self._read_text(
            'plugins/teim-review/references/teim-review-core.md'
        )
        shared_profiles = self._read_json('config/tool-profiles.json')
        plugin_profiles = self._read_json(
            'plugins/teim-review/references/tool-profiles.json'
        )

        self.assertThat(plugin_prompt, matchers.Equals(shared_prompt))
        self.assertThat(plugin_profiles, matchers.Equals(shared_profiles))

    def test_skill_points_at_teim_review_agent_and_schema(self):
        """The interactive entrypoint must keep its agent and schema contract."""
        skill = self._read_text('skills/teim-review/SKILL.md')

        self.assertThat(
            skill, matchers.Contains('Use the @teim-review-agent subagent')
        )
        self.assertThat(
            skill, matchers.Contains('prompts/teim-review-core.md')
        )
        self.assertThat(
            skill,
            matchers.Contains('schemas/review-report-schema.json'),
        )
        self.assertThat(skill, matchers.Contains('.teim-review/'))
        self.assertThat(skill, matchers.Contains('./docs/knowledge/'))

    def test_orchestrator_agent_references_core_outputs(self):
        """The orchestrator agent must still define the expected review flow."""
        agent = self._read_text('agents/teim-review-agent.md')

        self.assertThat(agent, matchers.Contains('@code-review-agent'))
        self.assertThat(
            agent, matchers.Contains('prompts/teim-review-core.md')
        )
        self.assertThat(agent, matchers.Contains('review-report.json'))
        self.assertThat(agent, matchers.Contains('project-guidelines.md'))
        self.assertThat(agent, matchers.Contains('knowledge_root'))

    def test_codex_and_cursor_adapters_reference_shared_core(self):
        """Codex and Cursor should stay thin adapters over the shared core."""
        codex_skill = self._read_text(
            'plugins/teim-review/skills/teim-review/SKILL.md'
        )
        cursor_rule = self._read_text('.cursor/rules/teim-review.mdc')
        cursor_mode = self._read_text('cursor/teim-review-mode-template.json')
        agents_doc = self._read_text('AGENTS.md')

        self.assertThat(
            codex_skill, matchers.Contains('references/teim-review-core.md')
        )
        self.assertThat(
            cursor_rule, matchers.Contains('prompts/teim-review-core.md')
        )
        self.assertThat(cursor_mode, matchers.Contains('Teim Review'))
        self.assertThat(agents_doc, matchers.Contains('plugins/teim-review/'))
        self.assertThat(agents_doc, matchers.Contains('.cursor/rules/'))
        self.assertThat(codex_skill, matchers.Contains('$teim-review'))
        self.assertThat(codex_skill, matchers.Contains('/skills'))
        self.assertThat(
            codex_skill,
            matchers.Not(matchers.Contains('scripts/teim-review-codex')),
        )
        self.assertThat(codex_skill, matchers.Not(matchers.Contains('@teim-review')))
        self.assertThat(agents_doc, matchers.Not(matchers.Contains('@teim-review')))

    def test_gitignore_ignores_codex_artifact(self):
        """Local Codex run artifacts should not dirty the repository."""
        gitignore = self._read_text('.gitignore')
        self.assertThat(gitignore, matchers.Contains('.codex'))

    def test_zuul_job_and_playbook_keep_current_entrypoints(self):
        """Zuul and playbook wiring should continue to target the same flow."""
        jobs = self._read_text('zuul.d/jobs.yaml')
        playbook = self._read_text('playbooks/teim-code-review/run.yaml')
        setup_role = self._read_text('roles/ai_review_setup/tasks/main.yaml')
        review_role = self._read_text('roles/ai_code_review/tasks/main.yaml')

        self.assertThat(jobs, matchers.Contains('name: teim-code-review'))
        self.assertThat(
            jobs, matchers.Contains('name: openstack-ai-style-guide-lint')
        )
        self.assertThat(playbook, matchers.Contains('name: ai_review_setup'))
        self.assertThat(playbook, matchers.Contains('name: ai_code_review'))
        self.assertThat(playbook, matchers.Contains('name: ai_html_generation'))
        self.assertThat(
            playbook, matchers.Contains('name: ai_zuul_integration')
        )
        self.assertThat(
            setup_role,
            matchers.Contains('teim-review@openstack-ai-style-guide'),
        )
        self.assertThat(review_role, matchers.Contains('knowledge_root'))

    def test_active_docs_and_archive_markers_exist(self):
        """Supporting docs should make active versus legacy material explicit."""
        active_doc = self.repo_root / 'docs/review-system-overview.md'
        archive_doc = self.repo_root / 'docs/archive/README.md'
        knowledge_doc = self.repo_root / 'docs/knowledge/README.md'
        quick_rules = self.repo_root / 'docs/quick-rules.md'
        comprehensive = self.repo_root / 'docs/comprehensive-guide.md'

        self.assertTrue(active_doc.exists())
        self.assertTrue(archive_doc.exists())
        self.assertTrue(knowledge_doc.exists())
        self.assertTrue(quick_rules.exists())
        self.assertTrue(comprehensive.exists())
        self.assertThat(active_doc.read_text(), matchers.Contains('teim-review'))
        self.assertThat(active_doc.read_text(), matchers.Contains('$teim-review'))
        self.assertThat(
            active_doc.read_text(),
            matchers.Not(matchers.Contains('@teim-review')),
        )
        self.assertThat(knowledge_doc.read_text(), matchers.Contains('overlays'))
