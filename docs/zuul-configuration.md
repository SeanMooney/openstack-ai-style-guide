# Zuul CI Configuration Guide

This document explains the Zuul CI/CD configuration for the OpenStack AI Style Guide repository and how to customize it.

## Overview

The repository uses Zuul for automated code review and linting. Two main
jobs are configured:

1. **teim-code-review** - AI-assisted code review using Claude Code via LiteLLM
2. **openstack-ai-style-guide-lint** - Linting checks using pre-commit via tox

## Linting Job Configuration

### Job Definition

**Location:** `zuul.d/jobs.yaml`

```yaml
- job:
    name: openstack-ai-style-guide-lint
    parent: tox-linters
    timeout: 900
    nodeset: debian-claude-code-single-node-pod
    vars:
      tox_envlist: linters
      python_version: "3.13"
```

### Configuration Parameters

#### `timeout: 900`

- **Duration**: 15 minutes
- **Purpose**: Maximum time allowed for linting to complete
- **Override**: Modify in `zuul.d/jobs.yaml` only after measuring sustained
  increased runtime

#### `nodeset: debian-claude-code-single-node-pod`

- **Purpose**: Specifies the CI node used for the tox lint job
- **Pre-installed**: Python 3.13 and development utilities
- **Constraint**: The lint job pins `python_version` to match the node image

#### `tox_envlist: linters`

- **Purpose**: Selects the tox environment to run
- **What it does**: Executes `pre-commit run --all-files --show-diff-on-failure`
- **Configuration**: See `tox.ini` and `.pre-commit-config.yaml` for hook
  details

### What the Linting Job Checks

The linting job runs the configured pre-commit hooks, including:

1. **Code Quality** - ruff checks and formatting policy
2. **Security** - bandit checks for common Python security issues
3. **License Headers** - Apache 2.0 header checks for Python files
4. **DCO Sign-off** - commit sign-off validation
5. **Documentation** - markdownlint checks
6. **File Quality** - whitespace, line endings, YAML/JSON syntax, merge
   conflict markers, and private key detection

## Code Review Job Configuration

### Job Definition

**Location:** `zuul.d/jobs.yaml`

```yaml
- job:
    name: teim-code-review-base
    abstract: true
    nodeset: debian-claude-code-single-node-pod
    vars:
      haiku_model: "glm-4.7"
      sonnet_model: "glm-5-turbo"
      opus_model: "glm-5.2"
      review_model: "opus"
      anthropic_api_url: "http://litellm.zuul-system.svc.cluster.local:4000"
```

### Configuration Parameters

#### Model Selection

- **`haiku_model`**: Remaps the Claude Haiku tier in CI
  - Default: `glm-4.7`
  - Purpose: Fast extraction and lightweight agent work
  - Override: Set in child jobs or via job variables

- **`sonnet_model`**: Remaps the Claude Sonnet tier in CI
  - Default: `glm-5-turbo`
  - Purpose: Reserved for future balanced general-purpose agent work
  - Override: Set in child jobs or via job variables

- **`opus_model`**: Remaps the Claude Opus tier in CI
  - Default: `glm-5.2`
  - Purpose: Controls inherited `model: opus` behavior through
    `ANTHROPIC_DEFAULT_OPUS_MODEL`
  - Override: Update this in the Zuul job when changing the backend model

- **`review_model`**: Model used for the top-level `teim-review-agent` run
  - Default: `opus`
  - Purpose: Launches the orchestrator and detailed reviewer on the Opus tier,
    which maps to `glm-5.2` in CI
  - Override: Update this in the Zuul job when changing the reviewer tier

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

### Creating a Child Lint Job

```yaml
- job:
    name: custom-lint-job
    parent: openstack-ai-style-guide-lint
    nodeset: your-custom-nodeset
    vars:
      python_version: "3.12"
```

**Note**: Requires that `your-custom-nodeset` has Python 3.12 installed.

### Creating a Child Review Job

```yaml
- job:
    name: custom-review-job
    parent: teim-code-review
    vars:
      review_model: "opus"
```

### Overriding Model Selection

You can override models in child jobs or via job variables:

```yaml
- job:
    name: custom-review-job
    parent: teim-code-review
    vars:
      review_model: "opus"
```

### Adding Additional Pre-commit Hooks

1. Edit `.pre-commit-config.yaml`
2. Add your hook configuration
3. Test locally: `pre-commit run --all-files`
4. Commit changes with proper DCO sign-off

## Job Inheritance

The repository uses Zuul job inheritance:

- **openstack-ai-style-guide-lint** inherits from `tox-linters`
  - Parent job provides tox integration
  - The child selects the `linters` tox environment
  - Can be inherited for alternate nodesets or Python versions

- **teim-code-review** inherits from `teim-code-review-base`
  - Base provides common configuration
  - Child job runs the teim-review workflow with Claude Code
  - Can be inherited further for specific project types

## Troubleshooting

### Lint Job Timeout Issues

If the linting job frequently times out:

1. Check recent performance trends in Zuul logs
2. Profile the slowest hooks locally: `pre-commit run -a --show-diff-on-failure`
3. Consider optimizing slow hooks or increasing timeout based on measured data

### Job Timeout Issues

If the review job frequently times out:

1. Check recent performance trends in Zuul logs
2. Review LiteLLM proxy and upstream model latency
3. Consider reducing review scope or increasing timeout
4. Only increase timeout after confirming measured execution time

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
