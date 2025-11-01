# OpenStack AI Code Review Job - Troubleshooting Guide

This guide helps diagnose and resolve common issues when running the OpenStack AI code review job.

## Quick Reference

**Job Components:**

- Job: `openstack-ai-code-review`
- Base Job: `openstack-ai-code-review-base`
- Playbooks: `playbooks/code-review/run.yaml` (main), `extract-context.yaml`, `analyze-commit.yaml`, `perform-review.yaml`
- Agents: `zuul-context-extractor`, `commit-summary`, `code-review-agent`

**Log Locations:**

- Review outputs: `logs/code-review/` (zuul-context.md, commit-summary.md, review-report.md)
- OpenCode logs: `logs/.local/share/opencode/log/`
- Job execution: Standard Zuul console output

---

## Common Error Scenarios

### 1. OpenCode Command Failures

#### Symptom

```text
OpenCode [context extraction|commit analysis|review] command failed with return code [non-zero]
```

#### Causes and Solutions

##### A. OpenCode Not Found

- **Error**: `opencode: command not found`
- **Cause**: OpenCode not installed or not in PATH
- **Solution**: Verify job uses nodeset `debian-opencode-single-node-pod` which has OpenCode pre-installed
- **Check**: `opencode --version` should succeed in the "Verify OpenCode installation" task

##### B. LiteLLM Proxy Connection Failure

- **Error**: Connection refused, timeout, or network errors in stderr
- **Cause**: LiteLLM proxy service not available at `http://litellm.zuul-system.svc.cluster.local:4000`
- **Solution**:
  - Verify proxy is running: `kubectl -n zuul-system get pods | grep litellm`
  - Check service: `kubectl -n zuul-system get svc litellm`
  - Review proxy logs: `kubectl -n zuul-system logs deployment/litellm`
- **Alternative**: Temporarily change `litellm_base_url` job variable to test different endpoint

##### C. Model Not Available

- **Error**: Model `litellm-homelab/glm-4.6` or `litellm-homelab/glm-4.5-air` not found
- **Cause**: LiteLLM proxy doesn't have model configured
- **Solution**:
  - Check LiteLLM config: Review the proxy's model mappings
  - Override models in child job:

    ```yaml
    - job:
        name: my-custom-review
        parent: openstack-ai-code-review-base
        vars:
          review_model: "litellm-homelab/alternative-model"
          context_model: "litellm-homelab/alternative-model"
    ```

##### D. Agent Definition Missing or Malformed

- **Error**: Agent `zuul-context-extractor` not found
- **Cause**: Agent files not copied or invalid markdown format
- **Solution**: Check "Validate agent deployment" task output:
  - Should show: "Successfully deployed [6] agent(s)"
  - If failed: Verify `github.com/SeanMooney/openstack-ai-style-guide` is in `required-projects`
  - Check agents exist in style guide repo: `agents/*.md`

##### E. API Authentication Failure

- **Error**: 401 Unauthorized, 403 Forbidden
- **Cause**: Zuul secret not properly configured or decrypted
- **Solution**:
  - Verify secret exists: Check Zuul tenant configuration
  - Re-encrypt key: Follow instructions in `zuul.d/secrets.yaml`
  - Test manually: `curl -H "Authorization: Bearer $KEY" http://litellm.zuul-system.svc.cluster.local:4000/v1/models`

---

### 2. Missing Output Files

#### Symptom

```text
[Context extraction|Commit analysis|Code review] command succeeded but did not produce expected output file.
```

#### Causes and Solutions

##### A. File Written to Wrong Location

- **Cause**: Agent wrote output to working directory instead of `{{ review_output_dir }}`
- **Check**: Look in project source directory for the file
- **Solution**: Agent prompts explicitly specify absolute paths like:

  ```text
  Write the output to {{ review_output_dir }}/zuul-context.md
  ```

- **Verify**: Check that `review_output_dir` is set correctly (default: `{{ ansible_user_dir }}/logs/code-review`)

##### B. File Permission Issues

- **Cause**: Agent can't write to output directory
- **Check**: Verify "Ensure output directories exist" task succeeded
- **Solution**: Directory should be created with mode `0755`

##### C. Agent Partial Failure

- **Cause**: Agent started but encountered error mid-execution
- **Check**: Review stdout for agent error messages
- **Solution**: Check OpenCode logs at `.local/share/opencode/log/` for detailed agent execution trace

---

### 3. Agent Deployment Failures

#### Symptom

```text
Agent deployment failed! Expected [6] agents, but found [0] in [directory].
```

#### Causes and Solutions

##### A. Style Guide Project Not Checked Out

- **Cause**: `github.com/SeanMooney/openstack-ai-style-guide` missing from workspace
- **Solution**: Verify in job definition:

  ```yaml
  required-projects:
    - name: github.com/SeanMooney/openstack-ai-style-guide
      override-checkout: master
  ```

##### B. Incorrect Project Path

- **Cause**: Project name changed or path misconfigured
- **Check**: Variable `style_guide_project` should resolve correctly
- **Solution**: Verify Zuul checked out the project:

  ```bash
  ls -la {{ zuul.projects['github.com/SeanMooney/openstack-ai-style-guide'].src_dir }}/agents/
  ```

##### C. rsync/synchronize Failure

- **Cause**: File copy operation failed
- **Check**: Look for errors in "Copy agents from style guide repo" task
- **Solution**: Verify source and destination directories are accessible

---

### 4. Style Guide File Access Issues

#### Symptom

```text
Could not access style guide files (quick-rules.md, comprehensive-guide.md)
```

