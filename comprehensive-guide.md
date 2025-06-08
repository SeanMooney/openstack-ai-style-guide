# OpenStack Python Comprehensive Style Guide for AI Code Generation

> **Comprehensive Guide**: Detailed explanations and examples for AI tools generating OpenStack-compliant Python code.  
> **For quick reference**: See the [OpenStack Python Quick Rules for AI](quick-version)

## Overview for AI Assistants
This guide provides specific instructions for AI coding assistants (Claude Code, aider, etc.) to generate Python code that meets OpenStack contribution standards. Follow these rules precisely to ensure code passes OpenStack's strict linting and review processes.

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

### Mock Usage (H210 - Critical)
```python
# Always use autospec=True
@mock.patch('nova.utils.execute', autospec=True)
def test_command_execution(self, mock_execute):
    mock_execute.return_value = ('output', '')
    # test code

# Wrong - will fail H210 check:
@mock.patch('nova.utils.execute')  # Missing autospec=True
```

### Assertion Patterns
```python
# Correct assertions (H203, H214 compliant):
self.assertIsNone(result)           # Not assertEqual(None, result)
self.assertIn('key', dictionary)    # Not assertTrue('key' in dictionary)
self.assertEqual(expected, actual)  # Order matters
self.assertIsInstance(obj, MyClass)
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

## 8. OpenStack-Specific Patterns

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

## 10. OpenInfra Foundation AI Policy Compliance

### Commit Message Requirements (MANDATORY)
All AI-generated contributions MUST include proper commit message labeling per OpenInfra Foundation AI Policy AND DCO sign-off (effective July 1, 2025):

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

#### DCO Sign-off Requirements (Effective July 1, 2025)
- **All new commits** must include `Signed-off-by: Your Name <your.email@example.com>`
- **Use your real name** (no pseudonyms or anonymous contributions)
- **Email must match** your Git configuration
- **Configure Git** to automatically add sign-off:
```bash
git config --global user.name "Your Real Name"
git config --global user.email "your.email@example.com"
git commit -s  # The -s flag adds Signed-off-by automatically
```

### AI Tool Configuration Requirements
Before generating OpenStack code, ensure:

1. **License Compatibility Mode**: Configure AI tools to respect open source licensing
2. **Code Scanning**: Enable features that flag output resembling publicly available code
3. **Duplicate Detection**: Use tools that block suggestions matching existing codebases
4. **Attribution Features**: Enable licensing information display when available

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

```python
# NEVER generate these patterns:

# H201 - Bare except
try:
    operation()
except:  # Will fail CI
    pass

# H210 - Missing autospec
@mock.patch('module.function')  # Add autospec=True

# H216 - Wrong mock import
from mock import patch  # Use: from unittest import mock

# H501 - locals() usage
"%(var)s" % locals()  # Use explicit formatting

# H304 - Relative imports
from .utils import helper  # Use: from package.utils import helper

# String formatting in logging
LOG.info(f"Value: {val}")  # Use: LOG.info("Value: %s", val)
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

### Legal Compliance Checklist
- [ ] AI tool configured for open source compatibility
- [ ] Generated code reviewed for copyright issues
- [ ] No proprietary claims by AI vendor on output
- [ ] Code is compatible with Apache 2.0 license
- [ ] Proper "Generated-By:" or "Assisted-By:" label added to commit
- [ ] Context explanation included in commit message
- [ ] DCO sign-off included (Signed-off-by line)
- [ ] Real name and valid email used in sign-off
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
- [ ] DCO sign-off ready (post July 1, 2025)
- [ ] Commit subject line ≤ 50 characters, imperative mood
- [ ] Commit body explains WHY and WHAT, wrapped at 72 characters

## 14. Verification Commands

After generating code, suggest these verification commands:

```bash
# Run style checks:
tox -e pep8

# Or with pre-commit (if available):
pre-commit run --all-files

# License check:
find . -name "*.py" -exec grep -L "Apache License" {} \;

# DCO sign-off:
git commit -s
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