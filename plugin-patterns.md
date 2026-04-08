# Claude Code Plugin Patterns Reference

This document captures patterns and conventions from Anthropic's first-party Claude Code
plugins (`code-review`, `pr-review-toolkit`, `claude-opus-4-5-migration`). Use this as a
reference when building Claude Code plugins.

## Plugin Directory Structure

### Standard Layout

```text
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Required: Plugin metadata
├── README.md                # Optional: User-facing documentation
├── commands/                # Optional: Slash command definitions
│   └── command-name.md
├── agents/                  # Optional: Specialized agent definitions
│   └── agent-name.md
└── skills/                  # Optional: Skill definitions with references
    └── skill-name/
        ├── SKILL.md
        └── references/
            └── detail-doc.md
```

### Plugin Types by Structure

**Command-Centric Plugins** (like `code-review`):

- Single command in `commands/` that orchestrates the entire workflow
- All logic embedded in the command file
- Best for: Automated workflows with clear start and end

**Agent-Centric Plugins** (like `pr-review-toolkit`):

- Multiple specialized agents in `agents/`
- Command in `commands/` that orchestrates agent selection
- Best for: Multi-aspect analysis with specialized expertise

**Skill-Centric Plugins** (like `claude-opus-4-5-migration`):

- Skills in `skills/` with detailed references
- Best for: Knowledge-heavy tasks with reference documentation

---

## Plugin Manifest: `.claude-plugin/plugin.json`

The manifest file is **required** and defines plugin metadata.

### Schema

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Brief description of what the plugin does",
  "author": {
    "name": "Author Name",
    "email": "author@example.com"
  }
}
```

### Field Requirements

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Plugin identifier (kebab-case recommended) |
| `version` | Yes | Semantic version string |
| `description` | Yes | One-line description of plugin functionality |
| `author.name` | Yes | Author's display name |
| `author.email` | Yes | Author's contact email |

### Examples from First-Party Plugins

```json
// code-review
{
  "name": "code-review",
  "description": "Automated code review for pull requests using multiple specialized agents with confidence-based scoring",
  "version": "1.0.0",
  "author": {"name": "Boris Cherny", "email": "boris@anthropic.com"}
}