#### Causes and Solutions

##### A. Missing Style Guide Docs

- **Cause**: Style guide repo checked out but docs/ directory missing
- **Check**: Verify prerequisite files exist in "Verify prerequisite context files exist" task
- **Solution**: Ensure style guide repo has complete structure:

  ```text
  docs/
    quick-rules.md
    comprehensive-guide.md
  agents/
    *.md (agent definitions)
  ```

##### B. File Path Variables Incorrect

- **Cause**: `style_guide_project` variable not resolving
- **Solution**: Check "Display job context" task output for correct paths

---

### 5. Job Timeout

#### Symptom

```text
Job exceeded timeout (600 seconds)
```

#### Causes and Solutions

##### A. Large Changeset

- **Cause**: Reviewing massive code changes takes too long
- **Solution**: Increase timeout in child job:

  ```yaml
  - job:
      name: extended-review
      parent: openstack-ai-code-review-base
      timeout: 1200  # 20 minutes
  ```

##### B. LiteLLM Proxy Slow Response

- **Cause**: Model inference taking too long
- **Solution**:
  - Use faster model: Override `review_model` to `litellm-homelab/glm-4.5-flash`
  - Check proxy performance: Review proxy metrics/logs

---

## Debugging Workflow

When a job fails, follow these steps:

### Step 1: Identify the Failure Point

Look at console output to find which playbook/task failed:

- `extract-context.yaml` - Context extraction phase
- `analyze-commit.yaml` - Commit analysis phase
- `perform-review.yaml` - Code review phase
- `run.yaml` - Setup or deployment phase

### Step 2: Check OpenCode Command Output

Each phase displays:

- **On Success**: stdout with agent output
- **On Failure**: Detailed error with both stdout and stderr, plus diagnostic guidance

### Step 3: Review Log Files

Check Zuul log artifacts:

1. `logs/code-review/index.md` - Summary of all outputs
2. `logs/code-review/*.md` - Individual phase outputs (if created)
3. `logs/.local/share/opencode/log/` - OpenCode internal logs

### Step 4: Verify Prerequisites

Common prerequisites to verify:

- [ ] OpenCode installed and in PATH
- [ ] LiteLLM proxy accessible from CI node
- [ ] Models configured in LiteLLM
- [ ] Zuul secret properly encrypted
- [ ] Style guide project checked out
- [ ] Agents deployed successfully (6 total)

### Step 5: Test Components Independently

If still stuck, test individual components:

**Test OpenCode:**

```bash
opencode --version
opencode run --agent "zuul-context-extractor" --model "litellm-homelab/glm-4.5-air" "test prompt"
```

**Test LiteLLM Connectivity:**

```bash
curl -H "Authorization: Bearer $LITELLM_API_KEY" \
  http://litellm.zuul-system.svc.cluster.local:4000/v1/models
```

**Test Agent Availability:**

```bash
ls -la ~/.config/opencode/agent/*.md
```

---

## Configuration Reference

### Job Variables

You can override these in child jobs:

| Variable | Default | Purpose |
|----------|---------|---------|
| `context_model` | `litellm-homelab/glm-4.5-air` | Model for context extraction and commit analysis |
| `review_model` | `litellm-homelab/glm-4.6` | Model for code review |
| `litellm_base_url` | `http://litellm.zuul-system.svc.cluster.local:4000/v1` | LiteLLM proxy endpoint |
| `review_output_dir` | `{{ ansible_user_dir }}/logs/code-review` | Output directory for reports |
| `opencode_config_dir` | `{{ ansible_user_dir }}/.config/opencode` | OpenCode configuration directory |

### Model Options

Available models (homelab setup):

- `litellm-homelab/glm-4.6` - Full capability model (slower, more accurate)
- `litellm-homelab/glm-4.5-air` - Balanced model
- `litellm-homelab/glm-4.5-flash` - Fast model (less thorough)

---

## Getting Help

If you've tried these solutions and still have issues:

1. **Check Recent Changes**: Review recent commits to this repository
2. **Review Job History**: Look at successful runs for comparison
3. **Examine Full Logs**: Download complete log archive from Zuul
4. **Check Zuul Status**: Verify no system-wide issues
5. **Test Locally**: If possible, run OpenCode locally with same config

---

## Advanced Debugging

### Enable Verbose OpenCode Logging

Temporarily modify playbook tasks to use:

```yaml
opencode run --print-logs --log-level "DEBUG" --agent "..." --model "..." "..."
```

### Inspect OpenCode Configuration

Check generated config:

```bash
cat ~/.config/opencode/opencode.json
```

Should contain:

- Provider configuration for `litellm-homelab`
- Model definitions for GLM models
- Correct base URL and API key reference

### Manual Agent Execution

Test agents manually:

```bash
cd {{ project_src_dir }}
opencode run --agent "commit-summary" \
  --model "litellm-homelab/glm-4.5-air" \
  "Analyze the current git commit and create a summary"
```

---

## Common Patterns

### Pattern: "Works Locally, Fails in CI"

Usually indicates:

- Network connectivity difference (LiteLLM proxy not accessible)
- Path differences (files in different locations)
- Permission differences (file access restrictions)

### Pattern: "Failed Once, Now Always Fails"

Check:

- OpenCode cache/state files
- Stale agent definitions
- LiteLLM proxy health

### Pattern: "Job Passes But Report Empty"

Indicates:

- Agent completed but didn't write output
- Output written to wrong location
- Agent prompt needs refinement

---

---

## Last Updated

Based on commit 78bdebc (Improve code review job security and reliability)
