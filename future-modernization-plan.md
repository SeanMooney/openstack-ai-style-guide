# TEIM Code Review Future Modernization Plan

This document contains a detailed planning prompt for future sessions to implement
the remaining phases of the TEIM code review modernization. Use this as context when
continuing the work.

## Completed Work (Phase 1-2)

The following has been implemented:

### Phase 1: Research Documentation

- `plugin-patterns.md` - Reference document on Claude Code plugin structure
- `ai-code-review-techniques.md` - Reference document on AI code review patterns

### Phase 2: JSON Reliability Fix

- Updated `run_claude_code` role with `--json-schema` support for structured output
- Updated `ai_code_review` role to pass schema and add validation/repair steps
- Created `validate_review_schema.py` - Schema validation safety net
- Created `repair_review_json.py` - JSON repair fallback
- Created `fallback-report.json.j2` - Fallback report template
- Updated agent prompts with clearer output requirements

---

## Remaining Phases

### Phase 3: Plugin Structure Migration

**Goal:** Convert the openstack-ai-style-guide repository to a Claude Code plugin
that can be installed and used locally via Claude Code.

#### 3.1 Create Plugin Manifest

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "teim-review",
  "version": "1.0.0",
  "description": "OpenStack-focused code review with agentic RAG for project guidelines",
  "author": {
    "name": "Sean Mooney",
    "email": "sean@teim.app"
  }
}
```

#### 3.2 Create Main Command

Create `commands/teim-review.md`:

```yaml
---
description: "OpenStack-focused code review with project-specific guidelines"
argument-hint: "[files|--all|--commit|--pr]"
allowed-tools: ["Bash", "Read", "Write", "Edit", "Grep", "Glob", "Task"]
---
```

**Workflow:**

1. Pre-flight (Haiku): Detect review scope
2. Guidelines Aggregation (Haiku): Run guidelines-aggregator
3. Context Gathering (Haiku): Extract commit metadata
4. Code Review (Opus/GLM-4.6): Run code-review-agent
5. Validation (Sonnet): Validate high-severity findings
6. Output: Generate structured JSON report

#### 3.3 Create Interactive Command

Create `commands/interactive-review.md`:

```yaml
---
description: "Interactive local code review with real-time feedback"
argument-hint: "[files|--staged|--working-tree]"
allowed-tools: ["Bash", "Read", "Write", "Edit", "Grep", "Glob", "Task"]
---
```

**Features:**

- Detect working tree or staged changes
- Run teim-review workflow
- Present findings interactively
- Offer to apply suggested fixes
- Re-run review after fixes (optional)

#### 3.4 Create Skill Definition

Create `skills/teim-review/SKILL.md`:

```yaml
---
name: teim-review
description: OpenStack code review skill. Use when reviewing Python, Ansible,
  or bash code for OpenStack projects.
---
```

**Contents:**

- Quick reference for OpenStack coding standards
- Links to detailed documentation
- Model selection guidelines

Create `skills/teim-review/references/`:

- `openstack-rules.md` - Quick coding standards reference
- `scoring-guide.md` - Confidence scoring guidelines

#### 3.5 Update Agent Frontmatter

Update all agents in `agents/` with plugin-compatible frontmatter:

```yaml
---
name: code-review-agent
description: |
  OpenStack code review agent. Use when reviewing Python, Ansible, or bash code
  for OpenStack projects. Automatically applies project-specific guidelines from
  CLAUDE.md, AGENTS.md, and HACKING.rst.
model: inherit  # CI: glm-4.6, Local: opus
color: blue
---
```

---

### Phase 4: Agentic RAG System

**Goal:** Dynamically incorporate review guidelines from repositories under review
using a file-based RAG system.

#### 4.1 Create Guidelines Directory Structure

Create `guidelines/` directory mirroring canonical repo structure:

```text
guidelines/
├── README.md                          # Documentation
├── opendev.org/
│   └── openstack/
│       ├── nova/
│       │   ├── HACKING.rst
│       │   └── rules.md
│       ├── tempest/
│       │   ├── HACKING.rst
│       │   └── rules.md
│       └── neutron/
│           └── rules.md
└── github.com/
    └── openstack/
        └── python-openstackclient/
            └── rules.md
