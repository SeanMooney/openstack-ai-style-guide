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

    def test_skill_points_at_teim_review_agent_and_schema(self):
        """The interactive entrypoint must keep its agent and schema contract."""
        skill = self._read_text('skills/teim-review/SKILL.md')

        self.assertThat(
            skill, matchers.Contains('Use the @teim-review-agent subagent')
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
        self.assertThat(agent, matchers.Contains('review-report.json'))
        self.assertThat(agent, matchers.Contains('project-guidelines.md'))
        self.assertThat(agent, matchers.Contains('knowledge_root'))

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
        self.assertThat(knowledge_doc.read_text(), matchers.Contains('overlays'))
