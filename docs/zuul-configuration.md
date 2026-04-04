# Zuul CI Configuration Guide

This document explains the Zuul CI/CD configuration for the OpenStack AI Style Guide repository and how to customize it.

## Overview

The repository uses Zuul for continuous integration and automated code review.
Two main jobs are configured:

1. **openstack-ai-style-guide-lint** - Linting checks using pre-commit hooks
2. **teim-code-review** - AI-assisted code review using Claude Code via LiteLLM

## Linting Job Configuration

### Job Definition

**Location:** `zuul.d/jobs.yaml`

```yaml
- job:
    name: openstack-ai-style-guide-lint
    parent: tox-linters
    timeout: 900
    nodeset: debian-opencode-single-node-pod
    vars:
      tox_envlist: linters
      python_version: "3.13"
```

### Configuration Parameters

#### `timeout: 900`

- **Duration**: 15 minutes
- **Purpose**: Maximum time allowed for linting to complete
- **Notes**: Set to approximately double the average runtime
- **Override**: Modify in `zuul.d/jobs.yaml` only if you've measured sustained increased execution time

#### `nodeset: debian-opencode-single-node-pod`

- **Purpose**: Specifies the type of CI node to use
- **Pre-installed**: Python 3.13, OpenCode tools, development utilities
- **Constraints**: Limited to Python 3.13 due to node pre-configuration
- **Alternative**: Contact infrastructure team to add different nodesets if needed

#### `python_version: "3.13"`

- **Requirement**: Hard-coded for debian-opencode nodeset compatibility
- **Rationale**: The debian-opencode nodes are pre-built with Python 3.13 and OpenCode
- **Flexibility Options**:
  - Use a different nodeset (requires infrastructure changes)
  - Create a child job with different version and nodeset
  - Contact the OpenStack infrastructure team to request a new nodeset

#### `tox_envlist: linters`

- **Purpose**: Specifies which tox environment to run
- **What it does**: Executes `pre-commit run --all-files --show-diff-on-failure`
- **Configuration**: See `tox.ini` and `.pre-commit-config.yaml` for hook details

### What the Linting Job Checks

The linting job runs the following checks via pre-commit hooks:

1. **Code Quality** (ruff)
   - PEP 8 compliance
   - Line length (79 characters max)
   - Import organization
   - Python best practices
   - Auto-fixes formatting issues

2. **Security** (bandit)
   - Common security vulnerabilities
   - Dangerous code patterns
   - Configuration issues

3. **License Headers**
   - Apache 2.0 license in all Python files
   - Proper header format

4. **DCO Sign-off**
   - Signed-off-by line in commit message
   - Email consistency between git config and sign-off
   - Ensures compliance with OpenInfra Foundation policy

5. **Documentation** (markdownlint)
   - Markdown formatting
   - Link validity
   - Code block formatting

6. **File Quality**
   - Trailing whitespace
   - Line endings (UNIX LF)
   - JSON/YAML syntax
   - Merge conflicts
   - Private keys detection

## Code Review Job Configuration

### Job Definition

**Location:** `zuul.d/jobs.yaml`

```yaml
- job:
    name: teim-code-review-base
    abstract: true
    nodeset: debian-claude-code-single-node-pod
    vars:
      haiku_model: "glm-4.7-flash"
      sonnet_model: "glm-4.7"
      opus_model: "glm-5.1"
      review_model: "glm-5.1"
      anthropic_api_url: "http://litellm.zuul-system.svc.cluster.local:4000"
```

### Configuration Parameters

#### Model Selection

- **`haiku_model`**: Remaps the Claude Haiku tier in CI
  - Default: `glm-4.7-flash`
  - Purpose: Fast extraction and lightweight agent work
  - Override: Set in child jobs or via job variables

- **`sonnet_model`**: Remaps the Claude Sonnet tier in CI
  - Default: `glm-4.7`
  - Purpose: Balanced general-purpose agent work
  - Override: Set in child jobs or via job variables

- **`opus_model`**: Remaps the Claude Opus tier in CI
  - Default: `glm-5.1`
  - Purpose: Controls inherited `model: opus` behavior through
    `ANTHROPIC_DEFAULT_OPUS_MODEL`
  - Override: Update this in the Zuul job when changing the backend model

- **`review_model`**: Model used for the top-level `teim-review-agent` run
  - Default: `glm-5.1`
  - Purpose: Comprehensive code analysis and review generation
  - Override: Update this in the Zuul job when changing the reviewer backend

#### LiteLLM Configuration

- **`anthropic_api_url`**: Proxy endpoint for model access
  - Default: `http://litellm.zuul-system.svc.cluster.local:4000`
  - Purpose: Routes Claude CLI requests through the LiteLLM proxy
  - Note: Internal homelab service, not accessible outside cluster

- **`anthropic_auth_token`**: Authentication for LiteLLM proxy
  - Default: `sk-1234` (internal key, not sensitive)
  - Note: Used only within isolated Zuul environment

#### Timeout Configuration

- **`timeout: 1800`** (30 minutes)
- Purpose: Allows sufficient time for context extraction and review generation
- Consideration: Should be roughly 2x the average execution time

## Customizing Jobs

### Creating a Child Job with Different Python Version

```yaml
- job:
    name: custom-lint-job
    parent: openstack-ai-style-guide-lint
    nodeset: your-custom-nodeset
    vars:
      python_version: "3.12"
```

**Note**: Requires that `your-custom-nodeset` has Python 3.12 installed.

### Overriding Model Selection

You can override models in child jobs or via job variables:

```yaml
- job:
    name: custom-review-job
    parent: teim-code-review
    vars:
      review_model: "glm-5.1"
```

### Adding Additional Pre-commit Hooks

1. Edit `.pre-commit-config.yaml`
2. Add your hook configuration
3. Test locally: `pre-commit run --all-files`
4. Commit changes with proper DCO sign-off

## Job Inheritance

The repository uses Zuul job inheritance:

- **openstack-ai-style-guide-lint** inherits from `tox-linters`
  - Provides tox integration
  - Handles environment setup
  - Executes tox environments

- **teim-code-review** inherits from `teim-code-review-base`
  - Base provides common configuration
  - Child job runs the teim-review workflow with Claude Code
  - Can be inherited further for specific project types

## Troubleshooting

### Job Timeout Issues

If the linting job frequently times out:

1. Check recent performance trends in Zuul logs
2. Profile the slowest hooks locally: `pre-commit run -a --show-diff-on-failure`
3. Consider disabling slow hooks or optimizing the code
4. Only increase timeout after confirming the measured execution time

### Python Version Compatibility

If you need a different Python version:

1. **Check available nodesets**: Contact your Zuul administrator
2. **Request new nodeset**: File an infrastructure request if needed
3. **Workaround**: Create a child job with different nodeset specification

### DCO Sign-off Failures

If the DCO hook fails:

1. Verify email in git config: `git config user.email`
2. Check commit sign-off matches: `git log -1 --pretty=%B | grep Signed-off-by`
3. Amend if mismatch: `git commit --amend -s`
4. Ensure config matches: `git config user.email "your@email.com"`

## Related Documentation

- **Pre-commit Hooks**: See `CONTRIBUTING.md` for detailed pre-commit instructions
- **Environment Variables**: See `docs/environment-variables.md` for Zuul job variables
- **Claude Code Plugin**: See `README.md` for plugin installation and review workflow setup
- **Linting Rules**: See `docs/quick-rules.md` and `docs/comprehensive-guide.md`
