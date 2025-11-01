# OpenStack Python Quick Rules for AI Code Generation

> **Quick Reference**: Essential rules for AI tools generating OpenStack-compliant Python code.

## Critical Rules (Follow ALL)

### 1. File Structure Template

```python
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License...
# [Full Apache 2.0 header - REQUIRED]

"""Module docstring."""

import json  # stdlib
import sys

import oslo_config  # third-party

from oslo_log import log  # from third-party

from nova import utils  # local project
```

### 2. Code Standards

- **79 chars max per line** (strict)
- **4 spaces indentation** (no tabs)
- **No bare except:** - always specify exceptions
- **autospec=True** in all @mock.patch decorators (recommended practice)
- **Delayed logging**: `LOG.info('Value: %s', val)` not f-strings

### 3. Required Patterns

```python
# Exception handling
try:
    operation()
except (ValueError, TypeError) as e:
    LOG.error('Failed: %s', e)

# Exception class pattern
class ModuleError(Exception):
    """Base exception for MODULE_NAME errors."""
    msg_fmt = "Error in MODULE_NAME: %(reason)s"

class ResourceNotFoundError(ModuleError):
    """Raised when resource not found."""
    msg_fmt = "Resource %(resource_id)s not found"

# Configuration pattern
from oslo_config import cfg

MODULE_OPTS = [
    cfg.StrOpt('param_name',
               default='default_value',
               help='Description of parameter'),
]

def register_opts(conf):
    conf.register_opts(MODULE_OPTS, group='module_name')

# Database transaction pattern
from oslo_db import exception as db_exc

def create_resource(context, resource_data):
    """Create resource with proper transaction handling."""
    try:
        with context.session.begin():
            resource = ResourceModel(**resource_data)
            context.session.add(resource)
            return resource
    except db_exc.DBDuplicateEntry:
        raise ResourceAlreadyExists(resource_data['id'])

# API service method pattern
def api_method(self, request, resource_id):
    """Standard API method with proper error handling."""
    context = request.environ['context']

    try:
        resource = self.manager.get_resource(context, resource_id)
        return {'resource': resource}
    except ResourceNotFoundError as e:
        raise webob.exc.HTTPNotFound(explanation=e.msg_fmt % e.kwargs)
    except Exception as e:
        LOG.exception('Unexpected error in api_method')
        raise webob.exc.HTTPInternalServerError()

# Mock usage (recommended)
@mock.patch('nova.utils.execute', autospec=True)
def test_method(self, mock_execute):

# Function defaults
def process_items(items=None):
    items = items or []

# Context managers
with open('/path/file') as f:
    data = f.read()

# Docstrings
def method(param):
    """Brief description.

    :param param: Description
    :returns: Description
    """
```

### 4. Commit Message Format (ALL REQUIRED)

```text
Subject: imperative, <50 chars, no period

Body explaining WHY and WHAT. Wrap at 72 chars.
Include technical approach and AI tool context.

Generated-By: claude-code  # or Assisted-By: tool-name
Signed-off-by: Name <email>  # REQUIRED for all commits
Closes-Bug: #123456
Change-Id: Ihash...
```

### 5. AI Policy Compliance

- **Generative AI** (substantial code): Use `Generated-By: tool-name`
- **Predictive AI** (suggestions/autocomplete): Use `Assisted-By: tool-name`
- **Human in loop**: Always review and understand AI-generated code
- **Treat as untrusted**: Apply same scrutiny as unknown contributor code
- **Document context**: What AI generated + manual modifications
- **DCO sign-off**: git commit -s (certifies you reviewed all content)

## Forbidden Patterns

```python
# NEVER use these:
except:                    # H201 - specify exceptions
@mock.patch('mod.func')    # H210 - missing autospec=True
from mock import patch     # H216 - use unittest.mock
LOG.info(f'Val: {x}')     # H702 - use delayed interpolation
locals() in formatting    # H501 - use explicit variables
# Author: Name            # H105 - use version control
# vim: syntax=python     # H106 - no vim configs
assertEqual(type(obj), Class)  # H212 - use assertIsInstance

# Additional anti-patterns:
try:
    operation()
except Exception:         # Too broad - catch specific exceptions
    pass

def func(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9):
    """Too many parameters - use config objects or **kwargs"""
    pass

# Missing error handling in API methods
def api_method_no_error_handling(self, request):
    result = some_operation()  # No try/catch
    return result
```

## Quick Checklist (ALL REQUIRED)

- [ ] Apache license header
- [ ] 79 char line limit
- [ ] No bare except
- [ ] autospec=True in mocks (recommended)
- [ ] Proper import order
- [ ] Delayed logging
- [ ] No locals() in formatting
- [ ] No author tags or vim configs
- [ ] assertIsInstance for type checks
- [ ] AI label in commit (Generated-By/Assisted-By)
- [ ] **DCO sign-off** (git commit -s)
- [ ] 50 char commit subject
- [ ] Specific exception handling (no broad Exception)
- [ ] Configuration options registered
- [ ] Database transactions properly handled
- [ ] API methods have error handling
- [ ] Function parameters <= 6 (use objects for more)

## Verification

```bash
tox -e pep8                    # Style check
git commit -s                    # Auto DCO sign-off
grep -q "Apache License" file.py  # License check
flake8 --select=E501 file.py      # Line length check
flake8 --select=H501,H105,H106,H212 file.py  # Hacking rules
```
