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

#### `context_model`

- **Job**: openstack-ai-code-review-base
- **Type**: String (LiteLLM model identifier)
- **Current Value**: `litellm-homelab/glm-4.5-air`
- **Purpose**: Specifies which model to use for context extraction
- **Use Case**: Fast analysis of code changes for context
- **Override**: Can be overridden in child jobs or via Zuul variables
- **Example Override**:

  ```yaml
  - job:
      name: my-custom-review
      parent: openstack-ai-code-review
      vars:
        context_model: "litellm-homelab/glm-4.5-turbo"
  ```

#### `review_model`

- **Job**: openstack-ai-code-review-base
- **Type**: String (LiteLLM model identifier)
- **Current Value**: `litellm-homelab/glm-4.6`
- **Purpose**: Specifies which model to use for generating code review feedback
- **Use Case**: Comprehensive code analysis and review generation
- **Override**: Can be overridden in child jobs or via Zuul variables
- **Performance Note**: More capable models may take longer but provide better reviews

#### `litellm_base_url`

- **Job**: openstack-ai-code-review-base
- **Type**: String (URL)
- **Current Value**: `http://litellm.zuul-system.svc.cluster.local:4000/v1`
- **Purpose**: Endpoint for the LiteLLM proxy that routes model requests
- **Scope**: Internal Zuul cluster service, not accessible externally
- **Routing**: Handles load balancing and model routing
- **Note**: Do not modify without infrastructure team coordination

#### `litellm_api_key`

- **Job**: openstack-ai-code-review-base
- **Type**: String (API Key)
- **Current Value**: `sk-1234`
- **Purpose**: Authentication key for LiteLLM proxy access
- **Security**: Not sensitive (internal homelab key, isolated environment)
- **Usage**: Automatically passed to OpenCode by Zuul
- **Note**: Do not modify without infrastructure team coordination

#### `opencode_binary`

- **Job**: openstack-ai-code-review-base
- **Type**: String (binary path)
- **Current Value**: `opencode`
- **Purpose**: Path to OpenCode binary (pre-installed on nodeset)
- **Pre-installation**: Included in debian-opencode-single-node-pod nodeset
- **Usage**: Internal variable for Zuul playbooks

#### `opencode_config_dir`

- **Job**: openstack-ai-code-review-base
- **Type**: String (directory path)
- **Current Value**: `{{ ansible_user_dir }}/.config/opencode`
- **Purpose**: Directory where OpenCode stores configuration and agents
- **Usage**: Zuul playbooks copy agent definitions here
- **Related**: `agents_source_dir`, `agents_target_dir`

### Output and Collection Variables

#### `review_output_dir`

- **Job**: openstack-ai-code-review-base
- **Type**: String (directory path)
- **Current Value**: `{{ ansible_user_dir }}/logs/code-review`
- **Purpose**: Directory where code review output files are written
- **Contents**: Review reports and analysis results
- **Access**: Output is collected in Zuul artifacts

#### `extensions_to_txt`

- **Job**: openstack-ai-code-review-base
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

- **Job**: openstack-ai-code-review-base
- **Type**: String (directory path)
- **Value**: Zuul project source directory
- **Computed As**: `{{ zuul.projects['github.com/SeanMooney/openstack-ai-style-guide'].src_dir }}`
- **Purpose**: Locates the style guide project in Zuul workspace
- **Usage**: Used to locate agents and configuration files

#### `agents_source_dir`

- **Job**: openstack-ai-code-review-base
- **Type**: String (directory path)
- **Computed As**: `{{ ansible_user_dir }}/{{ style_guide_project }}/agents`
- **Purpose**: Source location of agent configuration files
- **Contents**: OpenCode agent definitions (JSON files)

#### `agents_target_dir`

- **Job**: openstack-ai-code-review-base
- **Type**: String (directory path)
- **Computed As**: `{{ opencode_config_dir }}/agent`
- **Purpose**: Destination where agent configurations are copied
- **Usage**: OpenCode reads agents from this location

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
    parent: openstack-ai-code-review
    vars:
      review_model: "litellm-homelab/glm-4.7"
      timeout: 1800
```

**Via Zuul Configuration** (project configuration file):

```yaml
- job:
    name: my-project-review
    parent: openstack-ai-code-review
    vars:
      review_model: "your-custom-model"
```

## Related Documentation

- **Zuul Configuration**: See `docs/zuul-configuration.md` for job-specific details
- **Pre-commit Setup**: See `CONTRIBUTING.md` for local pre-commit configuration
- **Code Review**: See `tools/README.md` for OpenCode configuration
- **Build and Testing**: See `tox.ini` for testing environment configuration
