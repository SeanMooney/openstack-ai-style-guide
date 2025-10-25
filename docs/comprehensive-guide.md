# OpenStack Python Comprehensive Style Guide for AI Code Generation

> **Comprehensive Guide**: Detailed explanations and examples for AI tools generating OpenStack-compliant Python code.  
> **For quick reference**: See the [OpenStack Python Quick Rules for AI](quick-version)  
> **For working templates**: See [docs/templates/](templates/) for ready-to-use code patterns  
> **For validation workflows**: See [docs/checklists/](checklists/) for pre-submit and review procedures

## Overview for AI Assistants
This guide provides specific instructions for AI coding assistants (Claude Code, aider, etc.) 
to generate Python code that meets OpenStack contribution standards. Follow these rules precisely
to ensure code passes OpenStack's strict linting and review processes.

## 1. Critical Code Generation Rules

### ALWAYS Include Apache License Header
Every Python file MUST start with:
```python
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
```

### Line Length & Formatting
- **Maximum 79 characters per line** (strictly enforced)
- Use 4 spaces for indentation (never tabs)
- UNIX line endings (`\n`) only
- Break long lines using parentheses, not backslashes:
```python
# Correct:
result = some_function(
    argument_one,
    argument_two,
    argument_three
)

# Wrong:
result = some_function(argument_one, argument_two, \
                      argument_three)
```

## 2. Import Organization (Critical for AI)
Always organize imports in exactly this order with blank lines between groups:

```python
# Standard library (alphabetical)
import json
import os
import sys

# Third-party libraries (alphabetical)
import oslo_config
import requests

# OpenStack libraries (alphabetical)
from oslo_config import cfg
from oslo_log import log

# Local project imports (alphabetical)
from nova import exception
from nova import utils
```

**AI Note**: Within each group, separate `import X` from `from X import Y` statements into sub-groups.

## 3. Function & Method Definitions

### Docstring Format (H404/H405 Compliance)
```python
def fetch_resource(resource_id, timeout=30):
    """Fetch a resource from the database.

    :param resource_id: Unique identifier for the resource
    :param timeout: Request timeout in seconds
    :returns: Resource object or None if not found
    :raises: ResourceNotFound if resource doesn't exist
    """
```

### Argument Handling
```python
# Correct: Use None for mutable defaults
def process_items(items=None):
    items = items or []
    # process items

# Wrong: Mutable default arguments
def process_items(items=[]):  # NEVER do this
    # process items
```

## 4. Exception Handling (Strictly Enforced)

### Never Use Bare Except (H201)
```python
# Correct:
try:
    risky_operation()
except (ValueError, TypeError) as e:
    LOG.error('Operation failed: %s', e)

# Wrong:
try:
    risky_operation()
except:  # H201 violation - will fail CI
    LOG.error('Something went wrong')
```

### Specific Exception Patterns
```python
# Handle specific exceptions
try:
    data = json.loads(response)
except json.JSONDecodeError as e:
    raise InvalidDataError('Failed to parse JSON: %s' % e)

# For re-raising, catching BaseException is acceptable
try:
    critical_operation()
except BaseException:
    cleanup_resources()
    raise
```

## 5. Testing Code Generation

### Test Structure with oslotest
OpenStack projects use oslotest for consistent test patterns:

```python
from oslotest import base
from unittest import mock

class TestResourceManager(base.BaseTestCase):
    """Test cases for ResourceManager class."""

    def setUp(self):
        """Set up test fixtures."""
        super(TestResourceManager, self).setUp()
        self.mock_session = mock.MagicMock()
        self.manager = ResourceManager(session=self.mock_session)

    def test_method_success(self):
        """Test successful operation."""
        # Setup
        expected_result = mock.MagicMock()
        self.mock_session.query.return_value.filter_by.return_value.first\
            .return_value = expected_result

        # Execute
        result = self.manager.get_resource('test-id')

        # Verify
        self.assertEqual(expected_result, result)
        self.mock_session.query.assert_called_once()
```

