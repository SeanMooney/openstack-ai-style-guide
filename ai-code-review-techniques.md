# AI Code Review Techniques Reference

This document captures AI code review techniques and patterns from Anthropic's first-party
plugins (`code-review`, `pr-review-toolkit`). Use this as a reference when implementing
AI-assisted code review systems.

## Multi-Agent Orchestration

### Agent Role Specialization

Effective AI code review uses specialized agents for different aspects:

| Agent Type | Model | Responsibility |
|------------|-------|----------------|
| Pre-flight | Haiku | Quick checks, file discovery, skip conditions |
| Context Gatherer | Haiku/Sonnet | CLAUDE.md discovery, PR summary |
| Compliance Auditor | Sonnet | CLAUDE.md/guideline violations |
| Bug Scanner | Opus | Logic errors, security issues |
| Validator | Opus/Sonnet | Confirm flagged issues are real |

### Parallel vs Sequential Execution

**Sequential Steps** (dependencies between steps):

```text
1. Pre-flight checks (Haiku)
   ↓ (only continue if checks pass)
2. Context gathering (Haiku/Sonnet)
   ↓ (provides context for review)
3. Parallel review agents
   ↓ (findings from all agents)
4. Validation layer
   ↓ (validated findings only)
5. Output generation
```

**Parallel Execution** (independent tasks):

```text
Step 4: Launch 4 agents in parallel:
├── Agent 1: CLAUDE.md compliance (Sonnet)
├── Agent 2: CLAUDE.md compliance (Sonnet)  ← Redundancy
├── Agent 3: Bug scanning (Opus)
└── Agent 4: Security review (Opus)
```

### Redundancy Pattern

Use multiple agents for the same task to catch more issues:

```markdown
Agents 1 + 2: CLAUDE.md compliance sonnet agents
Audit changes for CLAUDE.md compliance in parallel.
```

Two agents reviewing the same aspect catch issues that one might miss while
maintaining high precision through the validation layer.

---

## Pre-Flight Checks

Before running the full review, verify conditions that would make review unnecessary:

### Skip Conditions

```markdown
Launch a haiku agent to check if any of the following are true:
- The pull request is closed
- The pull request is a draft
- The pull request does not need code review (e.g., automated PR, trivial change)
- The reviewer has already commented on this PR

If any condition is true, stop and do not proceed.
```

### Trivial Change Detection

Identify changes that don't need full review:

- Documentation-only changes
- Dependency version bumps
- Auto-generated code updates
- Formatting-only changes

---

## Context Gathering

### CLAUDE.md Scoping

Guidelines apply hierarchically based on file location:

```markdown
When evaluating CLAUDE.md compliance for a file, only consider
CLAUDE.md files that share a file path with the file or parents.

Example: For `src/api/handlers/user.py`:
- Consider: /CLAUDE.md, /src/CLAUDE.md, /src/api/CLAUDE.md
- Ignore: /tests/CLAUDE.md (different path)
```

### Context Injection Pattern

Pass relevant context to all subagents:

```markdown
Each subagent should be told:
- PR title and description (author's intent)
- Relevant CLAUDE.md rules (project-specific guidelines)
- Summary of changes (scope understanding)
```

### Git Diff Focus

Scope analysis to changed code only:

```markdown
Focus only on the diff itself without reading extra context.
Do not flag issues that you cannot validate without looking
at context outside of the git diff.
```

This prevents:

- Flagging pre-existing issues
- Scope creep into unrelated code
- False positives from missing context

---

## Confidence Scoring Systems

### 0-100 Scale (pr-review-toolkit)

```text
91-100: Critical
        - Code will fail to compile/parse
        - Code will definitely produce wrong results
        - Clear, unambiguous rule violations

80-90:  Important
        - Strong evidence of issue
        - High confidence finding

0-79:   DO NOT REPORT
        - Insufficient confidence
        - Likely false positive
        - Subjective/style concerns
```

### Threshold Enforcement

