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
    def _load_schema(relative_path='schemas/review-report-schema.json'):
        schema_path = pathlib.Path(__file__).resolve().parents[2]
        schema_path /= relative_path
        return json.loads(schema_path.read_text())

    def test_all_object_nodes_set_additional_properties_false(self):
        """Every schema object should be closed explicitly."""
        for schema_name in [
            'schemas/review-report-schema.json',
            'schemas/candidate-findings-schema.json',
            'schemas/validated-findings-schema.json',
        ]:
            self._assert_object_nodes_closed(self._load_schema(schema_name))

    def _assert_object_nodes_closed(self, schema):
        """Every schema object should be closed explicitly."""
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
        """Schema objects require fields unless explicitly normalizer-owned."""
        for schema_name in [
            'schemas/review-report-schema.json',
            'schemas/candidate-findings-schema.json',
            'schemas/validated-findings-schema.json',
        ]:
            self._assert_object_properties_required(
                self._load_schema(schema_name)
            )

    def _assert_object_properties_required(self, schema):
        """Every non-optional object property should be listed as required."""
        mismatches = []

        def walk(node, path='root'):
            if isinstance(node, dict):
                if node.get('type') == 'object' and 'properties' in node:
                    properties = set(node['properties'].keys())
                    required = set(node.get('required', []))
                    optional = set()
                    if path in {
                        'root.$defs.criticalIssue',
                        'root.$defs.highIssue',
                        'root.$defs.warningIssue',
                        'root.$defs.suggestionIssue',
                    }:
                        optional.add('reporting_mode')
                    expected_required = properties - optional
                    if expected_required != required:
                        mismatches.append(
                            {
                                'path': path,
                                'missing_required': sorted(
                                    expected_required - required
                                ),
                                'extra_required': sorted(
                                    required - expected_required
                                ),
                            }
                        )
                for key, value in node.items():
                    walk(value, f'{path}.{key}')
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, f'{path}[{index}]')

        walk(schema)
        self.assertThat(mismatches, matchers.Equals([]))

    def test_review_report_reporting_mode_is_normalizer_owned(self):
        """Raw Claude output may omit routing before normalization."""
        schema = self._load_schema()
        for issue_type in [
            'criticalIssue',
            'highIssue',
            'warningIssue',
            'suggestionIssue',
        ]:
            issue_schema = schema['$defs'][issue_type]
            self.assertThat(
                issue_schema['properties'],
                matchers.Contains('reporting_mode'),
            )
            self.assertThat(
                issue_schema['required'],
                matchers.Not(matchers.Contains('reporting_mode')),
            )

    def test_base_issue_definition_removed(self):
        """Issue definitions should not retain an orphaned baseIssue def."""
        schema = self._load_schema()
        self.assertThat(schema['$defs'], matchers.Not(matchers.Contains('baseIssue')))

    def test_issue_base_fields_stay_aligned(self):
        """Duplicated issue base fields should not drift between severities."""
        schema = self._load_schema()
        defs = schema['$defs']
        base_fields = ['description', 'confidence', 'reporting_mode', 'location']
        reference = {
            field: defs['criticalIssue']['properties'][field]
            for field in base_fields
        }

        for issue_type in [
            'highIssue',
            'warningIssue',
            'suggestionIssue',
        ]:
            properties = defs[issue_type]['properties']
            for field, expected in reference.items():
                self.assertThat(properties[field], matchers.Equals(expected))

    def test_intermediate_schemas_do_not_include_reporting_mode(self):
        """Model handoff schemas should not own publication routing."""
        for schema_name in [
            'schemas/candidate-findings-schema.json',
            'schemas/validated-findings-schema.json',
        ]:
            schema = self._load_schema(schema_name)
            self.assertThat(
                json.dumps(schema),
                matchers.Not(matchers.Contains('reporting_mode')),
            )

    def test_candidate_findings_include_classification_fields(self):
        """Candidate findings carry proposed severity, confidence, and anchor."""
        schema = self._load_schema('schemas/candidate-findings-schema.json')
        finding = schema['properties']['findings']['items']
        required = set(finding['required'])
        self.assertThat(required, matchers.Contains('severity'))
        self.assertThat(required, matchers.Contains('confidence'))
        self.assertThat(required, matchers.Contains('anchor_kind'))

    def test_confidence_fields_allow_full_score_range(self):
        """Schemas accept honest confidence before deterministic filtering."""
        def collect_confidence_fields(schema):
            confidence_fields = []

            def walk(node):
                if isinstance(node, dict):
                    for key, value in node.items():
                        if key == 'confidence' and isinstance(value, dict):
                            confidence_fields.append(value)
                        walk(value)
                elif isinstance(node, list):
                    for value in node:
                        walk(value)

            walk(schema)
            return confidence_fields

        for schema_name in [
            'schemas/review-report-schema.json',
            'schemas/candidate-findings-schema.json',
            'schemas/validated-findings-schema.json',
        ]:
            schema = self._load_schema(schema_name)
            confidence_fields = collect_confidence_fields(schema)
            self.assertThat(confidence_fields, matchers.Not(matchers.Equals([])))
            for field in confidence_fields:
                self.assertThat(field.get('minimum'), matchers.Equals(0.0))
                self.assertThat(field.get('maximum'), matchers.Equals(1.0))
