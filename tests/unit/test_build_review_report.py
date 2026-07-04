# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Tests for deterministic review report assembly."""

import json
import pathlib

import fixtures
from testtools import matchers

from tests import test


class TestBuildReviewReport(test.NoDBTestCase):
    """Test conversion from validated findings to final report shape."""

    def setUp(self):
        super().setUp()
        self.builder = test.load_script('tools/build_review_report.py')

    def _finding(self, anchor_kind='changed_line', severity='high'):
        return {
            'id': 'CF-001',
            'category': 'Correctness',
            'title': 'Changed code drops required state',
            'description': 'Changed code drops required scheduler state.',
            'evidence': 'The modified line removes the state update.',
            'source_basis': 'OpenStack correctness guidance',
            'relation_to_change': 'The issue is introduced by this patch.',
            'location': 'nova/compute/manager.py:42',
            'impact': 'Operators may see incorrect scheduling behavior.',
            'recommendation': 'Preserve the scheduler state transition.',
            'severity': severity,
            'confidence': 0.91,
            'anchor_kind': anchor_kind,
            'validation_rationale': 'The changed line directly removes state.',
        }

    def test_build_report_routes_findings_by_anchor_kind(self):
        """Changed-line findings are issues; other anchors are observations."""
        validated = {
            'context': {
                'change': 'Scheduler behavior update',
                'scope': 'nova/compute/manager.py',
                'review_basis': 'OpenStack review guidance',
            },
            'accepted_findings': [
                self._finding(),
                self._finding(anchor_kind='patch_level', severity='warnings'),
                self._finding(anchor_kind='out_of_patch',
                              severity='suggestions'),
            ],
            'rejected_findings': [],
        }
        review_context = {
            'change': 'Fallback change',
            'scope': 'Fallback scope',
            'review_basis': 'Fallback basis',
            'impact': 'Fallback impact statement',
        }

        report = self.builder.build_report(validated, review_context)

        self.assertThat(
            report['context']['impact'],
            matchers.Equals('Fallback impact statement'),
        )
        self.assertThat(len(report['issues']['high']), matchers.Equals(1))
        self.assertThat(
            report['issues']['high'][0]['remediation_priority'],
            matchers.Equals('Before merge'),
        )
        self.assertThat(
            len(report['patch_level_observations']),
            matchers.Equals(1),
        )
        self.assertThat(
            len(report['out_of_patch_observations']),
            matchers.Equals(1),
        )
        self.assertThat(report['statistics']['high'], matchers.Equals(1))
        self.assertThat(
            report['statistics_html_only']['total'],
            matchers.Equals(2),
        )

    def test_summary_considers_html_only_high_severity_findings(self):
        """HTML-only critical/high findings still affect assessment."""
        report = {
            'statistics': {
                'critical': 0,
                'high': 0,
                'warnings': 0,
                'suggestions': 0,
                'total': 0,
            },
            'statistics_html_only': {
                'critical': 0,
                'high': 1,
                'warnings': 0,
                'suggestions': 0,
                'total': 1,
            },
        }

        summary = self.builder.summary_for(report, accepted_count=1)

        self.assertThat(summary['assessment'], matchers.Equals('Needs work'))

    def test_summary_keeps_html_only_suggestions_as_suggestions(self):
        """HTML-only suggestions should not be summarized as warnings."""
        report = {
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
                'suggestions': 1,
                'total': 1,
            },
        }

        summary = self.builder.summary_for(report, accepted_count=1)

        self.assertThat(
            summary['assessment'],
            matchers.Equals('Ready with minor fixes'),
        )
        self.assertThat(
            summary['priority_focus'],
            matchers.Equals('Consider the retained suggestions before merge'),
        )

    def test_cli_writes_report_and_unwrapped_validated_findings(self):
        """The CLI accepts a Claude wrapper and writes deterministic outputs."""
        tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        raw_validated = tempdir / 'validated-findings.raw.json'
        review_context = tempdir / 'review-context.json'
        report = tempdir / 'review-report.raw.json'
        validated_output = tempdir / 'validated-findings.json'
        raw_validated.write_text(
            json.dumps(
                {
                    'type': 'result',
                    'structured_output': {
                        'context': {
                            'change': 'Scheduler behavior update',
                            'scope': 'nova/compute/manager.py',
                            'review_basis': 'OpenStack review guidance',
                        },
                        'accepted_findings': [self._finding()],
                        'rejected_findings': [],
                    },
                }
            ),
            encoding='utf-8',
        )
        review_context.write_text(
            json.dumps({
                'change': 'Fallback',
                'scope': 'Fallback',
                'impact': 'Fallback impact statement',
            }),
            encoding='utf-8',
        )

        self.useFixture(
            fixtures.MonkeyPatch(
                'sys.argv',
                [
                    'build_review_report.py',
                    '--validated-findings',
                    str(raw_validated),
                    '--review-context',
                    str(review_context),
                    '--output',
                    str(report),
                    '--validated-output',
                    str(validated_output),
                ],
            )
        )

        result = self.builder.main()

        self.assertThat(result, matchers.Equals(0))
        self.assertTrue(report.exists())
        self.assertTrue(validated_output.exists())
        parsed = json.loads(report.read_text(encoding='utf-8'))
        self.assertThat(parsed['statistics']['total'], matchers.Equals(1))
