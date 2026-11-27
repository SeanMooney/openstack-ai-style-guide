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

"""Tests for review report normalization."""

import json
import pathlib

import fixtures
from testtools import matchers

from tests import test


class TestNormalizeReviewReport(test.NoDBTestCase):
    """Test deterministic review report normalization."""

    def setUp(self):
        super().setUp()
        self.normalizer = test.load_script('skills/teim-review/scripts/normalize_review_report.py')

    def _issue(self, confidence=0.9, location='nova/compute/manager.py:42'):
        return {
            'description': 'Changed code can return the wrong result',
            'confidence': confidence,
            'reporting_mode': 'html_only',
            'location': location,
            'impact': 'Operators may see incorrect scheduling behavior',
            'suggestion': 'Preserve the existing scheduler state transition',
        }

    def _report(self):
        return {
            'context': {
                'change': 'Scheduler behavior update',
                'scope': 'nova/compute/manager.py scheduler path',
                'impact': 'Moderate behavior impact for scheduling',
            },
            'statistics': {
                'critical': 99,
                'high': 99,
                'warnings': 99,
                'suggestions': 99,
                'total': 99,
            },
            'statistics_html_only': {
                'critical': 99,
                'high': 99,
                'warnings': 99,
                'suggestions': 99,
                'total': 99,
            },
            'issues': {
                'critical': [],
                'high': [],
                'warnings': [self._issue()],
                'suggestions': [],
            },
            'positive_observations': [],
            'out_of_patch_observations': [],
            'patch_level_observations': [],
            'summary': {
                'assessment': 'Needs work',
                'priority_focus': 'Fix the scheduler behavior change',
                'detailed_summary': 'The review found one scheduler issue.',
            },
        }

    def test_extract_structured_output_wrapper(self):
        """Claude CLI wrappers are unwrapped."""
        report = self._report()
        wrapper = {'type': 'result', 'structured_output': report}
        self.assertThat(
            self.normalizer.extract_structured_output(wrapper),
            matchers.Equals(report),
        )

    def test_filtering_last_finding_updates_assessment(self):
        """No retained issues must not leave a stale minor-fix assessment."""
        raw = self._report()
        raw['issues']['warnings'][0]['confidence'] = 0.60
        raw['summary']['assessment'] = 'Ready with minor fixes'

        report, diagnostics = self.normalizer.normalize_report(raw)

        self.assertEqual(0, report['statistics']['total'])
        self.assertEqual(0, report['statistics_html_only']['total'])
        self.assertEqual(1, len(diagnostics['dropped_findings']))
        self.assertEqual('No retained findings',
                         report['summary']['assessment'])
        self.assertIn('not the same as a reviewer producing zero candidates',
                      report['summary']['detailed_summary'])

    def test_html_only_warning_prevents_clean_assessment(self):
        """A warning routed away from inline publication remains visible."""
        raw = self._report()
        raw['issues']['warnings'][0]['confidence'] = 0.70
        report, _diagnostics = self.normalizer.normalize_report(raw)
        self.assertEqual(0, report['statistics']['total'])
        self.assertEqual(1, report['statistics_html_only']['total'])
        self.assertEqual('Ready with minor fixes',
                         report['summary']['assessment'])

    def test_missing_summary_is_incomplete_even_with_empty_findings(self):
        """An absent completion summary cannot imply a clean review."""
        report, _diagnostics = self.normalizer.normalize_report({})
        self.assertEqual('Incomplete', report['summary']['assessment'])

    def test_inline_routing_and_stats_are_recalculated(self):
        """High-confidence changed-line issues become inline comments."""
        report, diagnostics = self.normalizer.normalize_report(
            self._report(),
            changed_files={'nova/compute/manager.py'},
            changed_lines=None,
        )

        issue = report['issues']['warnings'][0]
        self.assertThat(issue['reporting_mode'], matchers.Equals('inline'))
        self.assertThat(report['statistics']['warnings'], matchers.Equals(1))
        self.assertThat(report['statistics']['total'], matchers.Equals(1))
        self.assertThat(
            report['statistics_html_only']['total'],
            matchers.Equals(0),
        )
        self.assertThat(diagnostics['repairs'], matchers.Not(matchers.Equals([])))

    def test_deleted_file_is_retained_html_only_without_line_scope(self):
        """Review deletions without emitting anchors into missing files."""
        project = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        (project / 'kept.py').write_text('value = 1\n')
        (project / 'removed.py').write_text('removed = True\n')
        (project / 'removed.py').unlink()
        raw = self._report()
        raw['issues']['warnings'] = [
            self._issue(location='kept.py:1'),
            self._issue(location='removed.py:1'),
        ]

        report, diagnostics = self.normalizer.normalize_report(
            raw, changed_files={'kept.py', 'removed.py'}, project_dir=project,
        )

        issues = report['issues']['warnings']
        self.assertEqual(['inline', 'html_only'],
                         [issue['reporting_mode'] for issue in issues])
        self.assertEqual('removed.py:1', issues[1]['location'])
        self.assertEqual(1, report['statistics']['warnings'])
        self.assertEqual(1, report['statistics_html_only']['warnings'])
        self.assertEqual([], diagnostics['dropped_findings'])

    def test_missing_file_is_not_inline_even_with_line_ranges(self):
        project = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        raw = self._report()
        raw['issues']['warnings'] = [self._issue(location='removed.py:1')]

        report, _diagnostics = self.normalizer.normalize_report(
            raw, changed_files={'removed.py'},
            changed_lines={'removed.py': [[1, 10]]}, project_dir=project,
        )

        self.assertEqual('html_only', report['issues']['warnings'][0]['reporting_mode'])

    def test_commit_message_anchor_needs_no_real_file(self):
        project = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        raw = self._report()
        raw['issues']['warnings'] = [self._issue(location='/COMMIT_MSG:1')]

        report, _diagnostics = self.normalizer.normalize_report(
            raw, changed_files=set(), changed_lines={}, project_dir=project,
        )

        self.assertEqual('inline', report['issues']['warnings'][0]['reporting_mode'])

    def test_confidence_is_rounded_before_routing(self):
        """Routing and persisted JSON use the same confidence value."""
        report = self._report()
        report['issues']['warnings'][0]['confidence'] = 0.7996

        normalized, _diagnostics = self.normalizer.normalize_report(
            report,
            changed_files={'nova/compute/manager.py'},
            changed_lines=None,
        )

        issue = normalized['issues']['warnings'][0]
        self.assertThat(issue['confidence'], matchers.Equals(0.8))
        self.assertThat(issue['reporting_mode'], matchers.Equals('inline'))

    def test_github_workspace_path_matches_changed_file(self):
        """GitHub Zuul checkout paths normalize to repo-relative paths."""
        report = self._report()
        report['issues']['warnings'][0]['location'] = (
            '/home/zuul/src/github.com/SeanMooney/'
            'openstack-ai-style-guide/nova/compute/manager.py:42'
        )

        normalized, _diagnostics = self.normalizer.normalize_report(
            report,
            changed_files={'nova/compute/manager.py'},
            changed_lines=None,
        )

        issue = normalized['issues']['warnings'][0]
        self.assertThat(issue['reporting_mode'], matchers.Equals('inline'))
        self.assertThat(normalized['statistics']['warnings'], matchers.Equals(1))

    def test_commit_message_location_remains_inline(self):
        """The synthetic commit-message file bypasses source allowlists."""
        report = self._report()
        report['issues']['warnings'][0]['location'] = '/COMMIT_MSG:1'

        normalized, _diagnostics = self.normalizer.normalize_report(
            report,
            changed_files={'nova/compute/manager.py'},
            changed_lines={'nova/compute/manager.py': [[1, 100]]},
        )

        issue = normalized['issues']['warnings'][0]
        self.assertThat(issue['reporting_mode'], matchers.Equals('inline'))
        self.assertThat(issue['location'], matchers.Equals('/COMMIT_MSG:1'))

    def test_changed_file_filter_downgrades_inline_finding(self):
        """Inline-eligible findings outside changed files are HTML-only."""
        report, diagnostics = self.normalizer.normalize_report(
            self._report(),
            changed_files={'nova/virt/driver.py'},
            changed_lines=None,
        )

        issue = report['issues']['warnings'][0]
        self.assertThat(issue['reporting_mode'], matchers.Equals('html_only'))
        self.assertThat(report['statistics']['total'], matchers.Equals(0))
        self.assertThat(
            report['statistics_html_only']['warnings'],
            matchers.Equals(1),
        )
        self.assertThat(
            diagnostics['downgraded_findings'][0]['reason'],
            matchers.Contains('outside changed scope'),
        )

    def test_changed_line_filter_downgrades_inline_finding(self):
        """Inline-eligible findings outside changed lines are HTML-only."""
        report, _diagnostics = self.normalizer.normalize_report(
            self._report(),
            changed_files={'nova/compute/manager.py'},
            changed_lines={'nova/compute/manager.py': [[1, 10]]},
        )

        issue = report['issues']['warnings'][0]
        self.assertThat(issue['reporting_mode'], matchers.Equals('html_only'))

    def test_below_keep_threshold_is_dropped(self):
        """Low-confidence suggestions are removed from the report."""
        report = self._report()
        report['issues']['warnings'] = []
        report['issues']['suggestions'] = [
            {
                'description': 'Small cleanup opportunity',
                'confidence': 0.65,
                'reporting_mode': 'inline',
                'location': 'nova/compute/manager.py:42',
                'impact': 'Slightly clearer local code structure',
                'recommendation': 'Rename the local variable for clarity',
            }
        ]

        normalized, diagnostics = self.normalizer.normalize_report(
            report,
            changed_files={'nova/compute/manager.py'},
            changed_lines=None,
        )

        self.assertThat(normalized['issues']['suggestions'], matchers.Equals([]))
        self.assertThat(normalized['statistics']['total'], matchers.Equals(0))
        self.assertThat(
            diagnostics['dropped_findings'][0]['reason'],
            matchers.Equals('below keep threshold'),
        )

    def test_cli_writes_output_and_diagnostics(self):
        """The CLI writes normalized report and diagnostics files."""
        tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        raw_report = tempdir / 'review-report.raw.json'
        validated = tempdir / 'validated-findings.json'
        validated.write_text(json.dumps({
            'context': {
                'change': 'Test normalization', 'scope': 'Test scope',
                'review_basis': 'Static fixture review completed',
            },
            'accepted_findings': [], 'rejected_findings': [],
        }))
        output = tempdir / 'review-report.json'
        diagnostics = tempdir / 'review-validation.json'
        raw_report.write_text(
            json.dumps(
                {
                    'type': 'result',
                    'structured_output': self._report(),
                }
            ),
            encoding='utf-8',
        )

        self.useFixture(
            fixtures.MonkeyPatch(
                'sys.argv',
                [
                    'normalize_review_report.py',
                    '--project-dir',
                    str(tempdir),
                    '--raw-report',
                    str(raw_report),
                    '--validated-findings',
                    str(validated),
                    '--output',
                    str(output),
                    '--diagnostics',
                    str(diagnostics),
                ],
            )
        )

        result = self.normalizer.main()
        self.assertThat(result, matchers.Equals(0))
        self.assertTrue(output.exists())
        self.assertTrue(diagnostics.exists())

    def test_cli_requires_successful_validated_findings(self):
        """Omitted, missing, malformed, and failed validator outputs fail."""
        tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        raw = tempdir / 'raw.json'
        validated = tempdir / 'validated.json'
        output = tempdir / 'report.json'
        diagnostics = tempdir / 'diagnostics.json'
        raw.write_text(json.dumps(self._report()))
        arguments = [
            'normalize_review_report.py', '--raw-report', str(raw),
            '--project-dir', str(tempdir), '--output', str(output),
            '--diagnostics', str(diagnostics),
        ]
        self.useFixture(fixtures.MonkeyPatch('sys.argv', arguments))
        self.assertEqual(2, self.assertRaises(SystemExit,
                                            self.normalizer.main).code)
        arguments.extend(['--validated-findings', str(validated)])
        self.assertEqual(1, self.normalizer.main())
        for payload in ['{', '{}', '{"is_error": true, "structured_output": {}}']:
            validated.write_text(payload)
            self.assertEqual(1, self.normalizer.main())
        self.assertFalse(output.exists())
        self.assertFalse(diagnostics.exists())

    def test_cli_preserves_critical_patch_level_assessment(self):
        """Required validator output retains critical observation severity."""
        tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        raw = tempdir / 'raw.json'
        validated_path = tempdir / 'validated.json'
        output = tempdir / 'report.json'
        diagnostics = tempdir / 'diagnostics.json'
        finding = {
            'id': 'CF-001', 'category': 'correctness',
            'title': 'Patch loses persisted state',
            'description': 'The patch loses persisted scheduler state.',
            'evidence': 'The changed operation removes persisted state.',
            'source_basis': 'Changed source code',
            'relation_to_change': 'State loss is introduced by the patch.',
            'location': None, 'impact': 'Operators lose their stored state.',
            'recommendation': 'Preserve the state before returning success.',
            'severity': 'critical', 'confidence': 0.95,
            'anchor_kind': 'patch_level',
            'validation_rationale': 'State loss follows from the changed code.',
        }
        validated = {
            'context': {
                'change': 'Change scheduler behavior', 'scope': 'Scheduler',
                'review_basis': 'Static review and validation completed',
            },
            'accepted_findings': [finding], 'rejected_findings': [],
        }
        builder = test.load_script(
            'skills/teim-review/scripts/build_review_report.py'
        )
        raw.write_text(json.dumps(builder.build_report(validated, {})))
        validated_path.write_text(json.dumps(validated))
        self.useFixture(fixtures.MonkeyPatch('sys.argv', [
            'normalize_review_report.py', '--raw-report', str(raw),
            '--project-dir', str(tempdir), '--output', str(output),
            '--diagnostics', str(diagnostics),
            '--validated-findings', str(validated_path),
        ]))
        self.assertEqual(0, self.normalizer.main())
        report = json.loads(output.read_text())
        self.assertEqual(0, report['statistics']['total'])
        self.assertEqual(1, report['statistics_html_only']['critical'])
        self.assertEqual('Blocked', report['summary']['assessment'])
