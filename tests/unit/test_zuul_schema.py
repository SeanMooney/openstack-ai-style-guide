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

"""Test cases for Zuul schema validation."""

from testtools import matchers

from tests import test


class TestValidateZuulSchema(test.NoDBTestCase):
    """Test cases for validate_zuul_schema.py."""

    def setUp(self):
        super().setUp()
        self.validate_schema = test.load_script(
            'roles/ai_zuul_integration/files/validate_zuul_schema.py'
        )

    def test_valid_file_comments_schema(self):
        """Test validation of valid Zuul file comments."""
        valid_data = {
            'zuul': {
                'file_comments': {
                    'roles/ai_code_review/tasks/main.yaml': [
                        {'message': 'Test comment', 'line': 25, 'level': 'error'}
                    ]
                }
            }
        }

        is_valid, message = self.validate_schema.validate_schema(valid_data)
        self.assertTrue(is_valid)
        self.assertThat(message, matchers.Equals('Schema validation passed'))

    def test_missing_required_zuul_key(self):
        """Test validation fails without zuul key."""
        invalid_data = {'file_comments': {}}

        is_valid, message = self.validate_schema.validate_schema(invalid_data)
        self.assertFalse(is_valid)
        self.assertThat(message, matchers.Contains('Missing required key: zuul'))

    def test_missing_file_comments_key(self):
        """Test validation fails without file_comments."""
        invalid_data = {'zuul': {}}

        is_valid, message = self.validate_schema.validate_schema(invalid_data)
        self.assertFalse(is_valid)
        self.assertThat(
            message, matchers.Contains('Missing required key: zuul.file_comments')
        )

    def test_invalid_comment_level(self):
        """Test validation rejects invalid comment level."""
        invalid_data = {
            'zuul': {
                'file_comments': {
                    'test.py': [
                        {'message': 'Test', 'line': 10, 'level': 'invalid_level'}
                    ]
                }
            }
        }

        is_valid, message = self.validate_schema.validate_schema(invalid_data)
        self.assertFalse(is_valid)
        self.assertThat(message, matchers.Contains('must be info/warning/error'))

    def test_comments_must_be_list(self):
        """Test validation ensures comments are a list."""
        invalid_data = {'zuul': {'file_comments': {'test.py': 'not_a_list'}}}

        is_valid, message = self.validate_schema.validate_schema(invalid_data)
        self.assertFalse(is_valid)
        self.assertThat(message, matchers.Contains('must be a list'))
