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

"""
Anti-patterns to avoid in OpenStack code generation.

This file demonstrates common mistakes that AI tools make when generating
OpenStack Python code. Each pattern shown here violates OpenStack hacking
rules and should be avoided.
"""

# WRONG: Import organization is incorrect
from nova import utils  # Should be in local imports section
import os  # Should be in standard library section
from oslo_log import log  # Should be grouped with other oslo imports

# WRONG: Missing proper import grouping and spacing
import json
import sys
from oslo_config import cfg
from nova import exception

LOG = log.getLogger(__name__)


class BadResourceManager:
    """Example class showing anti-patterns to avoid."""

    # WRONG: Mutable default arguments (will cause H232 error)
    def process_items(self, items=[]):
        items.append('processed')
        return items

    def risky_operation(self):
        """Example showing bad exception handling."""
        try:
            result = self._dangerous_call()
            return result
        except:  # WRONG: H201 - bare except clause
            # This will fail OpenStack CI
            LOG.error('Something went wrong')
            return None

    def string_formatting_bad(self, user_id, count):
        """Examples of incorrect string formatting."""
        # WRONG: H702 - f-string in logging
        LOG.info(f'User {user_id} has {count} items')
        
        # WRONG: H702 - .format() in logging
        LOG.error('Failed to process user {}'.format(user_id))
        
        # WRONG: H501 - using locals() in string formatting
        message = "User %(user_id)s processed" % locals()
        
        return message

    def bad_line_length_example(self, very_long_parameter_name, another_long_parameter, third_parameter, fourth_parameter):
        """This line is too long and will fail H501 check."""
        # WRONG: Line exceeds 79 characters
        very_long_variable_name_that_exceeds_limit = very_long_parameter_name + another_long_parameter + third_parameter
        
        return very_long_variable_name_that_exceeds_limit

    def incorrect_context_usage(self, filename):
        """Shows incorrect file handling."""
        # WRONG: Not using context manager for file operations
        file_handle = open(filename, 'r')
        data = file_handle.read()
        file_handle.close()  # Easy to forget, creates resource leaks
        
        return data

    def bad_variable_naming(self):
        """Shows incorrect naming conventions."""
        # WRONG: camelCase variables (should be snake_case)
        userName = 'test_user'
        itemCount = 42
        
        # WRONG: Single letter variables in non-trivial contexts
        x = self._get_data()
        
        return userName, itemCount, x

    # WRONG: Method name should be snake_case
    def GetActiveUsers(self):
        """Method names should use snake_case, not PascalCase."""
        pass

    def _dangerous_call(self):
        """Simulates a risky operation."""
        raise ValueError("Something went wrong")


# WRONG: Class name should be PascalCase
class badExceptionClass(Exception):
    """Exception class names should use PascalCase."""
    pass


# WRONG: Missing docstring for test class and methods
class TestBadPatterns:
    def test_without_autospec(self):
        # WRONG: H210 - missing autospec=True
        with mock.patch('some.module.function') as mock_func:
            mock_func.return_value = 'test'
            # test code here

    # WRONG: H216 - wrong mock import
    from mock import patch  # Should use: from unittest import mock

    def test_bad_assertions(self):
        result = None
        
        # WRONG: H203 - should use assertIsNone
        self.assertEqual(None, result)
        
        # WRONG: H214 - should use assertIn
        self.assertTrue('key' in {'key': 'value'})
        
        # WRONG: Assertion argument order
        self.assertEqual(result, None)  # Should be (expected, actual)


# WRONG: Module-level constants should be UPPER_CASE
defaultTimeout = 30
maxRetries = 3

# WRONG: Using relative imports (H304)
from .utils import helper_function

# WRONG: Using deprecated string formatting in non-logging context
error_message = "Error code: %d" % (500,)  # Should use f-strings or .format()

# This file intentionally contains violations for educational purposes.
# Never use these patterns in actual OpenStack code!