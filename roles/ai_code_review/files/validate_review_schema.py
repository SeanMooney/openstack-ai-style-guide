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

"""Validate review JSON against the review-report schema.

This script validates that the generated review report conforms to the
expected JSON schema. It's used as a safety net after Claude's structured
output to catch any edge cases that might slip through.

Exit codes:
    0: Validation passed
    1: Validation failed (schema violations)
    2: File not found or read error
    3: Invalid JSON syntax
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json_file(filepath: Path) -> tuple[dict[str, Any] | None, str]:
    """Load and parse a JSON file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Tuple of (parsed_data, error_message)
        If successful, error_message is empty string
    """
    if not filepath.exists():
        return None, f"File not found: {filepath}"

    try:
        with filepath.open('r', encoding='utf-8') as f:
            return json.load(f), ""
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON syntax: {e}"
    except OSError as e:
        return None, f"Failed to read file: {e}"


def validate_required_fields(data: dict[str, Any]) -> list[str]:
    """Validate required fields in the review report.

    Args:
        data: The data to validate

    Returns:
        List of validation error messages
    """
    errors = []

    # Top-level required fields
    required_top = ['context', 'statistics', 'issues', 'summary']
    for field in required_top:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Context fields
    if 'context' in data:
        ctx = data['context']
        for field in ['change', 'scope', 'impact']:
            if field not in ctx:
                errors.append(f"Missing required field: context.{field}")

    # Statistics fields
    if 'statistics' in data:
        stats = data['statistics']
        for field in ['critical', 'high', 'warnings', 'suggestions', 'total']:
            if field not in stats:
                errors.append(f"Missing required field: statistics.{field}")
            elif not isinstance(stats.get(field), int):
                errors.append(
                    f"Invalid type for statistics.{field}: "
                    f"expected int, got {type(stats.get(field)).__name__}"
                )

        # Validate total equals sum
        if all(field in stats for field in
               ['critical', 'high', 'warnings', 'suggestions', 'total']):
            expected_total = (
                stats['critical'] + stats['high'] +
                stats['warnings'] + stats['suggestions']
            )
            if stats['total'] != expected_total:
                errors.append(
                    f"statistics.total ({stats['total']}) doesn't match "
                    f"sum of severities ({expected_total})"
                )

    # Issues structure
    if 'issues' in data:
        issues = data['issues']
        for severity in ['critical', 'high', 'warnings', 'suggestions']:
            if severity not in issues:
                errors.append(f"Missing required field: issues.{severity}")
            elif not isinstance(issues.get(severity), list):
                errors.append(
                    f"Invalid type for issues.{severity}: "
                    f"expected list, got {type(issues.get(severity)).__name__}"
                )
            else:
                # Validate each issue
                for i, issue in enumerate(issues[severity]):
                    issue_errors = validate_issue(issue, severity, i)
                    errors.extend(issue_errors)

    # Summary fields
    if 'summary' in data:
        summary = data['summary']
        for field in ['assessment', 'priority_focus', 'detailed_summary']:
            if field not in summary:
                errors.append(f"Missing required field: summary.{field}")

        # Validate assessment enum
        valid_assessments = [
            'Ready', 'Ready with minor fixes', 'Needs work',
            'Requires significant changes', 'Blocked'
        ]
        if summary.get('assessment') not in valid_assessments:
            errors.append(
                f"Invalid value for summary.assessment: "
                f"'{summary.get('assessment')}' not in {valid_assessments}"
            )

    return errors


def validate_issue(
    issue: dict[str, Any],
    severity: str,
    index: int
) -> list[str]:
    """Validate a single issue.

    Args:
        issue: The issue data
        severity: Severity level (critical, high, warnings, suggestions)
        index: Index of the issue in the array

    Returns:
        List of validation error messages
    """
    errors = []
    prefix = f"issues.{severity}[{index}]"

    # Common required fields
    for field in ['description', 'confidence', 'location']:
        if field not in issue:
            errors.append(f"Missing required field: {prefix}.{field}")

    # Validate confidence range
    if 'confidence' in issue:
        conf = issue['confidence']
        if not isinstance(conf, (int, float)):
            errors.append(
                f"Invalid type for {prefix}.confidence: "
                f"expected number, got {type(conf).__name__}"
            )
        elif conf < 0.6 or conf > 1.0:
            errors.append(
                f"Invalid value for {prefix}.confidence: "
                f"{conf} not in range [0.6, 1.0]"
            )

    # Severity-specific required fields
    if severity in ['critical', 'high']:
        for field in ['risk', 'remediation_priority', 'why_matters',
                      'recommendation']:
            if field not in issue:
                errors.append(f"Missing required field: {prefix}.{field}")

        # Validate remediation_priority enum
        valid_priorities = ['Immediate', 'Before merge', 'Next sprint',
                           'Backlog']
        if issue.get('remediation_priority') not in valid_priorities:
            errors.append(
                f"Invalid value for {prefix}.remediation_priority: "
                f"'{issue.get('remediation_priority')}' not in "
                f"{valid_priorities}"
            )

    elif severity == 'warnings':
        for field in ['impact', 'suggestion']:
            if field not in issue:
                errors.append(f"Missing required field: {prefix}.{field}")

    elif severity == 'suggestions':
        for field in ['benefit', 'recommendation']:
            if field not in issue:
                errors.append(f"Missing required field: {prefix}.{field}")

    return errors


def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Validate review JSON against schema"
    )
    parser.add_argument(
        "json_file",
        type=Path,
        help="Path to the review JSON file"
    )
    parser.add_argument(
        "--schema",
        type=Path,
        help="Path to JSON schema file (not used for validation, "
             "but validates existence)"
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
        if "json" in error.lower():
            return 3
        return 2

    # Validate the data
    errors = validate_required_fields(data)

    if errors:
        print(f"Validation failed with {len(errors)} error(s):",
              file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    if args.verbose:
        stats = data.get('statistics', {})
        print(f"Validation passed. Statistics: {stats.get('total', 0)} issues")

    return 0


if __name__ == "__main__":
    sys.exit(main())
