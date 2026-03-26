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

"""Test cases for HTML rendering script."""

import json
import pathlib

import fixtures
from testtools import matchers

from tests import test


class TestRenderHtml(test.NoDBTestCase):
    """Test cases for render_html_from_json.py."""

    def setUp(self):
        super().setUp()
        self.render_html = test.load_script(
            'tools/render_html_from_json.py'
        )

    def _create_sample_review(self):
        """Create sample review data.

        :returns: Dictionary with sample review data
        """
        return {
            'context': {
                'change': '12345',
                'scope': 'Modified roles/ai_code_review',
                'impact': 'Adds structured output support',
            },
            'statistics': {
                'critical': 1,
                'high': 2,
                'warnings': 3,
                'suggestions': 1,
                'total': 7,
            },
            'statistics_html_only': {
                'critical': 0,
                'high': 0,
                'warnings': 0,
                'suggestions': 0,
                'total': 0,
            },
            'issues': {
                'critical': [
                    {
                        'description': 'Security vulnerability',
                        'confidence': 0.95,
                        'reporting_mode': 'inline',
                        'location': 'roles/ai_code_review/tasks/main.yaml:25',
                        'risk': 'High',
                        'remediation_priority': 'Immediate',
                        'why_matters': 'Allows unauthorized access',
                        'recommendation': 'Add authentication check',
                    }
                ],
                'high': [],
                'warnings': [],
                'suggestions': [],
            },
            'positive_observations': [
                {'category': 'Code Quality', 'observation': 'Good structure'}
            ],
            'summary': {
                'assessment': 'Needs improvements',
                'priority_focus': 'Security',
                'detailed_summary': 'Multiple security issues found',
            },
        }

    def test_render_html_with_valid_data(self):
        """Test HTML generation with valid review data."""
        review_data = self._create_sample_review()
        html_content = self.render_html.render_html_template(review_data)

        # Verify HTML structure using matchers (H203/H204 compliance)
        self.assertThat(html_content, matchers.Contains('<!DOCTYPE html>'))
        self.assertThat(html_content, matchers.Contains('<title>Code Review Report</title>'))
        self.assertThat(html_content, matchers.Contains('1 Critical'))
        self.assertThat(html_content, matchers.Contains('Security vulnerability'))

    def test_extract_review_data_from_wrapper(self):
        """Test extracting review data from Claude CLI wrapper."""
        wrapper_data = {
            'type': 'result',
            'structured_output': self._create_sample_review(),
        }

        extracted = self.render_html.extract_review_data(wrapper_data)
        self.assertIn('context', extracted)
        self.assertIn('issues', extracted)

    def test_load_json_with_trailing_text(self):
        """Test loading JSON with trailing text (Claude CLI output)."""
        tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        json_file = tempdir / 'review.json'
        review_data = self._create_sample_review()

        # Write JSON with trailing text (Claude CLI behavior)
        with json_file.open('w') as f:
            f.write(json.dumps(review_data))
            f.write('\nAdditional text from Claude CLI\n')

        loaded = self.render_html.load_json_with_trailing_text(json_file)
        self.assertThat(loaded['statistics']['total'], matchers.Equals(7))

    def test_escape_html_special_characters(self):
        """Test HTML escaping prevents XSS."""
        self.assertThat(
            self.render_html.escape_html('<script>alert("xss")</script>'),
            matchers.Equals(
                '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
            ),
        )

    def test_render_statistics_section(self):
        """Test statistics HTML generation."""
        stats = {'critical': 2, 'high': 3, 'warnings': 5, 'suggestions': 1, 'total': 11}
        stats_html_only = {'critical': 0, 'high': 1, 'warnings': 2, 'suggestions': 0, 'total': 3}

        html = self.render_html.render_statistics_section(stats, stats_html_only)
        self.assertThat(html, matchers.Contains('2'))  # Critical count
        self.assertThat(html, matchers.Contains('stat-critical'))
        self.assertThat(html, matchers.Contains('stat-high'))
        self.assertThat(html, matchers.Contains('HTML report only'))  # html_only row shown

    def test_render_statistics_section_no_html_only(self):
        """Test statistics section without html_only findings."""
        stats = {'critical': 1, 'high': 0, 'warnings': 0, 'suggestions': 0, 'total': 1}
        stats_html_only = {'critical': 0, 'high': 0, 'warnings': 0, 'suggestions': 0, 'total': 0}

        html = self.render_html.render_statistics_section(stats, stats_html_only)
        self.assertThat(html, matchers.Contains('stat-critical'))
        # html_only row should not appear when all counts are zero
        self.assertThat(
            html, matchers.Not(matchers.Contains('HTML report only'))
        )

    def test_render_out_of_patch_observations_empty(self):
        """Empty list returns empty string."""
        html = self.render_html.render_out_of_patch_observations([])
        self.assertThat(html, matchers.Equals(''))

    def test_render_out_of_patch_observations_normal(self):
        """Observations are rendered with location, description, and suggestion."""
        observations = [
            {
                'location': 'nova/compute/manager.py:42',
                'description': 'Potential resource leak in cleanup path',
                'suggestion': 'Address in a follow-up patch',
            }
        ]
        html = self.render_html.render_out_of_patch_observations(observations)
        self.assertThat(html, matchers.Contains('nova/compute/manager.py:42'))
        self.assertThat(html, matchers.Contains('Potential resource leak'))
        self.assertThat(html, matchers.Contains('follow-up patch'))
        self.assertThat(html, matchers.Contains('Out-of-Patch Observations'))

    def test_render_out_of_patch_observations_html_escaping(self):
        """Special characters in observation fields are escaped."""
        observations = [
            {
                'location': 'path/to/file.py:1',
                'description': '<script>alert("xss")</script>',
                'suggestion': 'Use & instead of &&',
            }
        ]
        html = self.render_html.render_out_of_patch_observations(observations)
        self.assertThat(html, matchers.Not(matchers.Contains('<script>')))
        self.assertThat(html, matchers.Contains('&lt;script&gt;'))
        self.assertThat(html, matchers.Contains('&amp;'))

    def test_render_html_template_includes_out_of_patch(self):
        """render_html_template includes out-of-patch section when data present."""
        review_data = self._create_sample_review()
        review_data['out_of_patch_observations'] = [
            {
                'location': 'nova/compute/manager.py:42',
                'description': 'Potential resource leak in cleanup path',
                'suggestion': 'Address in a follow-up patch',
            }
        ]
        html_content = self.render_html.render_html_template(review_data)
        self.assertThat(html_content, matchers.Contains('Out-of-Patch Observations'))
        self.assertThat(html_content, matchers.Contains('nova/compute/manager.py:42'))
        self.assertThat(html_content, matchers.Contains('Potential resource leak'))
