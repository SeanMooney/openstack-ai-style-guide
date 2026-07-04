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

"""Normalize teim-review structured output before publication."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SEVERITIES = ('critical', 'high', 'warnings', 'suggestions')

INLINE_THRESHOLDS = {
    'critical': 0.70,
    'high': 0.75,
    'warnings': 0.80,
    'suggestions': 0.85,
}

KEEP_THRESHOLDS = {
    'critical': 0.60,
    'high': 0.60,
    'warnings': 0.65,
    'suggestions': 0.70,
}

EMPTY_STATS = {
    'critical': 0,
    'high': 0,
    'warnings': 0,
    'suggestions': 0,
    'total': 0,
}


def load_json_with_trailing_text(path: Path) -> Any:
    """Load JSON, tolerating trailing text after the first JSON value."""
    content = path.read_text(encoding='utf-8')
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        data, _ = decoder.raw_decode(content)
        return data


def extract_structured_output(data: Any) -> Any:
    """Return Claude structured_output when a CLI wrapper is present."""
    if isinstance(data, dict) and isinstance(data.get('structured_output'), dict):
        return data['structured_output']
    return data


def normalize_file_path(file_path: str) -> str:
    """Normalize workspace-prefixed paths to repository-relative paths."""
    prefixes = [
        '/home/zuul/src/review.opendev.org/',
        '/home/zuul/src/opendev.org/',
        '/home/zuul/src/github.com/',
        '/home/zuul/src/',
    ]
    for prefix in prefixes:
        if file_path.startswith(prefix):
            file_path = file_path.replace(prefix, '', 1)
            parts = file_path.split('/', 2)
            return parts[2] if len(parts) >= 3 else file_path
    if file_path.startswith('/'):
        parts = file_path.lstrip('/').split('/', 2)
        return parts[2] if len(parts) >= 3 else file_path.lstrip('/')
    return file_path


def parse_location(location: Any) -> tuple[str | None, int | None]:
    """Parse a review location into file path and starting line."""
    if not isinstance(location, str):
        return None, None
    match = re.match(r'^([^:]+):(\d+)(?:-\d+)?$', location)
    if not match:
        return None, None
    return normalize_file_path(match.group(1)), int(match.group(2))


def load_changed_files(path: Path | None) -> set[str] | None:
    """Load a changed-file allowlist."""
    if path is None or not path.exists():
        return None
    changed_files = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line:
            changed_files.add(normalize_file_path(line))
    return changed_files


def load_changed_lines(path: Path | None) -> dict[str, list[list[int]]] | None:
    """Load optional changed-line ranges."""
    if path is None or not path.exists():
        return None
    data = load_json_with_trailing_text(path)
    if not isinstance(data, dict):
        return None
    return data


def is_changed_scope(
    issue: dict[str, Any],
    changed_files: set[str] | None,
    changed_lines: dict[str, list[list[int]]] | None,
) -> bool:
    """Return True when an issue is safe to publish inline."""
    file_path, line_number = parse_location(issue.get('location'))
    if file_path is None or line_number is None:
        return False
    if changed_files is not None and file_path not in changed_files:
        return False
    if changed_lines is None:
        return True
    ranges = changed_lines.get(file_path)
    if ranges is None:
        return False
    return any(start <= line_number <= end for start, end in ranges)


def empty_report() -> dict[str, Any]:
    """Return a minimal valid report structure."""
    return {
        'context': {
            'change': 'No change context available',
            'scope': 'No review scope available',
            'impact': 'No impact assessment available',
        },
        'statistics': dict(EMPTY_STATS),
        'statistics_html_only': dict(EMPTY_STATS),
        'issues': {severity: [] for severity in SEVERITIES},
        'positive_observations': [],
        'out_of_patch_observations': [],
        'patch_level_observations': [],
        'summary': {
            'assessment': 'Ready',
            'priority_focus': 'No actionable findings were retained',
            'detailed_summary': (
                'The deterministic normalizer did not retain actionable '
                'findings from the structured review output.'
            ),
        },
    }


def ensure_report_shape(data: Any, diagnostics: dict[str, Any]) -> dict[str, Any]:
    """Fill missing top-level report fields for partial publication."""
    if not isinstance(data, dict):
        diagnostics['fatal_errors'].append('raw report is not a JSON object')
        return empty_report()

    report = empty_report()
    for key in report:
        if key in data:
            report[key] = data[key]

    if not isinstance(report.get('issues'), dict):
        diagnostics['repairs'].append('replaced non-object issues with empty buckets')
        report['issues'] = {severity: [] for severity in SEVERITIES}

    for severity in SEVERITIES:
        if not isinstance(report['issues'].get(severity), list):
            diagnostics['repairs'].append(
                f'replaced non-list issues.{severity} with an empty list'
            )
            report['issues'][severity] = []

    if not isinstance(report.get('positive_observations'), list):
        report['positive_observations'] = []
        diagnostics['repairs'].append('replaced positive_observations')
    if not isinstance(report.get('out_of_patch_observations'), list):
        report['out_of_patch_observations'] = []
        diagnostics['repairs'].append('replaced out_of_patch_observations')
    if not isinstance(report.get('patch_level_observations'), list):
        report['patch_level_observations'] = []
        diagnostics['repairs'].append('replaced patch_level_observations')

    return report


def normalize_issues(
    report: dict[str, Any],
    changed_files: set[str] | None,
    changed_lines: dict[str, list[list[int]]] | None,
    diagnostics: dict[str, Any],
    preserve_html_stats: bool = False,
) -> None:
    """Normalize issue routing and statistics in place."""
    inline_stats = dict(EMPTY_STATS)
    html_stats = dict(report.get('statistics_html_only', EMPTY_STATS))
    if not preserve_html_stats:
        html_stats = dict(EMPTY_STATS)
    for name in (*SEVERITIES, 'total'):
        if not isinstance(html_stats.get(name), int):
            html_stats[name] = 0
    normalized = {severity: [] for severity in SEVERITIES}

    for severity in SEVERITIES:
        for index, issue in enumerate(report['issues'].get(severity, [])):
            finding_id = issue.get('id') or f'{severity}[{index}]'
            if not isinstance(issue, dict):
                diagnostics['dropped_findings'].append(
                    {'id': finding_id, 'reason': 'issue is not an object'}
                )
                continue

            confidence = issue.get('confidence')
            if not isinstance(confidence, int | float):
                diagnostics['dropped_findings'].append(
                    {'id': finding_id, 'reason': 'missing numeric confidence'}
                )
                continue
            confidence = float(confidence)
            if confidence < KEEP_THRESHOLDS[severity]:
                diagnostics['dropped_findings'].append(
                    {
                        'id': finding_id,
                        'reason': 'below keep threshold',
                        'severity': severity,
                        'confidence': confidence,
                    }
                )
                continue

            target_mode = (
                'inline'
                if confidence >= INLINE_THRESHOLDS[severity]
                else 'html_only'
            )
            if target_mode == 'inline' and not is_changed_scope(
                issue, changed_files, changed_lines
            ):
                diagnostics['downgraded_findings'].append(
                    {
                        'id': finding_id,
                        'reason': 'inline finding outside changed scope',
                        'severity': severity,
                        'location': issue.get('location'),
                    }
                )
                target_mode = 'html_only'

            if issue.get('reporting_mode') != target_mode:
                diagnostics['repairs'].append(
                    f'set {finding_id} reporting_mode to {target_mode}'
                )
            issue['reporting_mode'] = target_mode
            normalized[severity].append(issue)
            if target_mode == 'inline':
                inline_stats[severity] += 1
            else:
                html_stats[severity] += 1

    inline_stats['total'] = sum(inline_stats[name] for name in SEVERITIES)
    html_stats['total'] = sum(html_stats[name] for name in SEVERITIES)
    report['issues'] = normalized
    report['statistics'] = inline_stats
    report['statistics_html_only'] = html_stats


def load_optional_artifact(
    path: Path | None,
    key: str,
    diagnostics: dict[str, Any],
) -> None:
    """Record whether an optional intermediate artifact is usable JSON."""
    if path is None:
        return
    if not path.exists():
        diagnostics['missing_artifacts'].append(str(path))
        return
    try:
        data = extract_structured_output(load_json_with_trailing_text(path))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        diagnostics['artifact_errors'].append(
            {'artifact': str(path), 'error': str(exc)}
        )
        return
    diagnostics['artifacts'][key] = {
        'path': str(path),
        'type': type(data).__name__,
    }


def normalize_report(
    raw_report: Any,
    changed_files: set[str] | None = None,
    changed_lines: dict[str, list[list[int]]] | None = None,
    preserve_html_stats: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Normalize a structured review report."""
    diagnostics: dict[str, Any] = {
        'repairs': [],
        'dropped_findings': [],
        'downgraded_findings': [],
        'missing_artifacts': [],
        'artifact_errors': [],
        'artifacts': {},
        'fatal_errors': [],
    }
    report = ensure_report_shape(raw_report, diagnostics)
    normalize_issues(
        report,
        changed_files,
        changed_lines,
        diagnostics,
        preserve_html_stats=preserve_html_stats,
    )
    return report, diagnostics


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description='Normalize teim-review structured report output'
    )
    parser.add_argument('--raw-report', required=True, type=Path)
    parser.add_argument('--candidate-findings', type=Path)
    parser.add_argument('--validated-findings', type=Path)
    parser.add_argument('--changed-files', type=Path)
    parser.add_argument('--changed-lines', type=Path)
    parser.add_argument('--schema', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--diagnostics', required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    """Run the normalizer CLI."""
    args = parse_args()
    try:
        raw_data = load_json_with_trailing_text(args.raw_report)
        raw_report = extract_structured_output(raw_data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f'ERROR: failed to read raw report: {exc}', file=sys.stderr)
        return 1

    changed_files = load_changed_files(args.changed_files)
    changed_lines = load_changed_lines(args.changed_lines)
    report, diagnostics = normalize_report(
        raw_report,
        changed_files,
        changed_lines,
        preserve_html_stats=(
            args.validated_findings is not None and args.validated_findings.exists()
        ),
    )
    load_optional_artifact(
        args.candidate_findings, 'candidate_findings', diagnostics
    )
    load_optional_artifact(
        args.validated_findings, 'validated_findings', diagnostics
    )
    if args.schema is not None and args.schema.exists():
        diagnostics['artifacts']['schema'] = {'path': str(args.schema)}

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.diagnostics.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    args.diagnostics.write_text(
        json.dumps(diagnostics, indent=2) + '\n',
        encoding='utf-8',
    )
    print(f'Normalized review report written to {args.output}')
    print(f'Review diagnostics written to {args.diagnostics}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