// pr-review-toolkit
{
  "name": "pr-review-toolkit",
  "version": "1.0.0",
  "description": "Comprehensive PR review agents specializing in comments, tests, error handling, type design, code quality, and code simplification",
  "author": {"name": "Daisy", "email": "daisy@anthropic.com"}
}
```

---

## Command Definitions: `commands/*.md`

Commands define slash-command workflows triggered by `/plugin-name:command-name`.

### Frontmatter Schema

```yaml
---
description: "Brief description of what the command does"
argument-hint: "[optional-args]"
allowed-tools: ["Tool1", "Tool2", "Bash(pattern:*)"]
---
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `description` | Yes | Shown in command help/autocomplete |
| `argument-hint` | No | Hint for expected arguments |
| `allowed-tools` | No | Tool allowlist for security scoping |

### Tool Allowlist Patterns

The `allowed-tools` field restricts which tools the command can use:

```yaml
# Allow specific tools
allowed-tools: ["Bash", "Read", "Write", "Edit", "Grep", "Glob", "Task"]

# Allow tool with argument patterns
allowed-tools: ["Bash(git log:*)", "Bash(git diff:*)"]

# Allow MCP tools
allowed-tools: ["mcp__github_inline_comment__create_inline_comment"]
```

### Command Body Structure

Commands use numbered steps for workflow clarity:

```markdown
---
description: "Review a pull request"
allowed-tools: ["Bash", "Read", "Task"]
---

**Agent assumptions (applies to all agents and subagents):**
- All tools are functional and will work without error
- Only call a tool if required to complete the task

To do this, follow these steps precisely:

1. Launch a haiku agent to check pre-flight conditions...

2. Launch a sonnet agent to gather context...

3. Launch 4 agents in parallel to review:
   - Agent 1: CLAUDE.md compliance (sonnet)
   - Agent 2: CLAUDE.md compliance (sonnet)
   - Agent 3: Bug detection (opus)
   - Agent 4: Security review (opus)

4. For each issue found, launch validation subagents...

5. Post results using appropriate tool...
```

### Key Command Patterns

**Agent Assumptions Section:**
Include at the top to ensure consistent behavior:

```markdown
**Agent assumptions (applies to all agents and subagents):**
- All tools are functional and will work without error
- Only call a tool if it is required to complete the task
```

**Model Selection:**
Specify models for each step based on task complexity:

- `haiku` - Quick checks, file discovery, pre-flight validation
- `sonnet` - Compliance checking, summarization, validation
- `opus` - Bug detection, security analysis, complex reasoning

**Parallel Execution:**
Use parallel agents for independent tasks:

```markdown
3. Launch 4 agents in parallel to independently review the changes.
   Each agent should return the list of issues...
```

**Validation Layer:**
Add validation step before output:

```markdown
5. For each issue found in the previous step, launch parallel
   subagents to validate the issue. Use Opus subagents for bugs
   and Sonnet agents for compliance violations.
```

---

## Agent Definitions: `agents/*.md`

Agents are specialized subagents that can be launched via the Task tool.

### Frontmatter Schema

```yaml
---
name: agent-name
description: |
  When to use this agent. Use when... followed by example scenarios.

  Examples:
  <example>
  Context: User has just implemented a feature
  user: "Can you review my code?"
  assistant: "I'll launch the code-reviewer agent..."
  </example>
model: opus|sonnet|haiku|inherit
color: green|blue|yellow|pink|cyan
---
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Agent identifier (kebab-case) |
| `description` | Yes | Activation conditions with examples |
| `model` | No | Model to use (default: `inherit`) |
| `color` | No | Visual identifier in UI |

### Description Format

The description field should include:

1. **Activation trigger**: "Use when..." statement
2. **Examples**: Scenarios showing when to invoke the agent

```yaml
description: |
  Use this agent when you need to review code for adherence to project
  guidelines. This agent should be used proactively after writing or
  modifying code, especially before committing changes.

  Examples:
  <example>
  Context: The user has just implemented a new feature.
  user: "I've added the new authentication feature. Can you check it?"
  assistant: "I'll launch the code-reviewer agent to review your changes."
  </example>
```

### Model Selection Guidelines

| Model | Use For | Cost/Speed |
|-------|---------|------------|
| `haiku` | Quick checks, file discovery | Fastest, cheapest |
| `sonnet` | Compliance, summarization, validation | Balanced |
| `opus` | Bug detection, security, complex analysis | Most capable |
| `inherit` | Use parent conversation's model | Depends on parent |

### Agent Body Structure

```markdown
---
name: code-reviewer
description: Use when reviewing code...
model: opus
color: green
---

You are an expert code reviewer specializing in...

## Review Scope

By default, review unstaged changes from `git diff`.

## Core Review Responsibilities

**Project Guidelines Compliance**: Verify adherence to...

**Bug Detection**: Identify actual bugs that will...

## Issue Confidence Scoring

Rate each issue from 0-100:
- **91-100**: Critical (explicit violations, clear bugs)
- **80-90**: Important (strong evidence)
- **0-79**: DO NOT REPORT

**Only report issues with confidence >= 80**

## Output Format

For each issue provide:
- Clear description and confidence score
- File path and line number
- Specific rule or bug explanation
- Concrete fix suggestion

Group issues by severity (Critical: 90-100, Important: 80-89).
```

---

## Skill Definitions: `skills/*/SKILL.md`

Skills provide knowledge-based guidance with supporting references.

### Directory Structure

```text
skills/
└── skill-name/
    ├── SKILL.md              # Main skill definition
    └── references/           # Supporting documentation
        ├── concept-1.md
        └── concept-2.md
```

### SKILL.md Frontmatter

```yaml
---
name: skill-name
description: Brief description. Use when the user wants to...
---
```

### SKILL.md Body Structure

```markdown
---
name: claude-opus-4-5-migration
description: Migrate prompts and code to Opus 4.5. Use when the user
  wants to update their codebase, prompts, or API calls.
---

# Skill Title

Brief overview.

## Workflow

1. Step one...
2. Step two...
3. Reference `references/detail.md` for specifics...

## Configuration Tables

| Setting | Value |
|---------|-------|
| ... | ... |

## Conditional Guidance

**Apply if**: User reports specific issue...