```markdown
**Only report issues with confidence >= 80**

Rate each issue from 0-100:
- **0-25**: Likely false positive or pre-existing issue
- **26-50**: Minor nitpick not explicitly in CLAUDE.md
- **51-75**: Valid but low-impact issue
- **76-90**: Important issue requiring attention
- **91-100**: Critical bug or explicit CLAUDE.md violation
```

### Severity Grouping

Group findings by severity for actionability:

```markdown
## Critical Issues (X found)
Issues that must be fixed before merge.
- [file:line]: Description (confidence: 95)

## Important Issues (X found)
Issues that should be addressed.
- [file:line]: Description (confidence: 85)

## Suggestions
Optional improvements.
- [file:line]: Description
```

### Test Coverage Criticality Scale (1-10)

For test analysis specifically:

```text
9-10: Critical functionality - data loss, security, system failures
7-8:  Important business logic - user-facing errors
5-6:  Edge cases - confusion or minor issues
3-4:  Nice-to-have for completeness
1-2:  Optional minor improvements
```

---

## False Positive Prevention

### Explicit Exclusion Lists

Include in every review agent's prompt:

```markdown
Do NOT flag:
- Pre-existing issues
- Something that appears to be a bug but is actually correct
- Pedantic nitpicks that a senior engineer would not flag
- Issues that a linter will catch (do not run the linter to verify)
- General code quality concerns unless explicitly required in CLAUDE.md
- Issues mentioned in CLAUDE.md but explicitly silenced in the code
  (e.g., via a lint ignore comment)
```

### High Signal Requirement

```markdown
**CRITICAL: We only want HIGH SIGNAL issues.**

Flag issues where:
- The code will fail to compile or parse
- The code will definitely produce wrong results regardless of inputs
- Clear, unambiguous CLAUDE.md violations where you can quote the exact rule

Do NOT flag:
- Code style or quality concerns
- Potential issues that depend on specific inputs or state
- Subjective suggestions or improvements

If you are not certain an issue is real, do not flag it.
False positives erode trust and waste reviewer time.
```

### Validation Layer

Add a separate validation step for each finding:

```markdown
5. For each issue found, launch parallel subagents to validate:

   - Subagent receives: PR context + issue description
   - Subagent task: Review code to confirm issue exists
   - Use Opus subagents for bugs and logic issues
   - Use Sonnet agents for CLAUDE.md violations

6. Filter out any issues that were not validated.
```

This two-stage approach (flag → validate) significantly reduces false positives.

### Certainty Requirement

```markdown
Do not flag issues that you cannot validate without looking at
context outside of the git diff.

If you are not certain an issue is real, do not flag it.
```

---

## Output Formatting

### Structured JSON for Machine Parsing

```json
{
  "context": {
    "change": "Brief description of what changed",
    "scope": "Files/modules affected",
    "impact": "Low/Medium/High"
  },
  "statistics": {
    "critical": 0,
    "high": 0,
    "warnings": 0,
    "suggestions": 0,
    "total": 0
  },
  "issues": {
    "critical": [...],
    "high": [...],
    "warnings": [...],
    "suggestions": [...]
  },
  "positive_observations": [...],
  "summary": {
    "assessment": "Ready|Needs work|Blocked",
    "priority_focus": "Top priority item",
    "detailed_summary": "Overall summary"
  }
}
```

### Issue Structure

Each issue should include:

```json
{
  "description": "Clear description of the issue",
  "confidence": 0.85,
  "location": "path/to/file.py:123",
  "risk": "What could go wrong",
  "why_matters": "Business/technical impact",
  "recommendation": "Specific fix suggestion"
}
```

### File References

Always include actionable locations:

```markdown
- File path and line number: `src/module.py:123`
- For GitHub links, use full SHA:
  https://github.com/org/repo/blob/abc123def/src/module.py#L120-L125

Line range format: L[start]-L[end]
Include 1+ lines of context before and after the issue.
```

### Committable Suggestion Blocks

For small, self-contained fixes:

```markdown
For each comment:
- Provide a brief description of the issue
- For small, self-contained fixes, include a committable suggestion block
- For larger fixes (6+ lines, structural changes, or changes spanning
  multiple locations), describe the issue without a suggestion block
- Never post a committable suggestion UNLESS committing it fixes
  the issue entirely
```

---

## Agent Assumptions Section

Include at the top of all orchestration prompts:

```markdown
**Agent assumptions (applies to all agents and subagents):**
- All tools are functional and will work without error. Do not test tools
  or make exploratory calls.
- Only call a tool if it is required to complete the task. Every tool call
  should have a clear purpose.

Make sure this is clear to every subagent that is launched.
```

This prevents:

- Unnecessary tool testing
- Exploratory calls that waste time
- Inconsistent behavior across agents

---

## Review Aspect Specialization

### Code Quality (code-reviewer)

Focus areas:

- Project guideline compliance (CLAUDE.md)
- Actual bugs that will impact functionality
- Logic errors, null handling, race conditions
- Security vulnerabilities, performance problems

### Test Coverage (pr-test-analyzer)

Focus areas:

- Behavioral coverage (not line coverage)
- Critical code paths that could cause production issues
- Edge cases and boundary conditions
- Error handling paths
- Tests that are resilient to refactoring

### Error Handling (silent-failure-hunter)

Focus areas:

- Silent failures (errors without logging/feedback)
- Broad exception catching that hides errors
- Missing user feedback on errors
- Inappropriate fallback behavior
- Empty catch blocks

### Comment Quality (comment-analyzer)

Focus areas:

- Factual accuracy of comments vs code
- Comment rot (outdated information)
- Missing documentation for complex logic
- Misleading comments

### Type Design (type-design-analyzer)

Focus areas:

- Encapsulation quality
- Invariant expression and enforcement
- Type safety

---

## Model Selection Guidelines

### By Task Type

| Task | Recommended Model | Rationale |
|------|-------------------|-----------|
| Pre-flight checks | Haiku | Simple conditions, fast |
| File discovery | Haiku | Pattern matching, fast |
| PR summarization | Sonnet | Balanced capability |
| Compliance checking | Sonnet | Rule matching |
| Bug detection | Opus | Complex reasoning |
| Security analysis | Opus | Deep analysis |
| Validation | Opus (bugs), Sonnet (rules) | Match original task |

### Cost-Performance Tradeoffs

```text
Haiku:  Fast, cheap, good for simple tasks
        Use for: Pre-flight, discovery, simple validation

Sonnet: Balanced, good for most review tasks
        Use for: Compliance, summarization, validation

Opus:   Expensive, highest capability
        Use for: Bug detection, security, complex reasoning
```

### Parallel Agent Model Mix

For comprehensive review, use a mix:

```text
2x Sonnet (compliance) + 2x Opus (bugs/security)
= Good coverage with reasonable cost
```

---

## Workflow Integration

### Pre-Commit Review

```text
1. Run: code-reviewer on staged changes
2. Fix critical issues
3. Commit
```

### Pre-PR Review

```text
1. Stage all changes
2. Run: full review with all agents
3. Address critical and important issues
4. Run specific reviews again to verify
5. Create PR
```

### CI Pipeline Integration

```text
1. Trigger on PR creation/update
2. Run pre-flight checks
3. If passes, run full review
4. Post inline comments for issues
5. Update PR status based on findings
```

---

## Best Practices Summary

1. **Use specialized agents** for different review aspects
2. **Scope to changed code** - avoid flagging pre-existing issues
3. **Require high confidence** - only report issues >= 80% confidence
4. **Add validation layer** - confirm issues before reporting
5. **Include exclusion lists** - explicitly state what NOT to flag
6. **Inject context** - pass PR info and relevant guidelines to all agents
7. **Use parallel execution** - for independent tasks
8. **Use redundancy** - multiple agents for important aspects
9. **Group by severity** - make findings actionable
10. **Include file:line references** - make issues locatable
11. **Match model to task** - use Opus for complex reasoning, Haiku for simple checks
12. **Provide committable suggestions** - for small, complete fixes only