### Mock Usage (H210 - Critical)
```python
# Always use autospec=True
@mock.patch('nova.utils.execute', autospec=True)
def test_command_execution(self, mock_execute):
    mock_execute.return_value = ('output', '')
    # test code

# Mock object methods with autospec
with mock.patch.object(self.manager, '_save_to_database', autospec=True) as mock_save:
    mock_save.return_value = expected_resource
    result = self.manager.create_resource('test')
    mock_save.assert_called_once()

# Wrong - will fail H210 check:
@mock.patch('nova.utils.execute')  # Missing autospec=True
```

### Advanced Assertion Patterns
```python
# Correct assertions (H203, H214, H212 compliant):
self.assertIsNone(result)                    # Not assertEqual(None, result)
self.assertIn('key', dictionary)             # Not assertTrue('key' in dictionary)
self.assertEqual(expected, actual)            # Order matters
self.assertIsInstance(obj, MyClass)            # Not assertEqual(type(obj), MyClass)
self.assertRaises(SpecificException, func)     # Not generic Exception

# Exception testing with context manager
with self.assertRaises(ResourceNotFoundError):
    self.manager.get_resource('nonexistent')

# Multiple assertions in logical groups
self.assertEqual(2, len(results))
self.assertIn('item1', [r.id for r in results])
self.assertIn('item2', [r.id for r in results])
```

### Database Testing Patterns
```python
def test_database_transaction_rollback(self):
    """Test transaction rollback on error."""
    with mock.patch.object(self.manager.session, 'begin') as mock_begin:
        mock_begin.side_effect = db_exception.DBError("Connection failed")
        
        self.assertRaises(DatabaseError, self.manager.create_resource, 
                         {'name': 'test'})
        
        # Verify transaction was attempted
        mock_begin.assert_called_once()

def test_pagination_logic(self):
    """Test pagination edge cases."""
    # Test limit boundary
    instances, has_more = self.manager.list_instances(limit=10)
    self.assertLessEqual(len(instances), 10)
    
    # Test marker functionality
    with mock.patch.object(self.manager, 'session') as mock_session:
        mock_session.query.return_value.filter_by.return_value.filter\
            .return_value.limit.return_value.all.return_value = []
        
        self.manager.list_instances(marker='last-id')
        mock_session.query.return_value.filter_by.return_value.filter\
            .assert_called_with(Instance.id > 'last-id')
```

### Import unittest.mock (H216)
```python
# Correct:
from unittest import mock

# Wrong:
from mock import patch  # H216 violation
```

## 6. Logging & String Formatting

### Logging with Delayed Interpolation
```python
# Correct (H702/H904 compliant):
LOG.info('Processing %d items', len(items))
LOG.error(_('Failed to connect to %s'), server)  # Translatable

# Wrong:
LOG.info(f'Processing {len(items)} items')  # Immediate interpolation
LOG.info('Processing {} items'.format(len(items)))
```

### String Formatting Preferences
```python
# Preferred for regular strings:
message = f'User {username} has {count} items'

# For logging (delayed interpolation):
LOG.debug('User %s has %d items', username, count)

# Multiline strings:
query = ("SELECT * FROM users "
         "WHERE active = true "
         "AND created_at > %s")
```

## 7. Data Structure Formatting

### Dictionary Formatting
```python
# One key-value pair per line for readability:
config = {
    'database_url': 'sqlite:///app.db',
    'debug': True,
    'timeout': 30,
}

# Trailing comma required for single-item tuples:
single_item = ('value',)  # Note the comma
```

### List Comprehensions (Keep Simple)
```python
# Acceptable:
results = [item.id for item in items if item.active]

# Too complex - use regular loop instead:
# results = [process(item) for sublist in nested_list 
#           for item in sublist if complex_condition(item)]
```

## 8. Exception Design Patterns

### Custom Exception Classes
OpenStack projects use structured exception classes with message formatting:

```python
class ModuleError(exception.BaseException):
    """Base exception for MODULE_NAME errors."""
    msg_fmt = "An error occurred in MODULE_NAME: %(reason)s"

class ResourceNotFoundError(ModuleError):
    """Raised when a resource cannot be found."""
    msg_fmt = "Resource %(resource_id)s not found"

class InvalidConfigurationError(ModuleError):
    """Raised when configuration is invalid."""
    msg_fmt = "Invalid configuration: %(config_key)s = %(config_value)s"
```

