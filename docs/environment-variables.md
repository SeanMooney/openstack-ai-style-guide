# Environment Variables Reference

This document describes the environment variables used in the OpenStack AI Style Guide
project, particularly in Zuul CI/CD jobs and local development.

## Zuul Job Variables

These variables are set and used in Zuul CI jobs defined in `zuul.d/jobs.yaml`.

### Linting Job Variables

#### `tox_envlist`

- **Job**: openstack-ai-style-guide-lint
- **Type**: String
- **Current Value**: `linters`
- **Purpose**: Specifies which tox environment(s) to execute
- **What it runs**: The `linters` environment in `tox.ini`, which executes:
  - `pre-commit run --all-files --show-diff-on-failure`
- **Usage**: Internal variable for tox, not typically overridden
- **Related Config**: See `tox.ini` for environment definitions

#### `python_version`

- **Job**: openstack-ai-style-guide-lint
- **Type**: String
- **Current Value**: `3.13`
- **Purpose**: Specifies Python version for tox environment
- **Nodeset Constraint**: Must match Python version available on the nodeset
- **Current Nodeset**: debian-opencode-single-node-pod (has Python 3.13)
- **Override**: Only change if using a different nodeset with different Python
- **Related Docs**: See `docs/zuul-configuration.md` for customization guide

### Code Review Job Variables

These variables are used by `teim-code-review-base` in `zuul.d/jobs.yaml`.
The Ansible roles default to Anthropic tier names (`haiku`, `sonnet`,
`opus`), and the Zuul job overrides them with the concrete LiteLLM model
aliases used in CI.

#### `haiku_model`

- **Job**: `teim-code-review-base`
- **Type**: String (LiteLLM model identifier)
- **Current Value**: `glm-4.7-flash`
- **Purpose**: Maps Claude's Haiku tier to the fast CI model
- **Override**: Can be overridden in child jobs or via Zuul variables

#### `sonnet_model`

- **Job**: `teim-code-review-base`
- **Type**: String (LiteLLM model identifier)
- **Current Value**: `glm-4.7`
- **Purpose**: Maps Claude's Sonnet tier to the balanced CI model
- **Override**: Can be overridden in child jobs or via Zuul variables

#### `opus_model`

- **Job**: `teim-code-review-base`
- **Type**: String (LiteLLM model identifier)
- **Current Value**: `glm-5.1`
- **Purpose**: Sets `ANTHROPIC_DEFAULT_OPUS_MODEL` for plugin-installed
  agents that inherit the Opus tier
- **Override**: Change this in Zuul when moving the default high-capability
  model to a new backend alias

#### `review_model`

- **Job**: `teim-code-review-base`
- **Type**: String (LiteLLM model identifier)
- **Current Value**: `glm-5.1`
- **Purpose**: Model used for the direct `teim-review-agent` invocation in
  the `ai_code_review` role
- **Override**: Change this in Zuul when moving the reviewer to a new backend
  alias

#### `anthropic_api_url`

- **Job**: `teim-code-review-base`
- **Type**: String (URL)
- **Current Value**: `http://litellm.zuul-system.svc.cluster.local:4000`
- **Purpose**: Anthropic-compatible LiteLLM endpoint used by Claude CLI
- **Scope**: Internal Zuul cluster service, not accessible externally

#### `anthropic_auth_token`

- **Job**: `teim-code-review-base`
- **Type**: String (API Key)
- **Current Value**: `sk-1234`
- **Purpose**: Authentication token for the internal LiteLLM proxy
- **Security**: Internal homelab token only; production should use Zuul
  secrets

### Output and Collection Variables

#### `review_output_dir`

- **Job**: `teim-code-review-base`
- **Type**: String (directory path)
- **Current Value**: `{{ ansible_user_dir }}/logs/code-review`
- **Purpose**: Directory where code review output files are written
- **Contents**: Review reports and analysis results
- **Access**: Output is collected in Zuul artifacts

#### `extensions_to_txt`

- **Job**: `teim-code-review-base`
- **Type**: Dictionary/Map
- **Current Value**: `{conf: true, log: true, localrc: true, stackenv: true, auto: true}`
- **Purpose**: Specifies which file extensions to convert to `.txt` in artifacts
- **Use Case**: Ensures certain log formats are readable in web interface
- **Extensions Collected**:
  - `conf`: Configuration files
  - `log`: Log files
  - `localrc`: Local resource files
  - `stackenv`: Stack environment files
  - `auto`: Auto-generated files

