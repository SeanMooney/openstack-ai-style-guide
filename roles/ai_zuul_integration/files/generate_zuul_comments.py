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

"""Generate Zuul file comments from JSON code review data.

This script reads structured JSON review reports and extracts issues with
file locations to generate Zuul inline comments in the proper format.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def parse_location(location: str) -> Tuple[Optional[str], Optional[int]]:
    """Parse location string into file path and line number.

    Args:
        location: Location string (e.g., "path/to/file.py:123")

    Returns:
        Tuple of (file_path, line_number) or (None, None) if invalid
    """
    # Pattern: path/to/file.ext:line or path/to/file.ext:start-end
    match = re.match(r'^([^:]+):(\d+)(?:-\d+)?$', location)
    if match:
        file_path = normalize_file_path(match.group(1))
        line_number = int(match.group(2))
        return file_path, line_number
    return None, None


def normalize_file_path(file_path: str) -> str:
    """Normalize file path to be relative to git repo root.

    Args:
        file_path: File path (may include Zuul prefixes or absolute paths)

    Returns:
        Normalized relative path
    """
    # Remove common Zuul path prefixes
    zuul_prefixes = [
        '/home/zuul/src/review.opendev.org/',
        '/home/zuul/src/opendev.org/',
        '/home/zuul/src/',
    ]

    # Check for known Zuul prefixes
    for prefix in zuul_prefixes:
        if file_path.startswith(prefix):
            file_path = file_path.replace(prefix, '', 1)
            # Remove org/project prefix (e.g., "openstack/nova/")
            parts = file_path.split('/', 2)
            if len(parts) >= 3:
                file_path = parts[2]
            break
    else:
        # Handle other absolute paths
        if file_path.startswith('/'):
            # Try to extract relative path from absolute path
            # Look for common patterns like /path/to/org/project/file.py
            parts = file_path.lstrip('/').split('/', 2)
            # Assume format is org/project/file.py, or just strip leading slash
            file_path = parts[2] if len(parts) >= 3 else file_path.lstrip('/')

    return file_path


def format_issue_message(issue: Dict[str, Any], severity: str) -> str:
    """Format issue as a well-structured message for Zuul inline comment.

    Args:
        issue: Issue dictionary from JSON
        severity: Severity level (critical, high, warning, suggestion)

    Returns:
        Formatted message string
    """
    description = issue.get('description', 'No description')
    confidence = issue.get('confidence', 0.0)

    # Start with description
    parts = [description, ""]

    # Add severity and confidence
    parts.append(f"**Severity**: {severity.upper()} | **Confidence**: {confidence:.1f}")
    parts.append("")

    # Add severity-specific fields
    if severity in ['critical', 'high']:
        if 'risk' in issue:
            parts.append(f"**Risk**: {issue['risk']}")
            parts.append("")
        if 'remediation_priority' in issue:
            parts.append(f"**Priority**: {issue['remediation_priority']}")
        if 'why_matters' in issue:
            parts.append(f"**Why This Matters**: {issue['why_matters']}")
            parts.append("")
        if 'recommendation' in issue:
            parts.append("**Recommendation**:")
            parts.append(issue['recommendation'])

    elif severity == 'warning':
        if 'impact' in issue:
            parts.append(f"**Impact**: {issue['impact']}")
            parts.append("")
        if 'suggestion' in issue:
            parts.append("**Suggestion**:")
            parts.append(issue['suggestion'])

    elif severity == 'suggestion':
        if 'benefit' in issue:
            parts.append(f"**Benefit**: {issue['benefit']}")
            parts.append("")
        if 'recommendation' in issue:
            parts.append("**Recommendation**:")
            parts.append(issue['recommendation'])

    return '\n'.join(parts)


def map_severity_to_level(severity: str) -> str:
    """Map review severity to Zuul comment level.

    Args:
        severity: Review severity (critical, high, warning, suggestion)

    Returns:
        Zuul level (error, warning, info)
    """
    severity_map = {
        'critical': 'error',
        'high': 'error',
        'warning': 'warning',
        'suggestion': 'info',
    }
    return severity_map.get(severity.lower(), 'info')


def extract_file_comments(review_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Extract file comments from review JSON data.

    Args:
        review_data: Parsed JSON review report

    Returns:
        Dictionary mapping file paths to lists of comments
    """
    file_comments: Dict[str, List[Dict[str, Any]]] = {}
    issues = review_data.get('issues', {})

    # Process all severity levels
    for severity in ['critical', 'high', 'warnings', 'suggestions']:
        severity_key = severity  # JSON uses 'warnings', not 'warning'
        severity_label = severity.rstrip('s')  # Remove trailing 's' for label

        for issue in issues.get(severity_key, []):
            location = issue.get('location', '')
            if not location:
                continue  # Skip issues without file locations

            file_path, line_number = parse_location(location)
            if not file_path or not line_number:
                continue  # Skip invalid locations

            # Format message
            message = format_issue_message(issue, severity_label)
            level = map_severity_to_level(severity_label)

            # Create comment
            comment = {
                'line': line_number,
                'message': message,
                'level': level,
            }

            # Add to file comments
            if file_path not in file_comments:
                file_comments[file_path] = []
            file_comments[file_path].append(comment)

    return file_comments


