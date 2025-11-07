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

"""Validate Zuul file comments JSON schema.

This script validates that the generated zuul_return data structure
conforms to the expected schema for file comments.
"""

import json
import sys
from pathlib import Path


def validate_schema(data: dict) -> tuple[bool, str]:
    """Validate Zuul file comments schema.

    Args:
        data: The data structure to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check top-level structure
    if 'zuul' not in data:
        return False, "Missing required key: zuul"

    if 'file_comments' not in data['zuul']:
        return False, "Missing required key: zuul.file_comments"

    file_comments = data['zuul']['file_comments']
    if not isinstance(file_comments, dict):
        return (
            False,
            f"file_comments must be a dict, got {type(file_comments).__name__}"
        )

    # Validate each file's comments
    valid_levels = {'info', 'warning', 'error'}
    for file_path, comments in file_comments.items():
        if not isinstance(comments, list):
            return False, f"Comments for {file_path} must be a list"

        for i, comment in enumerate(comments):
            if not isinstance(comment, dict):
                return (
                    False,
                    f"Comment {i} in {file_path} must be a dict"
                )

            if 'message' not in comment:
                return (
                    False,
                    f"Comment {i} in {file_path} missing required message field"
                )

            if 'level' in comment and comment['level'] not in valid_levels:
                level = comment['level']
                return (
                    False,
                    f"Invalid level {level} in {file_path}, must be "
                    "info/warning/error"
                )

            if 'line' in comment and not isinstance(comment['line'], int):
                return (
                    False,
                    f"line must be integer in {file_path}, got "
                    f"{type(comment['line']).__name__}"
                )

    return True, "Schema validation passed"


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: validate_zuul_schema.py <json_file>\n")
        sys.exit(1)

    json_file = Path(sys.argv[1])

    if not json_file.exists():
        sys.stderr.write(f"Error: File not found: {json_file}\n")
        sys.exit(1)

    try:
        with json_file.open() as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error: Invalid JSON: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: Failed to read file: {e}\n")
        sys.exit(1)

    is_valid, message = validate_schema(data)

    if is_valid:
        sys.stderr.write(f"{message}\n")
        sys.exit(0)
    else:
        sys.stderr.write(f"Schema validation failed: {message}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