**Key Pattern Rules:**
- Inherit from appropriate OpenStack exception base class
- Use `msg_fmt` for consistent message formatting
- Support parameter substitution with `%(param)s` syntax
- Create specific exception classes for different error types

### Exception Usage Patterns
```python
def get_resource(self, resource_id):
    if not resource_id:
        raise ValueError("resource_id cannot be empty")
    
    try:
        resource = self._fetch_from_database(resource_id)
        if not resource:
            raise ResourceNotFoundError(resource_id=resource_id)
        return resource
    except (ValueError, TypeError) as e:
        LOG.error("Invalid resource_id format: %s", e)
        raise InvalidInputError(reason=str(e))
    except Exception as e:
        LOG.exception("Unexpected error retrieving resource %s", resource_id)
        raise ModuleError(reason=str(e))
```

## 9. OpenStack-Specific Patterns

### Configuration Options
```python
from oslo_config import cfg

CONF = cfg.CONF

# Define options clearly:
api_opts = [
    cfg.IntOpt('timeout',
               default=30,
               help='API request timeout in seconds'),
    cfg.StrOpt('endpoint',
               help='Service endpoint URL'),
]

CONF.register_opts(api_opts, group='api')
```

### Context Managers for Resources
```python
# Always use context managers:
with open('/etc/nova/nova.conf') as config_file:
    config_data = config_file.read()

# For database connections:
with session.begin():
    instance = session.query(Instance).filter_by(uuid=uuid).one()
    instance.update(updates)
```

### Database Session Patterns
OpenStack uses oslo.db with proper transaction management:

```python
from oslo_db import exception as db_exception

def create_instance(self, instance_data):
    """Create a new database instance with proper error handling."""
    try:
        with self.session.begin():
            instance = Instance(**instance_data)
            self.session.add(instance)
            self.session.flush()  # Get ID without committing
            return instance
    except db_exception.DBDuplicateEntry:
        LOG.error("Instance %s already exists", instance_data['name'])
        raise InstanceExistsError(name=instance_data['name'])
    except db_exception.DBError as e:
        LOG.exception("Database error creating instance")
        raise DatabaseError(reason=str(e))

def update_instance(self, instance_id, updates):
    """Update instance with atomic transaction."""
    try:
        with self.session.begin():
            instance = self.session.query(Instance).filter_by(
                id=instance_id).with_for_update().one()
            if not instance:
                raise InstanceNotFoundError(instance_id=instance_id)
            instance.update(updates)
            return instance
    except db_exception.DBError as e:
        LOG.exception("Failed to update instance %s", instance_id)
        raise DatabaseError(reason=str(e))
```

### Database Query Patterns
```python
# Efficient querying with proper error handling
def get_active_instances(self, limit=None):
    """Get active instances with optional limit."""
    try:
        query = self.session.query(Instance).filter_by(
            deleted=False, active=True)
        if limit:
            query = query.limit(limit)
        return query.all()
    except db_exception.DBError as e:
        LOG.exception("Database error fetching active instances")
        raise DatabaseError(reason=str(e))

# Pagination for large result sets
def list_instances(self, marker=None, limit=None):
    """List instances with pagination support."""
    try:
        query = self.session.query(Instance).filter_by(deleted=False)
        if marker:
            query = query.filter(Instance.id > marker)
        if limit:
            query = query.limit(limit + 1)  # +1 to check for more
        instances = query.all()
        has_more = len(instances) > limit if limit else False
        if has_more:
            instances = instances[:-1]  # Remove the extra
        return instances, has_more
    except db_exception.DBError as e:
        LOG.exception("Error listing instances")
        raise DatabaseError(reason=str(e))
```

### API Service Method Patterns
OpenStack API controllers require specific error handling and response patterns:

