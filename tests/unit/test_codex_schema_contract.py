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

"""Contract tests for Codex-compatible schema strictness."""

import json
import pathlib

from testtools import matchers

from tests import test


class TestCodexSchemaContract(test.NoDBTestCase):
    """Ensure object nodes are explicit enough for Codex schema validation."""

    @staticmethod
    def _load_schema():
        schema_path = pathlib.Path(__file__).resolve().parents[2]
        schema_path /= 'schemas/review-report-schema.json'
        return json.loads(schema_path.read_text())

    def test_all_object_nodes_set_additional_properties_false(self):
        """Every schema object should be closed explicitly."""
        schema = self._load_schema()
        missing = []

        def walk(node, path='root'):
            if isinstance(node, dict):
                if (
                    node.get('type') == 'object'
                    and node.get('additionalProperties') is not False
                ):
                    missing.append(path)
                for key, value in node.items():
                    walk(value, f'{path}.{key}')
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, f'{path}[{index}]')

        walk(schema)
        self.assertThat(missing, matchers.Equals([]))

    def test_all_object_properties_are_required(self):
        """Codex requires object required lists to cover every property."""
        schema = self._load_schema()
        mismatches = []

        def walk(node, path='root'):
            if isinstance(node, dict):
                if node.get('type') == 'object' and 'properties' in node:
                    properties = set(node['properties'].keys())
                    required = set(node.get('required', []))
                    if properties != required:
                        mismatches.append(
                            {
                                'path': path,
                                'missing_required': sorted(properties - required),
                                'extra_required': sorted(required - properties),
                            }
                        )
                for key, value in node.items():
                    walk(value, f'{path}.{key}')
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, f'{path}[{index}]')

        walk(schema)
        self.assertThat(mismatches, matchers.Equals([]))
