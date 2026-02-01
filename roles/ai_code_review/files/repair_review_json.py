#!/usr/bin/env python3
# Copyright 2025 Sean Mooney
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

"""Repair review JSON to conform to the review-report schema.

This script attempts to repair common issues in review JSON that don't
conform to the schema. It's used as a fallback when validation fails.

Repairs performed:
- Add missing required fields with default values
- Fix confidence scores outside valid range
- Correct invalid enum values
- Recalculate statistics.total
- Coerce types (e.g., string "0.8" -> float 0.8)

Exit codes:
    0: Repair successful, output written
    1: Repair failed, JSON could not be fixed
    2: File not found or read error
    3: Invalid JSON syntax that couldn't be recovered
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def load_json_file(filepath: Path) -> tuple[dict[str, Any] | None, str]:
    """Load and parse a JSON file, attempting recovery for common issues.

    Args:
        filepath: Path to the JSON file

    Returns:
        Tuple of (parsed_data, error_message)
        If successful, error_message is empty string
    """
    if not filepath.exists():
        return None, f"File not found: {filepath}"

    try:
        content = filepath.read_text(encoding='utf-8')
    except OSError as e:
        return None, f"Failed to read file: {e}"

    # Try direct parsing first
    try:
        return json.loads(content), ""
    except json.JSONDecodeError:
        pass

    # Attempt recovery: remove trailing commas
    content_fixed = re.sub(r',\s*}', '}', content)
    content_fixed = re.sub(r',\s*]', ']', content_fixed)

    try:
        return json.loads(content_fixed), ""
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON syntax (couldn't recover): {e}"


def repair_context(data: dict[str, Any]) -> dict[str, Any]:
    """Repair the context section.

    Args:
        data: The data to repair

    Returns:
        Repaired data
    """
    if 'context' not in data:
        data['context'] = {}

    ctx = data['context']
    defaults = {
        'change': 'Change description unavailable',
        'scope': 'Scope information unavailable',
        'impact': 'Impact assessment unavailable'
    }

    for field, default in defaults.items():
        if field not in ctx or not ctx[field]:
            ctx[field] = default
        # Truncate if too long (maxLength: 200-300)
        max_len = 200 if field == 'change' else 300
        if len(str(ctx[field])) > max_len:
            ctx[field] = str(ctx[field])[:max_len-3] + "..."

    return data


def repair_statistics(data: dict[str, Any]) -> dict[str, Any]:
    """Repair the statistics section.

    Args:
        data: The data to repair

    Returns:
        Repaired data
    """
    if 'statistics' not in data:
        data['statistics'] = {}

    stats = data['statistics']

    # Ensure all fields exist and are integers
    for field in ['critical', 'high', 'warnings', 'suggestions']:
        if field not in stats:
            stats[field] = 0
        else:
            try:
                stats[field] = int(stats[field])
            except (ValueError, TypeError):
                stats[field] = 0

    # Recalculate total
    stats['total'] = (
        stats['critical'] + stats['high'] +
        stats['warnings'] + stats['suggestions']
    )

    return data


def repair_issue(issue: dict[str, Any], severity: str) -> dict[str, Any]:
    """Repair a single issue.

    Args:
        issue: The issue to repair
        severity: Severity level

    Returns:
        Repaired issue
    """
    # Common required fields
    if 'description' not in issue or not issue['description']:
        issue['description'] = 'Issue description unavailable'
    if len(str(issue['description'])) > 300:
        issue['description'] = str(issue['description'])[:297] + "..."

    if 'location' not in issue or not issue['location']:
        issue['location'] = 'unknown:0'

    # Fix confidence
    if 'confidence' not in issue:
        issue['confidence'] = 0.7
    else:
        try:
            conf = float(issue['confidence'])
            # Clamp to valid range
            conf = max(0.6, min(1.0, conf))
            issue['confidence'] = conf
        except (ValueError, TypeError):
            issue['confidence'] = 0.7

    # Severity-specific fields
    if severity in ['critical', 'high']:
        if 'risk' not in issue or not issue['risk']:
            issue['risk'] = 'Risk assessment unavailable'
        if len(str(issue['risk'])) > 300:
            issue['risk'] = str(issue['risk'])[:297] + "..."

        # Fix remediation_priority enum
        valid_priorities = ['Immediate', 'Before merge', 'Next sprint',
                           'Backlog']
        if issue.get('remediation_priority') not in valid_priorities:
            issue['remediation_priority'] = (
                'Immediate' if severity == 'critical' else 'Before merge'
            )

        if 'why_matters' not in issue or not issue['why_matters']:
            issue['why_matters'] = 'Impact assessment unavailable'
        if len(str(issue['why_matters'])) > 300:
            issue['why_matters'] = str(issue['why_matters'])[:297] + "..."

        if 'recommendation' not in issue or not issue['recommendation']:
            issue['recommendation'] = 'Review and address this issue'
        if len(str(issue['recommendation'])) > 500:
            issue['recommendation'] = str(issue['recommendation'])[:497] + "..."

    elif severity == 'warnings':
        if 'impact' not in issue or not issue['impact']:
            issue['impact'] = 'Potential impact on code quality'
        if len(str(issue['impact'])) > 300:
            issue['impact'] = str(issue['impact'])[:297] + "..."

        if 'suggestion' not in issue or not issue['suggestion']:
            issue['suggestion'] = 'Consider addressing this issue'
        if len(str(issue['suggestion'])) > 500:
            issue['suggestion'] = str(issue['suggestion'])[:497] + "..."

    elif severity == 'suggestions':
        if 'benefit' not in issue or not issue['benefit']:
            issue['benefit'] = 'May improve code quality'
        if len(str(issue['benefit'])) > 300:
            issue['benefit'] = str(issue['benefit'])[:297] + "..."

        if 'recommendation' not in issue or not issue['recommendation']:
            issue['recommendation'] = 'Consider implementing this improvement'
        if len(str(issue['recommendation'])) > 500:
            issue['recommendation'] = str(issue['recommendation'])[:497] + "..."

    return issue


def repair_issues(data: dict[str, Any]) -> dict[str, Any]:
    """Repair the issues section.

    Args:
        data: The data to repair

    Returns:
        Repaired data
    """
    if 'issues' not in data:
        data['issues'] = {}

    issues = data['issues']

    # Ensure all severity arrays exist
    for severity in ['critical', 'high', 'warnings', 'suggestions']:
        if severity not in issues or not isinstance(issues[severity], list):
            issues[severity] = []
        else:
            # Repair each issue
            issues[severity] = [
                repair_issue(issue, severity)
                for issue in issues[severity]
                if isinstance(issue, dict)
            ]

    return data


def repair_summary(data: dict[str, Any]) -> dict[str, Any]:
    """Repair the summary section.

    Args:
        data: The data to repair

    Returns:
        Repaired data
    """
    if 'summary' not in data:
        data['summary'] = {}

    summary = data['summary']

    # Fix assessment enum
    valid_assessments = [
        'Ready', 'Ready with minor fixes', 'Needs work',
        'Requires significant changes', 'Blocked'
    ]
    if summary.get('assessment') not in valid_assessments:
        # Determine appropriate assessment based on issues
        stats = data.get('statistics', {})
        if stats.get('critical', 0) > 0:
            summary['assessment'] = 'Requires significant changes'
        elif stats.get('high', 0) > 0:
            summary['assessment'] = 'Needs work'
        elif stats.get('warnings', 0) > 0:
            summary['assessment'] = 'Ready with minor fixes'
        else:
            summary['assessment'] = 'Ready'

    if 'priority_focus' not in summary or not summary['priority_focus']:
        summary['priority_focus'] = 'Review all identified issues'
    if len(str(summary['priority_focus'])) > 300:
        summary['priority_focus'] = str(summary['priority_focus'])[:297] + "..."

    if 'detailed_summary' not in summary or not summary['detailed_summary']:
        stats = data.get('statistics', {})
        summary['detailed_summary'] = (
            f"Code review identified {stats.get('total', 0)} issues: "
            f"{stats.get('critical', 0)} critical, "
            f"{stats.get('high', 0)} high, "
            f"{stats.get('warnings', 0)} warnings, and "
            f"{stats.get('suggestions', 0)} suggestions."
        )
    if len(str(summary['detailed_summary'])) > 1000:
        summary['detailed_summary'] = (
            str(summary['detailed_summary'])[:997] + "..."
        )

    return data


def update_statistics_from_issues(data: dict[str, Any]) -> dict[str, Any]:
    """Update statistics to match actual issue counts.

    Args:
        data: The data to update

    Returns:
        Updated data
    """
    issues = data.get('issues', {})
    stats = data.setdefault('statistics', {})

    stats['critical'] = len(issues.get('critical', []))
    stats['high'] = len(issues.get('high', []))
    stats['warnings'] = len(issues.get('warnings', []))
    stats['suggestions'] = len(issues.get('suggestions', []))
    stats['total'] = (
        stats['critical'] + stats['high'] +
        stats['warnings'] + stats['suggestions']
    )

    return data


def repair_json(data: dict[str, Any]) -> dict[str, Any]:
    """Perform all repairs on the data.

    Args:
        data: The data to repair

    Returns:
        Repaired data
    """
    data = repair_context(data)
    data = repair_issues(data)
    data = update_statistics_from_issues(data)
    return repair_summary(data)


def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Repair review JSON to conform to schema"
    )
    parser.add_argument(
        "json_file",
        type=Path,
        help="Path to the review JSON file"
    )
    parser.add_argument(
        "--schema",
        type=Path,
        help="Path to JSON schema file (for reference, not used directly)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (defaults to overwriting input)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Load the JSON file
    data, error = load_json_file(args.json_file)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        if "not found" in error.lower():
            return 2
        return 3

    if args.verbose:
        print(f"Loaded JSON from {args.json_file}")

    # Repair the data
    try:
        repaired = repair_json(data)
    except Exception as e:
        print(f"Error during repair: {e}", file=sys.stderr)
        return 1

    # Write the output
    output_path = args.output or args.json_file
    try:
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(repaired, f, indent=2)
        print(f"Repaired JSON written to {output_path}")
    except OSError as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        return 1

    if args.verbose:
        stats = repaired.get('statistics', {})
        print(f"Statistics: {stats.get('total', 0)} total issues")

    return 0


if __name__ == "__main__":
    sys.exit(main())