```

#### 4.2 Document Precedence Rules

In `guidelines/README.md`:

```markdown
# Guidelines Precedence

1. **Repository's own files** (highest priority)
   - CLAUDE.md (root and parent directories)
   - AGENTS.md
   - HACKING.rst

2. **Mirror in guidelines/** (fallback)
   - guidelines/{canonical_name}/HACKING.rst
   - guidelines/{canonical_name}/rules.md

3. **Default OpenStack guidelines** (base)
   - docs/quick-rules.md
   - docs/comprehensive-guide.md
```

#### 4.3 Create Guidelines Aggregator Agent

Create `agents/guidelines-aggregator.md`:

**Purpose:** Prepare consolidated review rules for any given repository.

**Workflow:**

1. Identify target repository canonical name
2. Check repository for guideline files:
   - CLAUDE.md (root and parent directories)
   - AGENTS.md
   - HACKING.rst
3. Check `guidelines/` mirror for matching path
4. Detect plugin relationships:
   - `*-tempest-plugin` → inherit `openstack/tempest` HACKING.rst
   - `*-neutron-*` → inherit `openstack/neutron` rules
5. Merge rules with precedence (repo > mirror > default)
6. Output consolidated `review-rules.md` for the review agent

**Key Features:**

- Automatic detection of plugin parent projects
- Conflict resolution with repo-first precedence
- Structured output for downstream agent consumption
- Caching support for repeated reviews of same repo

#### 4.4 Create Ansible Role for Guidelines

Create `roles/ai_guidelines_aggregation/`:

```yaml
# tasks/main.yaml
- name: Identify repository canonical name
  # Extract from zuul context or git remote

- name: Check for repo guideline files
  # Look for CLAUDE.md, AGENTS.md, HACKING.rst

- name: Check guidelines/ mirror
  # Look for matching path in guidelines/

- name: Run guidelines-aggregator agent
  # Invoke agent via run_claude_code

- name: Output review-rules.md
  # Write consolidated rules
```

#### 4.5 Update Playbook Workflow

Update `playbooks/teim-code-review/run.yaml`:

```yaml
roles:
  - ai_review_setup
  - ai_guidelines_aggregation  # NEW
  - ai_context_extraction
  - ai_code_review            # Pass aggregated rules
  - ai_html_generation
  - ai_zuul_integration
```

---

### Phase 5: Validation Layer

**Goal:** Add validation subagents to verify high-severity findings before output.

#### 5.1 Validation Pattern

For each critical/high finding:

```text
1. Launch validation subagent:
   - Opus for bugs and logic issues
   - Sonnet for CLAUDE.md/rule violations

2. Subagent receives:
   - Issue description
   - File location
   - PR/commit context
   - Relevant guidelines

3. Subagent task:
   - Review the specific code section
   - Verify the issue actually exists
   - Confirm it's not a false positive
   - Return validation result

4. Filter:
   - Only report validated issues
   - Log unvalidated issues for debugging
```

#### 5.2 Update Review Agent

Add validation step to code-review-agent workflow:

```markdown
### Validation Step

For each critical or high severity finding:

1. Launch a validation subagent to confirm the issue
2. Pass: issue description, location, context
3. Subagent verifies the issue exists in the code
4. Only include validated issues in final report
5. Log unvalidated issues as "filtered" for debugging
```

---

### Phase 6: Dual-Mode Architecture

**Goal:** Support both CI mode (Zuul) and local interactive mode.

#### 6.1 CI Mode (Zuul)

```text
┌─────────────────────────────────────────────────────────────────┐
│                        Zuul CI Pipeline                          │
├─────────────────────────────────────────────────────────────────┤
│  Ansible Playbook → Roles → Claude CLI (GLM models via LiteLLM) │
│                                                                  │
│  Models:                                                         │
│  - Context/Haiku: glm-4.5-air (fast, cheap)                     │
│  - Review/Opus: glm-4.6 (capable, cost-effective)               │
│                                                                  │
│  Output: JSON report → Zuul comments → HTML artifact             │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.2 Local Mode (Interactive)

```text
┌─────────────────────────────────────────────────────────────────┐
│                     Local Interactive Mode                       │
├─────────────────────────────────────────────────────────────────┤
│  /teim-review:interactive-review command                         │
│                                                                  │
│  Models:                                                         │
│  - Orchestration: opus (highest capability)                     │
│  - Context/Summary: haiku (fast)                                │
│  - Validation: sonnet (balanced)                                │
│                                                                  │
│  Output: Interactive terminal feedback + optional fixes          │
└─────────────────────────────────────────────────────────────────┘
```

#### 6.3 Mode Detection

The command should auto-detect mode based on environment:

```markdown
**Mode Detection:**

1. Check for `ZUUL_PIPELINE` environment variable:
   - If present: CI mode
   - If absent: Local mode

2. CI Mode behavior:
   - Use GLM models via LiteLLM
   - Write JSON report to specified path
   - Generate Zuul comments
   - Non-interactive

3. Local Mode behavior:
   - Use native Anthropic models
   - Present findings interactively
   - Offer fix suggestions
   - Support watch mode
```

---

### Phase 7: Language Support

**Primary Languages:**

- Python - Core OpenStack code
- Ansible - Playbooks and roles
- Bash - Shell scripts

**Secondary Languages:**

- Go - CLI tools
- JavaScript - Dashboard/UI

**Future Languages:**

- Rust

#### Guidelines per Language

Create language-specific rules in `guidelines/`:

- `guidelines/languages/python.md` - Python-specific rules
- `guidelines/languages/ansible.md` - Ansible-specific rules
- `guidelines/languages/bash.md` - Bash-specific rules

---

## Implementation Priority

1. **Phase 3** (Plugin Structure) - Enables local usage
2. **Phase 4** (Agentic RAG) - Dynamic guideline incorporation
3. **Phase 5** (Validation Layer) - Reduces false positives
4. **Phase 6** (Dual-Mode) - Full CI + local support

---

## Planning Prompt for Future Sessions

Use this prompt when starting a new session to continue the work:

```text
I'm continuing work on the openstack-ai-style-guide TEIM code review modernization.

Context:
- Phase 1-2 completed: Research docs + JSON reliability fix
- Remaining: Plugin structure, agentic RAG, validation layer, dual-mode

Please read:
1. /home/sean/repos/openstack-ai-style-guide/future-modernization-plan.md (this file)
2. /home/sean/repos/openstack-ai-style-guide/plugin-patterns.md
3. /home/sean/repos/openstack-ai-style-guide/ai-code-review-techniques.md

I want to implement [SPECIFY PHASE] next. Focus on:
- [SPECIFIC GOALS]
- [CONSTRAINTS]
- [TESTING APPROACH]
```

---

## Success Criteria

### Phase 3 (Plugin Structure)

- Plugin can be installed locally via Claude Code
- `/teim-review:teim-review` command works
- Agents use correct model based on mode

### Phase 4 (Agentic RAG)

- guidelines-aggregator correctly merges repo + mirror rules
- Plugin detection works (tempest plugins inherit tempest rules)
- Precedence rules enforced (repo > mirror > default)

### Phase 5 (Validation Layer)

- Validation subagents confirm high-severity findings
- False positives reduced by >50%
- Unvalidated issues logged for debugging

### Phase 6 (Dual-Mode)

- CI mode produces same results as current implementation
- Local mode provides interactive feedback
- Mode auto-detection works correctly

---

## Testing Strategy

### Unit Testing

- Validate JSON schema scripts work correctly
- Test repair script handles edge cases
- Test guidelines aggregation logic

### Integration Testing

- Run CI job on test changes
- Verify HTML report generation
- Check Zuul comment posting

### Local Testing

- Install plugin locally
- Run interactive review on sample code
- Verify guideline aggregation

---

## Notes

### Model Costs

- CI: GLM models are cost-effective for high-volume CI
- Local: Native Anthropic models for best quality

### Backward Compatibility

- Keep existing Ansible roles functional
- Zuul jobs continue to work during migration
- Phased rollout minimizes risk

### Security

- API keys handled via environment variables
- No secrets in repository
- LiteLLM proxy for CI isolation
