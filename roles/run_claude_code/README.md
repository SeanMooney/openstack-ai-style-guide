# run-claude-code

Execute Claude Code CLI commands in headless mode with automatic retry logic and
comprehensive error handling.

## Description

This role provides a reusable interface for running Claude Code CLI commands in CI/CD
environments. It includes:

- Environment variable validation
- Command execution with retry logic (3 attempts)
- Intelligent error detection and categorization
- Detailed troubleshooting guidance
- Output file verification

## Requirements

- Claude Code CLI installed and accessible via `claude` command (or custom path)
- Anthropic-compatible API endpoint (e.g., LiteLLM proxy)
- API authentication token

## Role Variables

### Required Variables

These variables must be provided by the caller:

```yaml
model_name: "glm-4.6"                    # Claude model to use
prompt_text: "Analyze this code..."      # Prompt string (may include @file references)
output_file: "/path/to/output.json"     # Expected output file path
command_name: "code analysis"            # Human-readable operation name for logging
anthropic_auth_token: "sk-..."           # API authentication token
anthropic_api_url: "http://api.example"  # API base URL
```

### Optional Variables

```yaml
working_dir: "/path/to/workdir"          # Working directory (default: ansible_user_dir)
claude_binary: "claude"                  # Path to Claude CLI (default: "claude")
```

## Dependencies

None.

## Example Usage

### Basic Usage

```yaml
- name: Run code review with Claude
  include_role:
    name: run-claude-code
  vars:
    model_name: "{{ review_model }}"
    prompt_text: "Review the code in @{{ project_dir }}"
    output_file: "{{ output_dir }}/review.json"
    command_name: "code review"
    anthropic_auth_token: "{{ api_token }}"
    anthropic_api_url: "{{ api_url }}"
```

### With Working Directory

```yaml
- name: Extract project context
  include_role:
    name: run-claude-code
  vars:
    model_name: "{{ context_model }}"
    prompt_text: "Extract context from @inventory.yaml"
    output_file: "{{ output_dir }}/context.md"
    command_name: "context extraction"
    working_dir: "{{ project_src_dir }}"
    anthropic_auth_token: "{{ api_token }}"
    anthropic_api_url: "{{ api_url }}"
```

### In Role Dependencies

```yaml
# roles/my-ai-role/meta/main.yaml
dependencies:
  - role: run-claude-code
```

## Error Handling

The role automatically detects and categorizes errors:

- **Authentication errors**: Invalid or expired API tokens
- **Model not found**: Requested model unavailable
- **Transient errors**: Rate limits or service overload (triggers retry)
- **Connectivity errors**: Network issues reaching API endpoint
- **Unknown errors**: Other failures with full diagnostic output

Each error type provides specific troubleshooting guidance.

## Tool Permissions

The Claude CLI is invoked with broad tool permissions appropriate for trusted CI environments:

- **Bash**: Git operations and CI commands
- **Read/Grep/Glob**: Code analysis and file discovery
- **Write**: Report generation
- **Edit**: Automated fix suggestions

For untrusted contexts, modify `tasks/main.yaml` to restrict to read-only tools.

## License

Apache-2.0

## Author

Sean Mooney
