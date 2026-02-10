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

"""Zuul context fixtures."""

import json
import pathlib
import tempfile

import fixtures


class ZuulContextFixture(fixtures.Fixture):
    """Fixture to provide mock Zuul CI context.

    Creates temporary files with Zuul execution context for testing.
    """

    def __init__(self, change_number='12345', patchset='6'):
        super().__init__()
        self.change_number = change_number
        self.patchset = patchset

    def setUp(self):
        super().setUp()

        # Create temp directory
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.temp_dir))

        # Create context file
        self.context_file = self._create_context_file()
        self.commit_summary_file = self._create_commit_summary_file()

    def _create_context_file(self):
        """Create mock Zuul context file.

        :returns: Path to context file
        """
        context_path = f'{self.temp_dir}/zuul_context.json'
        context_data = {
            'zuul': {
                'change': self.change_number,
                'patchset': self.patchset,
                'project': {'name': 'openstack/test-project', 'hostname': 'opendev.org'},
                'branch': 'main',
                'ref': 'refs/changes/45/12345/6',
            }
        }

        with pathlib.Path(context_path).open('w') as f:
            json.dump(context_data, f)

        return context_path

    def _create_commit_summary_file(self):
        """Create mock commit summary file.

        :returns: Path to summary file
        """
        summary_path = f'{self.temp_dir}/commit_summary.json'
        summary_data = {
            'change_number': self.change_number,
            'commit_message': 'Test commit\n\nImplements: blueprint test',
            'files_changed': ['roles/ai_code_review/tasks/main.yaml'],
            'author': 'Test Author <test@example.com>',
        }

        with pathlib.Path(summary_path).open('w') as f:
            json.dump(summary_data, f)

        return summary_path
