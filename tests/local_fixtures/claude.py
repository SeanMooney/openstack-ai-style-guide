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

"""Claude API mock fixtures."""

import json

import fixtures


class ClaudeCLIResponse(fixtures.Fixture):
    """Fixture to mock Claude CLI subprocess responses.

    This mocks at the system boundary (subprocess calls) which is
    appropriate for tests. Unit tests should mock individual
    functions directly.
    """

    def __init__(self, review_data=None):
        super().__init__()
        if review_data is None:
            review_data = {
                'context': {
                    'change': 'Fixture review output',
                    'scope': 'Default fixture scope for test helpers',
                    'impact': 'Provides a schema-compatible default response',
                },
                'statistics': {
                    'critical': 0,
                    'high': 0,
                    'warnings': 0,
                    'suggestions': 0,
                    'total': 0,
                },
                'statistics_html_only': {
                    'critical': 0,
                    'high': 0,
                    'warnings': 0,
                    'suggestions': 0,
                    'total': 0,
                },
                'issues': {
                    'critical': [],
                    'high': [],
                    'warnings': [],
                    'suggestions': [],
                },
                'out_of_patch_observations': [],
                'positive_observations': [],
                'summary': {
                    'assessment': 'Ready',
                    'priority_focus': 'No review action required for default fixture',
                    'detailed_summary': (
                        'Default fixture response includes the full review '
                        'schema shape for tests that only need a valid stub.'
                    ),
                },
            }
        self.review_data = review_data

    def setUp(self):
        super().setUp()

        # Create mock response wrapper
        response_wrapper = {'type': 'result', 'structured_output': self.review_data}
        self.mock_response = json.dumps(response_wrapper)

        # Mock subprocess.run (boundary mock)
        from unittest import mock

        def mock_subprocess_run(*_args, **_kwargs):
            """Mock subprocess.run to return Claude CLI output."""
            mock_result = mock.Mock()
            mock_result.stdout = self.mock_response
            mock_result.stderr = ''
            mock_result.returncode = 0
            return mock_result

        self.mock_run = self.useFixture(fixtures.MockPatch('subprocess.run', mock_subprocess_run))


class ClaudeAPIFixture(fixtures.Fixture):
    """Fixture for Claude API configuration and setup."""

    def setUp(self):
        super().setUp()

        # Set test environment variables
        import os

        os.environ['ANTHROPIC_AUTH_TOKEN'] = 'test_token'
        os.environ['ANTHROPIC_BASE_URL'] = 'http://localhost:8080'

        # Cleanup environment
        self.addCleanup(lambda: os.environ.pop('ANTHROPIC_AUTH_TOKEN', None))
        self.addCleanup(lambda: os.environ.pop('ANTHROPIC_BASE_URL', None))