### Project Path Variables

#### `style_guide_project`

- **Job**: `teim-code-review-base`
- **Type**: String (directory path)
- **Value**: Zuul project source directory
- **Computed As**: `{{ zuul.projects['github.com/SeanMooney/openstack-ai-style-guide'].src_dir }}`
- **Purpose**: Locates the style guide project in Zuul workspace
- **Usage**: Used to locate agents and configuration files

#### `style_guide_quick_rules`

- **Job**: `teim-code-review-base`
- **Type**: String (file path)
- **Current Value**: `{{ style_guide_project }}/docs/quick-rules.md`
- **Purpose**: Quick reference passed into the review workflow

#### `style_guide_comprehensive`

- **Job**: `teim-code-review-base`
- **Type**: String (file path)
- **Current Value**: `{{ style_guide_project }}/docs/comprehensive-guide.md`
- **Purpose**: Detailed style guide passed into the review workflow

## Pre-commit Hook Environment Variables

These variables can be set in your shell to customize pre-commit behavior locally.

### Common Pre-commit Variables

#### `PRE_COMMIT_FROM_REF` and `PRE_COMMIT_TO_REF`

- **Purpose**: Limit hooks to changed files between two git refs
- **Usage**: `PRE_COMMIT_FROM_REF=origin/master PRE_COMMIT_TO_REF=HEAD pre-commit run`
- **Use Case**: Running hooks only on your changes

#### `SKIP`

- **Purpose**: Skip specific hooks
- **Usage**: `SKIP=ruff,bandit pre-commit run --all-files`
- **Note**: Not recommended for CI, useful for local development only
- **Available Hooks**: See `.pre-commit-config.yaml` for hook IDs

### Hook-Specific Variables

#### Bandit Security Scanner

- **Config File**: `pyproject.toml` (bandit configuration)
- **Hook**: Lines 49-65 in `.pre-commit-config.yaml`
- **Environment**: Uses system Python

#### Ruff Linter/Formatter

- **Config File**: `ruff.toml`
- **Hook**: Lines 38-39 in `.pre-commit-config.yaml`
- **Args**: `[--fix]` (auto-fix enabled)
- **Environment Variables**: None typically needed

#### Markdownlint

- **Config File**: `.markdownlint.yaml`
- **Hook**: Lines 44-47 in `.pre-commit-config.yaml`
- **Args**: `[--fix]` (auto-fix enabled)

## Local Development Variables

When working locally, you may need to set these variables:

### Git Configuration

These aren't environment variables but important for development:

```bash
# Set your git email (must match Signed-off-by line)
git config user.email "your@email.com"

# Verify configuration
git config user.email
```

### Python Environment (Optional)

For development, you may want to set:

```bash
# If using virtual environment
export PYTHONPATH=/path/to/repo

# For debugging
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUTF8=1
```

## Zuul-Specific Variables

These variables are provided by Zuul itself and used in job definitions:

### Zuul Build Context

#### `{{ zuul.projects['<project-name>'].src_dir }}`

- **Purpose**: Provides path to checked-out project source
- **Example**: `{{ zuul.projects['github.com/SeanMooney/openstack-ai-style-guide'].src_dir }}`
- **Usage**: Locating project files within Zuul playbooks

#### `{{ ansible_user_dir }}`

- **Purpose**: Home directory of the Zuul execution user
- **Typical Value**: `/home/zuul`
- **Usage**: Base path for relative directory paths

## Customization Guide

### How to Override Variables in Zuul

**In Job Definition** (`zuul.d/jobs.yaml`):

```yaml
- job:
    name: custom-job
    parent: teim-code-review
    vars:
      review_model: "glm-4.7"
      timeout: 1800
```

**Via Zuul Configuration** (project configuration file):

```yaml
- job:
    name: my-project-review
    parent: teim-code-review
    vars:
      review_model: "your-custom-model"
```

## Related Documentation

- **Zuul Configuration**: See `docs/zuul-configuration.md` for job-specific details
- **Pre-commit Setup**: See `CONTRIBUTING.md` for local pre-commit configuration
- **Claude Code Plugin**: See `README.md` for plugin installation and review workflow setup
- **Build and Testing**: See `tox.ini` for testing environment configuration