```python
import webob.exc
from oslo_log import log

LOG = log.getLogger(__name__)

def api_method(self, request, resource_id):
    """Standard API method with proper error handling."""
    context = request.environ['context']
    
    try:
        resource = self.manager.get_resource(context, resource_id)
        return {'resource': resource}
    except ResourceNotFoundError as e:
        raise webob.exc.HTTPNotFound(
            explanation=e.msg_fmt % e.kwargs)
    except InvalidParameterError as e:
        raise webob.exc.HTTPBadRequest(
            explanation=e.msg_fmt % e.kwargs)
    except Exception as e:
        LOG.exception('Unexpected error in api_method')
        raise webob.exc.HTTPInternalServerError()

def create_resource(self, request, resource_data):
    """Create resource with validation and proper error handling."""
    context = request.environ['context']
    
    try:
        # Validate input
        if not resource_data.get('name'):
            raise InvalidParameterError(param='name', value='missing')
        
        resource = self.manager.create_resource(context, resource_data)
        return {'resource': resource}, 201  # Created status
    except ResourceAlreadyExistsError as e:
        raise webob.exc.HTTPConflict(
            explanation=e.msg_fmt % e.kwargs)
    except Exception as e:
        LOG.exception('Failed to create resource')
        raise webob.exc.HTTPInternalServerError()
```

**Key API Pattern Rules:**
- Extract context from `request.environ['context']`
- Catch specific exceptions and return appropriate HTTP status codes
- Use `webob.exc` for HTTP exceptions with proper explanations
- Log unexpected errors with `LOG.exception()`
- Return 201 status for resource creation
- Always include error explanations in exception messages

## 9. Naming Conventions

### Variable and Function Names
```python
# Correct:
user_count = 10
def get_active_users():
    pass

# Wrong:
userCount = 10  # camelCase not allowed
def GetActiveUsers():  # PascalCase for functions not allowed
```

### Class Names
```python
# Correct:
class DatabaseManager:
    pass

class HTTPSConnection:
    pass

# Exception classes:
class InvalidConfigurationError(Exception):
    pass
```

### Constants
```python
# Module-level constants:
DEFAULT_TIMEOUT = 30
MAX_RETRY_ATTEMPTS = 3
API_VERSION = '2.1'
```

## 10. OpenInfra Foundation AI Policy and DCO Compliance

### Commit Message Requirements (MANDATORY)
All AI-generated contributions MUST include proper commit message labeling per OpenInfra Foundation AI Policy AND Developer Certificate of Origin (DCO) sign-off:

#### OpenStack Commit Message Structure
Follow this exact format for all commits:

```
Subject line: imperative, < 50 chars, no period

Body paragraph explaining the WHY and WHAT of the change.
Wrap at 72 characters. Include enough detail for reviewers
to understand the problem being solved and how the fix works.

For AI contributions, explain the context and approach
used with the AI tool, focusing on the technical decisions
and reasoning behind the implementation.

Generated-By: claude-code (or Assisted-By: github-copilot)
Signed-off-by: Jane Doe <jane.doe@example.com>
Closes-Bug: #1234567
Change-Id: I1234567890abcdef1234567890abcdef12345678
```

#### Subject Line Rules (First Line - CRITICAL)
- **Imperative mood**: "Add user auth" not "Added user auth" or "Adding user auth"
- **Maximum 50 characters** (strictly enforced)
- **No period** at the end
- **Mention affected component**: Include "libvirt", "nova", "api", etc. when relevant
- **Be specific**: "Fix memory leak in compute manager" not "Fix bug"

#### Body Content Requirements
- **Explain WHY first**: What problem does this solve?
- **Explain WHAT**: What changes were made?
- **Explain HOW**: Overall approach (for complex changes)
- **Self-contained**: Don't assume reviewer has access to external bug trackers
- **Include limitations**: Mention known issues or future improvements needed
- **Wrap at 72 characters**

#### For Generative AI (Claude Code, ChatGPT, etc.)
```
Add user authentication module

This module implements OAuth2 authentication for the API service
to address security requirements for multi-tenant access. The
implementation follows the existing Nova auth patterns but adds
support for token refresh and role-based permissions.

I used Claude Code to generate the initial implementation based on
the existing auth patterns in Nova. The generated code included
the OAuth2 flow, token validation, and basic error handling.
Manual modifications were made for OpenStack-specific configuration
handling, integration with existing keystone middleware, and
custom error messages and logging.

Generated-By: claude-code
Signed-off-by: Jane Doe <jane.doe@example.com>
Closes-Bug: #2001234
Implements: blueprint oauth2-authentication
Change-Id: I1234567890abcdef1234567890abcdef12345678
```

