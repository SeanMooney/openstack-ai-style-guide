# Pre-Submission Checklist for OpenStack AI-Generated Code

Complete checklist for validating AI-generated OpenStack code before committing and pushing to Gerrit.

## Part 1: Before Committing

### Code Quality

- [ ] **Apache 2.0 license header** present in all new Python files
- [ ] **Line length ≤ 79 characters** (no exceptions)
- [ ] **4 space indentation** (no tabs)
- [ ] **UNIX line endings** (\n, not \r\n)
- [ ] **No trailing whitespace**
- [ ] **File ends with newline**

### Python Standards

- [ ] **No bare `except:` statements** (H201)
- [ ] **All `@mock.patch` use `autospec=True`** (H210)
- [ ] **Import from `unittest.mock`**, not third-party `mock` (H216)
- [ ] **Delayed logging interpolation** (`LOG.info("Value: %s", val)`) (H702)
- [ ] **No relative imports** (H304)
- [ ] **Proper import organization** (stdlib → third-party → openstack → local)

### Docstrings and Documentation

- [ ] Module docstring at top of file
- [ ] Class docstrings with :param and :returns: (H404/H405)
- [ ] Function docstrings with :param and :returns:
- [ ] TODO comments include author name: `# TODO(username): ...` (H101)
- [ ] No author tags in code (use version control) (H105)

### Testing (If Applicable)

- [ ] Tests written for new functionality
- [ ] Tests use specific exceptions, not generic `Exception` (H202)
- [ ] Tests use `assertIsNone(x)` not `assertEqual(None, x)` (H203)
- [ ] Tests use `assertEqual(a, b)` not `assertTrue(a == b)` (H204)
- [ ] Tests use `assertIn(a, b)` not `assertTrue(a in b)` (H214)
- [ ] All mocks use `autospec=True` or `spec=` parameter (H210)

### Exception Handling

- [ ] Specific exception types caught (not bare `except:`)
- [ ] Exception messages are helpful and specific
- [ ] Logging includes exception context where appropriate
- [ ] No swallowed exceptions without logging

### OpenStack-Specific

- [ ] Context managers used for resources (files, database sessions)
- [ ] oslo.config used for configuration options
- [ ] oslo.log used for logging (not standard `logging`)
- [ ] No mutable default arguments (`items=None` not `items=[]`) (H232)

### AI Policy Compliance

- [ ] **AI attribution prepared** for commit message:
  - [ ] `Generated-By: tool-name` if substantial code was AI-generated
  - [ ] `Assisted-By: tool-name` if minor AI assistance (autocomplete)
- [ ] **Explanation ready** of what AI generated vs manual changes
- [ ] **You reviewed and understand** ALL AI-generated code
- [ ] **AI tool configured** for open source compatibility

### DCO and Commit Message

- [ ] **DCO sign-off ready** (will use `git commit -s`)
- [ ] **Real name and email** configured in git
- [ ] **Commit message drafted**:
  - [ ] Subject line ≤ 50 characters, imperative mood, no period
  - [ ] Body explains WHY (problem/motivation)
  - [ ] Body explains WHAT (changes made)
  - [ ] Body explains HOW (approach for complex changes)
  - [ ] Body wraps at 72 characters
  - [ ] AI usage documented in body
  - [ ] External references prepared (Closes-Bug, Implements, etc.)

### Validation Commands

Run these commands before committing:

```bash
# Syntax check
python -m py_compile your_file.py

# Style check
tox -e pep8
# OR
flake8 your_file.py

# License header check
grep -q "Apache License" your_file.py && echo "✓ License OK" || echo "✗ Missing license"

# Line length check
flake8 --select=E501 your_file.py

# Import order check
flake8 --select=I,H301,H303,H304,H306 your_file.py
```

### Commit Command

When ready to commit:

```bash
# Stage your changes
git add your_file.py

# Commit with DCO sign-off
git commit -s

# Your commit message template:
# ----------------------------------------
# Subject line: imperative, <50 chars
#
# Body paragraph explaining WHY and WHAT.
# Wrap at 72 characters. Include AI context.
#
# I used TOOL_NAME to generate DESCRIPTION.
# Manual modifications included CHANGES.
#
# Generated-By: tool-name
# Signed-off-by: Your Name <email>
# Closes-Bug: #XXXXXX
# Change-Id: Ixxxxx
# ----------------------------------------
```

## Part 2: Before Pushing to Gerrit

### Git History Review

- [ ] **All commits have DCO sign-off** (`Signed-off-by:`)
- [ ] **All commits have AI attribution** (if AI-assisted)
- [ ] **Commit messages follow format**:
  - [ ] Subject ≤ 50 characters, imperative mood
  - [ ] Body wraps at 72 characters
  - [ ] Explains WHY, WHAT, HOW
- [ ] **No "fixup" or "WIP" commits** in final history
- [ ] **Logical commit structure** (not too granular, not too large)

### Full Test Suite

Run all tests locally:

