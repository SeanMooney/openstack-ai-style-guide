# OpenStack Python Quick Rules for AI Code Generation

> **Quick Reference**: Essential rules for AI tools generating OpenStack-compliant Python code.  
> **For detailed explanations**: See the [OpenStack Python Comprehensive Style Guide for AI](comprehensive-version)

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
- **autospec=True** in all @mock.patch decorators
- **Delayed logging**: `LOG.info('Value: %s', val)` not f-strings

### 3. Required Patterns
```python
# Exception handling
try:
    operation()
except (ValueError, TypeError) as e:
    LOG.error('Failed: %s', e)

# Mock usage
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

### 4. Commit Message Format
```
Subject: imperative, <50 chars, no period

Body explaining WHY and WHAT. Wrap at 72 chars.
Include technical approach and AI tool context.

Generated-By: claude-code  # or Assisted-By: tool-name
Signed-off-by: Name <email>  # Required July 1, 2025
Closes-Bug: #123456
Change-Id: Ihash...
```

### 5. AI Policy Compliance
- **Generative AI**: Use `Generated-By: tool-name`
- **Predictive AI**: Use `Assisted-By: tool-name`
- **Document**: What AI generated + manual modifications
- **Review**: Confirm all AI code for correctness/security

## Forbidden Patterns
```python
# NEVER use these:
except:                    # H201 - specify exceptions
@mock.patch('mod.func')    # H210 - missing autospec=True
from mock import patch     # H216 - use unittest.mock
LOG.info(f'Val: {x}')     # H702 - use delayed interpolation
```

## Quick Checklist
- [ ] Apache license header
- [ ] 79 char line limit
- [ ] No bare except
- [ ] autospec=True in mocks
- [ ] Proper import order
- [ ] Delayed logging
- [ ] AI label in commit
- [ ] DCO sign-off (post July 1)
- [ ] 50 char commit subject

## Verification
```bash
tox -e pep8        # Style check
git commit -s      # Auto DCO sign-off
```