#### For Predictive AI (Copilot, Tabnine, etc.)
```
Fix memory leak in compute manager

The compute manager was not properly releasing resources when
instances were deleted, causing memory usage to grow over time
in long-running compute services. This was particularly visible
in environments with high instance turnover.

The fix ensures that all event listeners and cached objects
are properly cleaned up in the instance deletion path. Added
explicit resource cleanup in the _delete_instance method and
improved error handling to prevent partial cleanup states.

I used GitHub Copilot suggestions for the resource cleanup
patterns and error handling blocks. The core logic and OpenStack-
specific integration was written manually.

Assisted-By: github-copilot
Signed-off-by: Jane Doe <jane.doe@example.com>
Closes-Bug: #2001235
Change-Id: I1234567890abcdef1234567890abcdef12345678
```

#### External References and Flags
Place all metadata at the end in this order:
```
# AI labeling (always first in metadata section)
Generated-By: tool-name
# or
Assisted-By: tool-name

# DCO sign-off (required after July 1, 2025)
Signed-off-by: Real Name <email@domain.com>

# Bug references
Closes-Bug: #1234567      # Fully fixes the bug
Partial-Bug: #1234567     # Partial fix, more work needed
Related-Bug: #1234567     # Related but doesn't fix

# Blueprint reference
Implements: blueprint feature-name

# Impact flags (when applicable)
DocImpact: Changes require documentation updates
APIImpact: Modifies public HTTP API
SecurityImpact: Has security implications
UpgradeImpact: Affects upgrade procedures

# Gerrit tracking (auto-generated)
Change-Id: I1234567890abcdef1234567890abcdef12345678
```

#### DCO Sign-off Requirements (REQUIRED)
- **Every commit** must include `Signed-off-by: Your Name <your.email@example.com>`
- **Use your real name** (no pseudonyms or anonymous contributions)
- **Email must match** your Git configuration and Gerrit account
- **Always use the -s flag** when committing:
```bash
git config --global user.name "Your Real Name"
git config --global user.email "your.email@example.com"
git commit -s  # The -s flag adds Signed-off-by automatically
```

### AI Policy: Generated-By vs Assisted-By

#### When to Use "Generated-By:"
Use **"Generated-By:"** for **generative AI** tools that produce substantial code artifacts:
- AI generated complete functions, classes, or modules
- AI created the initial implementation that you then modified
- Substantial portions of the code came from AI prompts
- Examples: Claude Code, ChatGPT, GitHub Copilot (when accepting large completions)

#### When to Use "Assisted-By:"
Use **"Assisted-By:"** for **predictive AI** tools that provide suggestions or minor edits:
- AI provided autocomplete suggestions you accepted
- AI helped with minor refactoring or renaming
- AI made small targeted changes based on prompts
- Examples: GitHub Copilot (autocomplete), Tabnine, code formatting tools

#### Key Principles (ALL AI Usage)
- **Human must be in the loop** - Always review and understand AI-generated code
- **Treat as untrusted source** - Apply the same scrutiny as code from unknown contributors
- **Ensure open source compatibility** - Configure tools to respect licensing
- **Document AI contributions** - Explain what AI generated and what you modified
- **Take responsibility** - Your DCO sign-off certifies you reviewed and approved all content

## 11. AI-Specific Generation Guidelines

### When Generating New Files
1. Start with Apache license header
2. Add module docstring
3. Place module-level constants after docstring, before imports
4. Organize imports per section 2
5. Define classes and functions with proper docstrings

### When Modifying Existing Files
1. Preserve existing license headers
2. Maintain import organization
3. Follow existing code style in the file
4. Add appropriate docstrings to new functions