def generate_zuul_return_data(review_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complete zuul_return data structure.

    Args:
        review_data: Parsed JSON review report

    Returns:
        Zuul return data dictionary
    """
    file_comments = extract_file_comments(review_data)

    return {
        'zuul': {
            'file_comments': file_comments
        }
    }


def print_summary(file_comments: Dict[str, List[Dict[str, Any]]]) -> None:
    """Print summary of extracted comments to stderr.

    Args:
        file_comments: Dictionary of file comments
    """
    total_comments = sum(len(comments) for comments in file_comments.values())
    print(f"Extracted {total_comments} comments across {len(file_comments)} files", file=sys.stderr)

    # Count by level
    level_counts = {'error': 0, 'warning': 0, 'info': 0}
    for comments in file_comments.values():
        for comment in comments:
            level = comment.get('level', 'info')
            level_counts[level] = level_counts.get(level, 0) + 1

    print(
        f"Breakdown: {level_counts['error']} errors, "
        f"{level_counts['warning']} warnings, "
        f"{level_counts['info']} info",
        file=sys.stderr
    )


def validate_zuul_schema(data: Dict[str, Any]) -> bool:
    """Basic validation of Zuul return data schema.

    Args:
        data: Zuul return data to validate

    Returns:
        True if valid, False otherwise
    """
    # Check top-level structure
    if 'zuul' not in data:
        print("Error: Missing 'zuul' key in return data", file=sys.stderr)
        return False

    if 'file_comments' not in data['zuul']:
        print("Error: Missing 'file_comments' key in zuul data", file=sys.stderr)
        return False

    file_comments = data['zuul']['file_comments']
    if not isinstance(file_comments, dict):
        print("Error: 'file_comments' must be a dictionary", file=sys.stderr)
        return False

    # Check each file's comments
    for file_path, comments in file_comments.items():
        if not isinstance(comments, list):
            print(f"Error: Comments for '{file_path}' must be a list", file=sys.stderr)
            return False

        for idx, comment in enumerate(comments):
            if not isinstance(comment, dict):
                print(f"Error: Comment {idx} in '{file_path}' must be a dict", file=sys.stderr)
                return False

            # Check required fields
            if 'line' not in comment:
                print(f"Error: Comment {idx} in '{file_path}' missing 'line'", file=sys.stderr)
                return False

            if 'message' not in comment:
                print(f"Error: Comment {idx} in '{file_path}' missing 'message'", file=sys.stderr)
                return False

            # Validate field types
            if not isinstance(comment['line'], int):
                print(f"Error: 'line' in comment {idx} of '{file_path}' must be int", file=sys.stderr)
                return False

            if not isinstance(comment['message'], str):
                print(f"Error: 'message' in comment {idx} of '{file_path}' must be str", file=sys.stderr)
                return False

            # Validate level if present
            if 'level' in comment:
                level = comment['level']
                if level not in ['error', 'warning', 'info']:
                    print(
                        f"Error: 'level' in comment {idx} of '{file_path}' must be "
                        f"'error', 'warning', or 'info', got '{level}'",
                        file=sys.stderr
                    )
                    return False

    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Zuul file comments from JSON review report"
    )
    parser.add_argument(
        "json_file",
        type=Path,
        help="Path to the review JSON file"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file for Zuul return JSON (default: stdout)"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary of extracted comments to stderr"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        default=True,
        help="Validate schema before output (default: True)"
    )

    args = parser.parse_args()

    # Read JSON file
    try:
        with args.json_file.open('r') as f:
            review_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found: {args.json_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"Loaded review data from {args.json_file}", file=sys.stderr)

    # Generate Zuul return data
    zuul_data = generate_zuul_return_data(review_data)

    # Validate schema
    if args.validate:
        if not validate_zuul_schema(zuul_data):
            print("Schema validation failed", file=sys.stderr)
            sys.exit(1)
        if args.verbose:
            print("Schema validation passed", file=sys.stderr)

    # Print summary if requested
    if args.summary:
        print_summary(zuul_data['zuul']['file_comments'])

    # Output JSON
    json_str = json.dumps(zuul_data, indent=2)
    if args.output:
        try:
            args.output.write_text(json_str)
            if args.verbose:
                print(f"✓ Zuul return data written to {args.output}", file=sys.stderr)
        except OSError as e:
            print(f"Error: Failed to write output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
