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

"""Test cases for generate_zuul_comments script."""

from testtools import matchers

from tests import test


class TestGenerateZuulComments(test.NoDBTestCase):
    """Test cases for generate_zuul_comments.py."""

    def setUp(self):
        super().setUp()
        self.gen_comments = test.load_script(
            'roles/ai_zuul_integration/files/generate_zuul_comments.py'
        )

    def _make_issue(self, reporting_mode='inline', location='nova/compute/manager.py:42'):
        return {
            'description': 'Test issue description here',
            'confidence': 0.9,
            'reporting_mode': reporting_mode,
            'location': location,
            'impact': 'Test impact description here',
            'suggestion': 'Fix the issue by doing X',
        }

    def test_extract_file_comments_excludes_html_only(self):
        """html_only issues are not included in file comments."""
        review_data = {
            'issues': {
                'critical': [],
                'high': [],
                'warnings': [self._make_issue(reporting_mode='html_only')],
                'suggestions': [],
            }
        }
        result = self.gen_comments.extract_file_comments(review_data)
        self.assertThat(result, matchers.Equals({}))

    def test_extract_file_comments_includes_inline(self):
        """Inline issues are included in file comments."""
        review_data = {
            'issues': {
                'critical': [],
                'high': [],
                'warnings': [self._make_issue(reporting_mode='inline')],
                'suggestions': [],
            }
        }
        result = self.gen_comments.extract_file_comments(review_data)
        self.assertThat(len(result), matchers.GreaterThan(0))
        self.assertIn('nova/compute/manager.py', result)

    def test_extract_file_comments_filters_unchanged_files(self):
        """Inline comments outside the changed file allowlist are dropped."""
        review_data = {
            'issues': {
                'critical': [],
                'high': [],
                'warnings': [
                    self._make_issue(
                        reporting_mode='inline',
                        location='nova/compute/manager.py:42',
                    ),
                    self._make_issue(
                        reporting_mode='inline',
                        location='nova/virt/driver.py:100',
                    ),
                ],
                'suggestions': [],
            }
        }
        result = self.gen_comments.extract_file_comments(
            review_data,
            changed_files={'nova/compute/manager.py'},
        )
        self.assertIn('nova/compute/manager.py', result)
        self.assertThat(
            result, matchers.Not(matchers.Contains('nova/virt/driver.py'))
        )

    def test_generate_zuul_return_data_includes_patch_level_warnings(self):
        """Patch-level observations become Zuul summary warnings."""
        review_data = {
            'issues': {
                'critical': [],
                'high': [],
                'warnings': [],
                'suggestions': [],
            },
            'patch_level_observations': [
                {
                    'description': 'Release note is needed for behavior change',
                    'impact': 'Operators need upgrade guidance',
                    'recommendation': 'Add a release note before merge',
                }
            ],
        }
        result = self.gen_comments.generate_zuul_return_data(review_data)
        self.assertThat(result['zuul']['file_comments'], matchers.Equals({}))
        self.assertThat(len(result['zuul']['warnings']), matchers.Equals(1))
        self.assertThat(
            result['zuul']['warnings'][0],
            matchers.Contains('Release note is needed'),
        )

    def test_out_of_patch_observations_do_not_generate_zuul_output(self):
        """Pre-existing findings remain HTML-only."""
        review_data = {
            'issues': {
                'critical': [],
                'high': [],
                'warnings': [],
                'suggestions': [],
            },
            'out_of_patch_observations': [
                {
                    'description': 'Pre-existing cleanup bug',
                    'location': 'nova/compute/manager.py:42',
                    'suggestion': 'Fix in a follow-up patch',
                }
            ],
        }
        result = self.gen_comments.generate_zuul_return_data(review_data)
        self.assertThat(
            result, matchers.Equals({'zuul': {'file_comments': {}}})
        )

    def test_extract_file_comments_mixed_reporting_modes(self):
        """Only inline issues are extracted when both modes are present."""
        review_data = {
            'issues': {
                'critical': [],
                'high': [],
                'warnings': [
                    self._make_issue(reporting_mode='inline',
                                     location='nova/compute/manager.py:42'),
                    self._make_issue(reporting_mode='html_only',
                                     location='nova/virt/driver.py:100'),
                ],
                'suggestions': [],
            }
        }
        result = self.gen_comments.extract_file_comments(review_data)
        self.assertIn('nova/compute/manager.py', result)
        self.assertThat(result, matchers.Not(matchers.Contains('nova/virt/driver.py')))
