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

"""Test cases for tool scripts."""

import pathlib

import fixtures
from testtools import matchers

from tests import test


class TestCountTokens(test.NoDBTestCase):
    """Test cases for count_tokens.py."""

    def setUp(self):
        super().setUp()
        self.count_tokens = test.load_script('tools/count_tokens.py')

    def test_count_python_file_tokens(self):
        """Test token counting for Python file."""
        # Use fixtures.TempDir() for temp file operations (auto-cleanup)
        tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        test_file = tempdir / 'test.py'

        with test_file.open('w') as f:
            f.write('print("hello world")\n')

        result, error = self.count_tokens.analyze_file(str(test_file))
        self.assertThat(error, matchers.Equals(None))
        self.assertThat(result['estimated_tokens'], matchers.GreaterThan(0))

    def test_count_markdown_file_tokens(self):
        """Test token counting for Markdown file."""
        tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        test_file = tempdir / 'test.md'

        with test_file.open('w') as f:
            f.write('# Test Header\n\nContent here\n')

        result, error = self.count_tokens.analyze_file(str(test_file))
        self.assertThat(error, matchers.Equals(None))
        self.assertThat(result['estimated_tokens'], matchers.GreaterThan(0))


class TestValidateStyle(test.NoDBTestCase):
    """Test cases for validate_style.py."""

    def setUp(self):
        super().setUp()
        self.validate_style = test.load_script('tools/validate_style.py')

    def test_validate_good_python_file(self):
        """Test validation of compliant Python file."""
        tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        test_file = tempdir / 'good.py'

        with test_file.open('w') as f:
            f.write(
                '''# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

"""Good Python file with proper license header."""


def test_function():
    """Test function."""
    pass
'''
            )

        validator = self.validate_style.OpenStackStyleValidator()
        is_valid = validator.validate_file(str(test_file))
        self.assertTrue(is_valid)

    def test_validate_bad_python_file_missing_license(self):
        """Test validation detects missing license."""
        tempdir = pathlib.Path(self.useFixture(fixtures.TempDir()).path)
        test_file = tempdir / 'bad.py'

        with test_file.open('w') as f:
            f.write('"""Bad file."""\ndef test():\n    pass\n')

        validator = self.validate_style.OpenStackStyleValidator()
        is_valid = validator.validate_file(str(test_file))
        results = validator.get_results()
        self.assertFalse(is_valid)
        self.assertThat(results['errors'][0].lower(), matchers.Contains('license'))
