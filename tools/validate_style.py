#!/usr/bin/env python3
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

"""Style validation tool for OpenStack AI-generated code.

This script performs basic style validation checks on Python files
to ensure they follow OpenStack standards.
"""

import argparse
import ast
import pathlib
import re
import sys


class OpenStackStyleValidator:
    """Validates Python code against OpenStack style guidelines."""

    def __init__(self):
        """Initialize the validator with empty error and warning lists."""
        self.errors = []
        self.warnings = []

    def validate_file(self, file_path):
        """Validate a single Python file."""
        self.errors = []
        self.warnings = []

        try:
            with pathlib.Path(file_path).open(encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            self.errors.append(f'Error reading file: {e}')
            return False

        # Perform validation checks
        self._check_license_header(lines)
        self._check_line_length(lines)
        self._check_import_organization(lines)
        self._check_exception_handling(content)
        self._check_logging_patterns(lines)

        try:
            tree = ast.parse(content)
            self._check_ast_patterns(tree)
        except SyntaxError as e:
            self.errors.append(f'Syntax error: {e}')

        return len(self.errors) == 0

    def _check_license_header(self, lines):
        """Check for proper Apache 2.0 license header."""
        if len(lines) < 10:
            self.errors.append('File too short to contain license header')
            return

        header_text = '\n'.join(lines[:15])
        if 'Apache License' not in header_text:
            self.errors.append('Missing Apache 2.0 license header')

    def _check_line_length(self, lines):
        """Check for lines exceeding 79 characters."""
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                self.errors.append(
                    f'Line {i}: exceeds 79 characters ({len(line)})'
                )

    def _check_import_organization(self, lines):
        """Check import organization and grouping."""
        import_started = False
        import_groups = []
        current_group = []

        for line in lines:
            stripped = line.strip()

            # Skip license header and empty lines
            if not stripped or stripped.startswith('#'):
                if import_started and current_group:
                    import_groups.append(current_group)
                    current_group = []
                continue

            # Check for imports
            if stripped.startswith(('import ', 'from ')):
                import_started = True
                current_group.append(stripped)
            elif import_started:
                # End of imports
                if current_group:
                    import_groups.append(current_group)
                break

        if len(import_groups) > 0:
            self._validate_import_groups(import_groups)

    def _validate_import_groups(self, groups):
        """Validate import group organization."""
        for group in groups:
            # Check for mixed import types within groups
            has_import = any(line.startswith('import ') for line in group)
            has_from = any(line.startswith('from ') for line in group)

            if has_import and has_from:
                self.warnings.append(
                    "Mixed 'import' and 'from' statements in same group"
                )

    def _check_exception_handling(self, content):
        """Check for bare except clauses and other exception anti-patterns."""
        # Check for bare except (H201)
        if re.search(r'except\s*:', content):
            self.errors.append('H201: Bare except clause found')

        # Check for except Exception (should be more specific)
        except_exception_pattern = r'except\s+Exception\s*:'
        if re.search(except_exception_pattern, content):
            self.warnings.append(
                'Consider using more specific exception types'
            )

    def _check_logging_patterns(self, lines):
        """Check logging patterns for delayed interpolation."""
        for i, line in enumerate(lines, 1):
            # Check for f-strings in logging (H702)
            if re.search(r'LOG\.\w+\s*\(\s*f["\']', line):
                self.errors.append(
                    f'Line {i}: H702 - Use delayed interpolation in logging'
                )

            # Check for .format() in logging (H702)
            if re.search(r'LOG\.\w+\s*\([^)]*\.format\s*\(', line):
                self.errors.append(
                    f'Line {i}: H702 - Use delayed interpolation in logging'
                )

    def _check_ast_patterns(self, tree):
        """Check AST for specific patterns."""
        for node in ast.walk(tree):
            # Check for mutable default arguments
            if isinstance(node, ast.FunctionDef):
                self._check_mutable_defaults(node)

            # Check for mock usage patterns
            if isinstance(node, ast.Call):
                self._check_mock_usage(node)

    def _check_mutable_defaults(self, func_node):
        """Check for mutable default arguments (H232)."""
        for default in func_node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.errors.append(
                    f"H232: Mutable default argument in function '{func_node.name}'"
                )

    def _check_mock_usage(self, call_node):
        """Check mock.patch usage for autospec."""
        if (
            isinstance(call_node.func, ast.Attribute)
            and isinstance(call_node.func.value, ast.Name)
            and call_node.func.value.id == 'mock'
            and call_node.func.attr == 'patch'
        ):
            # Check for autospec=True
            has_autospec = any(
                kw.arg == 'autospec' for kw in call_node.keywords
            )
            if not has_autospec:
                self.errors.append('H210: mock.patch missing autospec=True')

    def get_results(self):
        """Return validation results."""
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'passed': len(self.errors) == 0,
        }


def main():
    """Main validation script."""
    parser = argparse.ArgumentParser(
        description='Validate Python files against OpenStack style guidelines'
    )
    parser.add_argument('files', nargs='+', help='Python files to validate')
    parser.add_argument(
        '--warnings-as-errors',
        action='store_true',
        help='Treat warnings as errors',
    )
    parser.add_argument(
        '--quiet', action='store_true', help='Only show errors and warnings'
    )

    args = parser.parse_args()

    validator = OpenStackStyleValidator()
    total_errors = 0
    total_warnings = 0

    for file_path in args.files:
        path = pathlib.Path(file_path)
        if not path.exists():
            print(f'Error: File {file_path} does not exist')
            continue

        if path.suffix != '.py':
            if not args.quiet:
                print(f'Skipping non-Python file: {file_path}')
            continue

        if not args.quiet:
            print(f'Validating {file_path}...')

        is_valid = validator.validate_file(path)
        results = validator.get_results()

        if results['errors']:
            print(f'\nErrors in {file_path}:')
            for error in results['errors']:
                print(f'  ❌ {error}')
            total_errors += len(results['errors'])

        if results['warnings']:
            print(f'\nWarnings in {file_path}:')
            for warning in results['warnings']:
                print(f'  ⚠️  {warning}')
            total_warnings += len(results['warnings'])

        if is_valid and not results['warnings'] and not args.quiet:
            print(f'  ✅ {file_path} passed validation')

    # Summary
    print('\nValidation Summary:')
    print(f'  Errors: {total_errors}')
    print(f'  Warnings: {total_warnings}')

    # Exit code
    if total_errors > 0 or args.warnings_as_errors and total_warnings > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
