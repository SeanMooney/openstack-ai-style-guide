#!/usr/bin/env python3
# Copyright 2026 Sean Mooney
#
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

"""Build a review report from validated teim-review findings."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SEVERITIES = ('critical', 'high', 'warnings', 'suggestions')


def load_json(path: Path) -> Any:
    """Load a JSON artifact, unwrapping Claude structured output."""
    data = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(data, dict) and isinstance(data.get('structured_output'), dict):
        return data['structured_output']
    return data


def empty_stats() -> dict[str, int]:
    """Return empty report statistics."""
    stats = {severity: 0 for severity in SEVERITIES}
    stats['total'] = 0
    return stats


def truncate(value: str, limit: int) -> str:
    """Trim a string to a schema-safe length."""
    value = ' '.join(str(value).split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + '...'


def issue_from_finding(finding: dict[str, Any]) -> dict[str, Any]:
    """Convert a changed-line finding to a report issue."""
    severity = finding['severity']
    base = {
        'description': truncate(finding['description'], 300),
        'confidence': finding['confidence'],
        'location': finding['location'],
    }
    if severity in ('critical', 'high'):
        base.update(
            {
                'risk': truncate(finding['impact'], 300),
                'remediation_priority': (
                    'Immediate' if severity == 'critical' else 'Before merge'
                ),
                'why_matters': truncate(finding['impact'], 300),
                'recommendation': truncate(finding['recommendation'], 500),
            }
        )
    elif severity == 'warnings':
        base.update(
            {
                'impact': truncate(finding['impact'], 300),
                'suggestion': truncate(finding['recommendation'], 500),
            }
        )
    else:
        base.update(
            {
                'benefit': truncate(finding['impact'], 300),
                'recommendation': truncate(finding['recommendation'], 500),
            }
        )
    return base


def patch_observation(finding: dict[str, Any]) -> dict[str, str]:
    """Convert a patch-level finding to a report observation."""
    return {
        'description': truncate(finding['description'], 300),
        'impact': truncate(finding['impact'], 300),
        'recommendation': truncate(finding['recommendation'], 500),
    }


def out_of_patch_observation(finding: dict[str, Any]) -> dict[str, str]:
    """Convert an out-of-patch finding to a report observation."""
    return {
        'description': truncate(finding['description'], 300),
        'location': finding['location'] or 'unknown:1',
        'suggestion': truncate(finding['recommendation'], 500),
    }


def context_from_validated(
    validated: dict[str, Any],
    review_context: dict[str, Any],
) -> dict[str, str]:
    """Build final report context."""
    validated_context = validated.get('context', {})
    change = validated_context.get('change') or review_context.get('change')
    scope = validated_context.get('scope') or review_context.get('scope')
    impact = (
        review_context.get('impact')
        or validated_context.get('impact')
        or 'Review impact was not provided by the prepared context'
    )
    return {
        'change': truncate(change or 'No change summary available', 200),
        'scope': truncate(scope or 'No review scope available', 300),
        'impact': truncate(impact, 300),
    }


def summary_for(report: dict[str, Any], accepted_count: int) -> dict[str, str]:
    """Build a deterministic review summary."""
    inline = report['statistics']
    html = report['statistics_html_only']
    total = accepted_count
    if inline['critical'] or html['critical']:
        assessment = 'Blocked'
        focus = 'Address critical review findings before merge'
    elif inline['high'] or html['high']:
        assessment = 'Needs work'
        focus = 'Address high severity review findings before merge'
    elif inline['warnings'] or html['warnings']:
        assessment = 'Ready with minor fixes'
        focus = 'Review the retained warnings and HTML-only observations'
    elif inline['suggestions'] or html['suggestions']:
        assessment = 'Ready with minor fixes'
        focus = 'Consider the retained suggestions before merge'
    else:
        assessment = 'Ready'
        focus = 'No actionable review findings were retained'

    return {
        'assessment': assessment,
        'priority_focus': focus,
        'detailed_summary': (
            f'The review validation stage accepted {total} finding(s). '
            f'{inline["total"]} finding(s) are eligible for inline publication '
            f'before deterministic routing, and {html["total"]} finding(s) are '
            'represented as patch-level or out-of-patch observations.'
        ),
    }


def build_report(
    validated: dict[str, Any],
    review_context: dict[str, Any],
) -> dict[str, Any]:
    """Build a review report from validated findings."""
    report: dict[str, Any] = {
        'context': context_from_validated(validated, review_context),
        'statistics': empty_stats(),
        'statistics_html_only': empty_stats(),
        'issues': {severity: [] for severity in SEVERITIES},
        'patch_level_observations': [],
        'out_of_patch_observations': [],
        'positive_observations': [],
    }

    accepted = validated.get('accepted_findings', [])
    for finding in accepted:
        severity = finding['severity']
        anchor_kind = finding['anchor_kind']
        if anchor_kind == 'changed_line' and finding.get('location'):
            report['issues'][severity].append(issue_from_finding(finding))
            report['statistics'][severity] += 1
        elif anchor_kind == 'out_of_patch':
            report['out_of_patch_observations'].append(
                out_of_patch_observation(finding)
            )
            report['statistics_html_only'][severity] += 1
        else:
            report['patch_level_observations'].append(
                patch_observation(finding)
            )
            report['statistics_html_only'][severity] += 1

    report['statistics']['total'] = sum(
        report['statistics'][severity] for severity in SEVERITIES
    )
    report['statistics_html_only']['total'] = sum(
        report['statistics_html_only'][severity] for severity in SEVERITIES
    )
    report['summary'] = summary_for(report, len(accepted))
    return report


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description='Build review-report.raw.json from validated findings'
    )
    parser.add_argument('--validated-findings', required=True, type=Path)
    parser.add_argument('--review-context', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--validated-output', type=Path)
    return parser.parse_args()


def main() -> int:
    """Run the report builder CLI."""
    args = parse_args()
    try:
        validated = load_json(args.validated_findings)
        review_context = load_json(args.review_context)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f'ERROR: failed to load input artifact: {exc}', file=sys.stderr)
        return 1

    report = build_report(validated, review_context)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if args.validated_output is not None:
        args.validated_output.parent.mkdir(parents=True, exist_ok=True)
        args.validated_output.write_text(
            json.dumps(validated, indent=2) + '\n',
            encoding='utf-8',
        )
    print(f'Review report written to {args.output}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
