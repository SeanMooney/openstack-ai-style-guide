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
            'roles/ai_html_generation/files/render_html_from_json.py'
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
            'issues': {
                'critical': [
                    {
                        'description': 'Security vulnerability',
                        'confidence': 0.95,
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

        html = self.render_html.render_statistics_section(stats)
        self.assertThat(html, matchers.Contains('2'))  # Critical count
        self.assertThat(html, matchers.Contains('stat-critical'))
        self.assertThat(html, matchers.Contains('stat-high'))