```bash
# Style checks
tox -e pep8

# Unit tests
tox -e py3

# Coverage
tox -e cover
# Check coverage report in cover/index.html

# Full validation pipeline
tox -e ALL
```

### Manual Code Review

- [ ] **All files have Apache license**
- [ ] **No debug code** or print statements
- [ ] **No commented-out code** (unless with explanation)
- [ ] **No TODOs** without author name
- [ ] **No hardcoded values** that should be configurable
- [ ] **No secrets** or credentials

### Documentation

- [ ] **Docstrings complete** for all new functions/classes
- [ ] **README updated** (if API or usage changed)
- [ ] **Release notes added** (if user-facing change)
- [ ] **API documentation updated** (if applicable)

### Dependencies

- [ ] **requirements.txt updated** (if new dependencies)
- [ ] **test-requirements.txt updated** (if new test dependencies)
- [ ] **All dependencies are approved** for OpenStack use
- [ ] **No GPL or incompatible licenses** in dependencies

### Change-Id Hook

- [ ] **Change-Id hook installed**:
```bash
# If not installed, install it:
scp -p -P 29418 username@review.opendev.org:hooks/commit-msg .git/hooks/
chmod +x .git/hooks/commit-msg
```

- [ ] **Change-Id present** in latest commit:
```bash
git log -1 --pretty=%B | grep "Change-Id:"
```

### External References

- [ ] **Bug reference included** (if fixing a bug):
  - `Closes-Bug: #XXXXXX` (fully fixes)
  - `Partial-Bug: #XXXXXX` (partial fix)
  - `Related-Bug: #XXXXXX` (related)

- [ ] **Blueprint reference included** (if implementing feature):
  - `Implements: blueprint name-of-blueprint`

- [ ] **Impact flags added** (if applicable):
  - `DocImpact` - Documentation changes needed
  - `APIImpact` - HTTP API modifications
  - `SecurityImpact` - Security implications
  - `UpgradeImpact` - Affects upgrade process

### Review Preparation

- [ ] **Self-review completed** (read your own diff carefully)
- [ ] **Reviewer list identified** (core team members familiar with this area)
- [ ] **Depends-On added** (if depends on another change)
- [ ] **Breaking changes documented** (if any)

### Final Pre-Push Validation

Quick validation before push:

```bash
# Full validation pipeline
python -m py_compile $(find . -name "*.py") && \
tox -e pep8 && \
tox -e py3 && \
git log -1 --pretty=%B | grep "Signed-off-by:" && \
git log -1 --pretty=%B | grep "Change-Id:" && \
echo "✓ Ready to push!"
```

### Push to Gerrit

```bash
# First-time push
git review

# Updating existing change (after amending)
git commit --amend -s
git review

# Push to specific branch
git review stable/wallaby  # For stable branch
git review master          # For master branch (default)
```

## Part 3: After Pushing

### Immediate Checks

- [ ] **Gerrit change created** successfully
- [ ] **Change-Id matches** commit message
- [ ] **Zuul CI triggered** (check status)
- [ ] **No immediate CI failures**

### Monitor CI

- [ ] **Check Zuul dashboard**: https://zuul.opendev.org
- [ ] **Watch for failures**:
  - pep8 check
  - unit tests
  - functional tests (if applicable)
  - documentation build

### Respond to CI Failures

If CI fails:

- [ ] **Review failure logs**
- [ ] **Fix issues locally**
- [ ] **Amend commit** (don't create new commit)
- [ ] **Re-push** with `git review`

## Common CI Failures and Fixes

### pep8 Failures

```bash
# Fix locally
tox -e pep8
# Address all issues
git commit --amend -s
git review
```

### Unit Test Failures

```bash
# Run locally
tox -e py3
# Fix failing tests
git commit --amend -s
git review
```

### Documentation Build Failures

```bash
# Test locally
tox -e docs
# Fix documentation
git commit --amend -s
git review
```

## Troubleshooting

### "Missing Change-Id" Error

```bash
# Install commit-msg hook
scp -p -P 29418 username@review.opendev.org:hooks/commit-msg .git/hooks/
chmod +x .git/hooks/commit-msg

# Amend commit to add Change-Id
git commit --amend -s
```

### "Missing DCO" Error

```bash
# Amend commit with sign-off
git commit --amend -s
git review
```

### Merge Conflict

```bash
# Rebase on latest master
git fetch origin
git rebase origin/master

# Resolve conflicts
# Edit conflicted files
git add resolved_files
git rebase --continue

# Re-push
git review
```

## Final Checklist

Before running `git review`:

- [ ] **All tests pass** locally
- [ ] **All commits signed off** (DCO)
- [ ] **AI attribution included** (if applicable)
- [ ] **Change-Id present**
- [ ] **Commit message complete**
- [ ] **No WIP or debug code**
- [ ] **Documentation updated**

---

**Remember**: DCO sign-off is REQUIRED. Always use `git commit -s`!

Monitor your submission at:
- Zuul CI: https://zuul.opendev.org
- Gerrit review: https://review.opendev.org