### AI-Specific Commit Message Guidelines
When using AI tools, ALWAYS include:
1. **Context provided**: Brief description of what guidance was given to the AI
2. **AI contributions**: Which parts used AI assistance (structure, logic, patterns, etc.)
3. **Manual modifications**: What you changed, added, or customized manually
4. **Technical reasoning**: Explain the approach and decisions made
5. **Review confirmation**: Implicitly demonstrate you reviewed all AI-generated code through your explanations

## 12. Common Anti-Patterns to Avoid

For complete examples of anti-patterns to avoid, see [docs/examples/bad/anti_patterns.py](examples/bad/anti_patterns.py) which demonstrates all common violations with explanations.

### Critical Violations (Will Fail CI)

```python
# H201 - Bare except (CRITICAL)
try:
    operation()
except:  # NEVER use bare except
    pass
# Fix: except (ValueError, TypeError) as e:

# H210 - Missing autospec in mock (CRITICAL)
@mock.patch('module.function')  # Missing autospec=True
def test_method(self, mock_func):
    pass
# Fix: @mock.patch('module.function', autospec=True)

# H216 - Wrong mock import (CRITICAL)
from mock import patch  # Third-party mock library
# Fix: from unittest import mock

# H304 - Relative imports
from .utils import helper  # Don't use relative imports
# Fix: from package.utils import helper

# H702 - String formatting in logging (CRITICAL)
LOG.info(f"Value: {val}")  # Immediate interpolation
LOG.info("Value: {}".format(val))  # Also wrong
# Fix: LOG.info("Value: %s", val)  # Delayed interpolation
```

### Code Quality Violations

```python
# H101 - TODO format
# TODO fix this  # Missing author name
# Fix: # TODO(yourname): Fix this issue

# H105 - Author tags (don't use)
# Author: Jane Doe  # Use version control instead
# Fix: Remove author tags entirely

# H106 - Vim configuration (don't use)
# vim: syntax=python:tabstop=4:shiftwidth=4
# Fix: Remove vim configuration entirely

# H212 - Type checking with assertEqual
assertEqual(type(obj), MyClass)  # Wrong approach
# Fix: assertIsInstance(obj, MyClass)

# H213 - Deprecated assertRaisesRegexp
self.assertRaisesRegexp(ValueError, "pattern", func)  # Deprecated
# Fix: self.assertRaises(ValueError, func)  # Or with context manager

# H232 - Mutable default arguments
def process_items(items=[]):  # Dangerous!
    items.append('new')
    return items
# Fix: def process_items(items=None):
#          items = items or []

# H501 - locals() usage
msg = "Error: %(error)s" % locals()  # Unclear what's being used
# Fix: msg = "Error: %s" % error  # Explicit

# H903 - UNIX line endings only
# Files with Windows line endings (\r\n) will fail
# Fix: Use UNIX line endings (\n) only
```

### Testing Violations

```python
# H202 - Testing for generic Exception
def test_operation(self):
    with self.assertRaises(Exception):  # Too broad
        risky_operation()
# Fix: with self.assertRaises(SpecificException):

# H203 - Use assertIsNone/assertIsNotNone
self.assertEqual(None, result)  # Less specific
# Fix: self.assertIsNone(result)

# H204 - Use assertEqual/assertNotEqual
self.assertTrue(a == b)  # Less specific
# Fix: self.assertEqual(a, b)

# H205 - Use assertGreater/assertLess
self.assertTrue(a > b)  # Less specific
# Fix: self.assertGreater(a, b)

# H211 - Use assertIsInstance
self.assertTrue(isinstance(obj, MyClass))  # Verbose
# Fix: self.assertIsInstance(obj, MyClass)

# H214 - Use assertIn/assertNotIn
self.assertTrue('key' in dictionary)  # Less specific
# Fix: self.assertIn('key', dictionary)
```

#### Common Commit Message Anti-Patterns to Avoid
```
# Too vague - doesn't explain what or why
Fix bug

# Missing component context
Update configuration

# Past tense instead of imperative
Fixed the memory leak issue

# Too long subject line (>50 chars)
Fix the memory leak that occurs in compute manager during instance deletion

# No explanation of AI usage
Add new feature
Generated-By: claude-code

# Missing why/context
Switch to new libvirt reset API
```

## 13. Comprehensive Checklists