**Fix**: Add snippet from `references/snippets.md`

## Reference

See `references/concept.md` for full details.
```

### Reference Organization

References provide detailed documentation separate from the workflow:

- `references/effort.md` - Configuration details and examples
- `references/prompt-snippets.md` - Reusable text snippets
- `references/migration-guide.md` - Step-by-step procedures

---

## Confidence Scoring Patterns

### Scale Options

**0-100 Scale** (pr-review-toolkit):

```text
91-100: Critical (must fix before merge)
80-90:  Important (should fix)
0-79:   DO NOT REPORT
```

**Categorical Scale** (silent-failure-hunter):

```text
CRITICAL: Silent failures, broad catches
HIGH:     Poor error messages, unjustified fallbacks
MEDIUM:   Missing context, could be more specific
```

### Filtering Rules

Only report issues meeting the threshold:

```markdown
**Only report issues with confidence >= 80**
```

### Output Grouping

Group issues by severity for actionability:

```markdown
## Critical Issues (X found)
- [agent-name]: Issue description [file:line]

## Important Issues (X found)
- [agent-name]: Issue description [file:line]
```

---

## False Positive Prevention

### Explicit Exclusion Lists

Include in command/agent prompts:

```markdown
Do NOT flag:
- Pre-existing issues
- Something that appears to be a bug but is actually correct
- Pedantic nitpicks that a senior engineer would not flag
- Issues that a linter will catch
- General code quality concerns unless required in CLAUDE.md
- Issues explicitly silenced in code (e.g., lint ignore comments)
```

### Validation Layer

Add validation step before output:

```markdown
For each issue found, launch parallel subagents to validate:
1. Subagent receives issue description and PR context
2. Subagent reviews code to confirm issue exists
3. Only validated issues proceed to output
```

### Project-Specific Awareness

Reference project configuration:

```markdown
Before starting your review, ALWAYS check for and read:
1. **CLAUDE.md** - Project-specific guidance
2. **AGENTS.md** - Agent definitions and rules

When you find these files:
1. Read them completely before analyzing code
2. Extract exceptions and rules
3. Apply them as binding rules (override defaults)
4. Skip flagged items
```

---

## Multi-Agent Orchestration

### Parallel Execution

Launch independent agents simultaneously:

```markdown
3. Launch 4 agents in parallel to independently review:
   - Agents 1 + 2: CLAUDE.md compliance (sonnet) - redundancy
   - Agent 3: Bug scanning (opus)
   - Agent 4: Security review (opus)
```

### Sequential Execution

Chain dependent steps:

```markdown
1. Launch haiku agent for pre-flight checks
2. If checks pass, launch sonnet agent for context gathering
3. Launch review agents with gathered context
4. Launch validation agents for each finding
5. Aggregate and output results
```

### Context Injection

Pass context to subagents:

```markdown
Each subagent should be told:
- PR title and description
- Relevant CLAUDE.md rules
- Summary of changes from step 2
```

---

## Output Formatting

### Structured JSON

For machine parsing:

```json
{
  "context": {...},
  "statistics": {"critical": 0, "high": 0, "warnings": 0, "total": 0},
  "issues": {
    "critical": [...],
    "high": [...],
    "warnings": [...],
    "suggestions": [...]
  },
  "summary": {...}
}
```

### File References

Include actionable locations:

```markdown
- File path and line number: `src/module.py:123`
- Link format with full SHA for GitHub:
  https://github.com/org/repo/blob/abc123def/src/module.py#L120-L125
```

### Issue Structure

```markdown
For each issue:
- Clear description and confidence score
- File path and line number
- Specific rule or bug explanation
- Concrete fix suggestion
- (Optional) Committable suggestion block for small fixes
```

---

## Best Practices Summary

1. **Use YAML frontmatter** for metadata in all markdown files
2. **Include examples** in agent descriptions for activation clarity
3. **Specify model selection** based on task complexity
4. **Add validation layers** to reduce false positives
5. **Use parallel execution** for independent tasks
6. **Include exclusion lists** to prevent noise
7. **Reference project config** (CLAUDE.md) for project-specific rules
8. **Group output by severity** for actionability
9. **Provide confidence scores** with clear thresholds
10. **Include file:line references** for all findings