### Legal Compliance Checklist (ALL REQUIRED)
- [ ] AI tool configured for open source compatibility
- [ ] Generated code reviewed for copyright issues
- [ ] No proprietary claims by AI vendor on output
- [ ] Code is compatible with Apache 2.0 license
- [ ] Proper "Generated-By:" or "Assisted-By:" label added to commit
- [ ] Context explanation included in commit message
- [ ] **DCO sign-off included** (`Signed-off-by: Your Name <email>`)
- [ ] **Real name and valid email** used in sign-off (no pseudonyms)
- [ ] Commit message follows OpenStack structure (50 char subject, 72 char body)
- [ ] Commit message explains WHY, WHAT, and HOW of the change
- [ ] AI usage and technical approach documented in commit message

### Error Prevention Checklist
Before generating code, verify:
- [ ] Line length ≤ 79 characters
- [ ] No bare `except:` statements
- [ ] `autospec=True` in all `@mock.patch` decorators
- [ ] Proper logging interpolation (use `%s`, not f-strings)
- [ ] Specific exception handling
- [ ] Apache license header present
- [ ] Imports properly organized
- [ ] "Generated-By:" or "Assisted-By:" label prepared for commit message
- [ ] AI tool configured for open source compatibility
- [ ] **DCO sign-off ready** (git commit -s)
- [ ] Commit subject line ≤ 50 characters, imperative mood
- [ ] Commit body explains WHY and WHAT, wrapped at 72 characters

## 14. Validation Workflows and Commands

### Pre-Commit Validation
After generating code, run these validation commands:

```bash
# Syntax check all Python files
python -m py_compile $(find . -name "*.py")

# Style checks
tox -e pep8
# OR
flake8 .

# License header verification
find . -name "*.py" -exec grep -L "Apache License" {} \;

# Line length verification
flake8 --select=E501 .

# Import order verification
flake8 --select=H301,H303,H304,H306 .

# Hacking rules verification
flake8 --select=H201,H210,H216,H501,H105,H106,H212 .

# DCO sign-off verification
git log -1 --pretty=%B | grep "Signed-off-by:"
```

### Git Hook Setup for Change-Id
Install Gerrit Change-Id hook:

```bash
# Install commit-msg hook
scp -p -P 29418 username@review.opendev.org:hooks/commit-msg .git/hooks/
chmod +x .git/hooks/commit-msg

# Verify Change-Id is present
git log -1 --pretty=%B | grep "Change-Id:"
```

### Full Validation Pipeline
```bash
# Complete validation before pushing
python -m py_compile $(find . -name "*.py") && \
tox -e pep8 && \
tox -e py3 && \
git log -1 --pretty=%B | grep "Signed-off-by:" && \
git log -1 --pretty=%B | grep "Change-Id:" && \
echo "✓ Ready to push!"
```

### CI Failure Troubleshooting

**Common pep8 failures:**
```bash
# Fix locally
tox -e pep8
# Address all issues
git commit --amend -s
git review
```

**Unit test failures:**
```bash
# Run specific failing test
tox -e py3 -- path/to/test_file.py:TestClass.test_method
# Fix failing tests
git commit --amend -s
git review
```

**Missing DCO sign-off:**
```bash
# Amend commit with sign-off
git commit --amend -s
git review
```

**Missing Change-Id:**
```bash
# Install hook and amend
scp -p -P 29418 username@review.opendev.org:hooks/commit-msg .git/hooks/
chmod +x .git/hooks/commit-msg
git commit --amend -s
git review
```

## 15. IDE Integration Notes

For AI assistants working with IDEs:
- Set line length markers at 79 characters
- Configure to show whitespace and line endings
- Enable PEP 8 checking plugins
- Set Python indent to 4 spaces, no tabs
- Configure AI tools for open source compatibility mode
- Enable code duplication detection features

---

**AI Assistant Note**: This guide prioritizes the most common OpenStack CI failures AND compliance with OpenInfra Foundation AI Policy. When in doubt, err on the side of being more explicit and verbose rather than concise, as OpenStack values clarity and maintainability over brevity. Always include proper AI attribution in commit messages.