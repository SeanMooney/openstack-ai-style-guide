# Teim Review Finding Policy

This file is the shared finding policy for the teim-review pipeline.
`code-review-agent` and `finding-validation-agent` must both follow this
policy so candidate generation and validation use the same review standards.

The policy defines what is worth surfacing as a finding, how to classify it,
and what to skip. It does not define final publication routing. Deterministic
tooling owns `reporting_mode`, statistics, HTML-only routing, and Zuul inline
comment safety.

## Project Guidance Precedence

Project-specific guidance is authoritative over generic OpenStack guidance.
Read and apply supplied `HACKING.rst`, `AGENTS.md`, `CLAUDE.md`,
`project-guidelines.md`, and configured linter behavior before evaluating
findings.

When project guidance says not to report a class of issue, do not report it.
When project guidance documents an intentional exception, treat that exception
as binding.

Distinguish between:

- **New files**: apply current project and OpenStack practices strictly.
- **Existing files being modified**: preserve local patterns unless the change
  introduces a real bug or clear rule violation.
- **Substantial refactors**: apply current best practices.
- **Minor changes**: do not force unrelated cleanup.

## Review Criteria

Evaluate changes across these dimensions:

- **Correctness**: wrong results, missing imports, undefined names, broken state
  transitions, missing critical error handling, data loss, or behavior that
  does not match the stated intent.
- **Compatibility and API behavior**: user-visible behavior changes, API
  compatibility breaks, upgrade-impacting changes, versioning problems, or
  missing release-note context when required.
- **Security**: concrete vulnerabilities introduced by the patch, using the
  security framework below.
- **Testing**: missing or weak tests for changed behavior, incorrect mocks,
  missing edge-case coverage, or tests that no longer assert the behavior under
  review.
- **Maintainability**: complexity, duplication, dead code, naming, or structure
  concerns only when they create meaningful maintenance risk.
- **Documentation**: missing or misleading documentation when the change alters
  user-visible behavior, APIs, configuration, operations, or upgrade behavior.
- **Project standards**: clear violations of HACKING.rst, AGENTS.md,
  CLAUDE.md, or supplied project guidance.

Do not spend review budget on routine formatting. If ruff, flake8,
pre-commit, or another mechanical checker is expected to catch an issue, do
not make it a finding unless project guidance explicitly says reviewers should
still flag it.

## Commit Message And AI Attribution

Review commit-message issues as change-level concerns, not line-anchored code
findings.

Only flag missing AI attribution when there is explicit evidence that AI tools
were used, such as:

- commit message text mentioning AI, Claude, Copilot, ChatGPT, LLM,
  generated, or assisted work
- code comments referencing AI generation
- commit body explicitly describing AI tool use

Do not infer AI use from patch size, formatting quality, or routine code
patterns alone. Default to assuming changes are human-written unless evidence
shows otherwise.

## Security Decision Framework

Only create or accept a security finding when all three questions are answered
with concrete evidence:

```text
1. Is there untrusted input?
2. Does it reach a sensitive operation?
3. Is sanitization missing or weak?
```

High-signal security patterns include:

- SQL queries built with string concatenation and user-controlled input
- command execution with user-controlled parameters
- authentication bypass or privilege escalation
- deserialization of untrusted data
- file operations with user-controlled paths

Do not flag these as security findings without a concrete exploit path:

- rate limiting, DOS protection, or resource exhaustion concerns
- secrets passed through environment variables or CLI flags
- UUID identifiers needing brute-force protection
- URLs or config paths in log output
- client-side authorization checks when backend enforcement is outside the diff
- regex injection, SSRF with a hardcoded host, AI prompt injection
- outdated dependencies managed by dependency tooling

Treat logging secrets or PII as a real issue. Treat logging URLs as safe unless
the URL contains sensitive tokens.

## High-Signal Rules

Create or accept a finding only when at least one of these is true:

- The changed code will clearly fail or produce wrong results.
- The change creates a concrete security, data-integrity, or compatibility
  risk.
- The change clearly violates a project rule that can be cited from supplied
  guidance.
- The issue is directly actionable by the patch author in this review.

Do not create or accept findings for:

- pre-existing issues unrelated to the current change
- speculative problems that depend on unknown runtime state
- subjective refactors or preferences that were not requested
- small duplications or trivially parallel code
- apparent dead code in dynamic plugin, stevedore, entry point, reflection, or
  `importlib` paths unless the diff proves it is unreachable
- type hints in projects that do not already use type annotations
- deprecation timelines or roadmap choices requiring team consensus
- performance tuning for one-shot CI/devstack/tooling scripts where
  performance is not material
- idempotency, rollback, or production-grade error handling in one-shot scripts
- style or quality concerns that linting already enforces

If you are not confident a concern is real, leave it out. False positives erode
trust and reduce the value of the review.

## Severity

Assign one severity to each finding:

- `critical`: security vulnerability, policy violation, data corruption,
  severe compatibility break, test failure, or other merge-blocking risk.
- `high`: important correctness, compatibility, security, performance, or
  testing issue that should be fixed before merge.
- `warnings`: actionable issue with moderate impact.
- `suggestions`: useful improvement with clear benefit and low risk.

Findings that need team consensus, roadmap decisions, or broad style
preference should normally be rejected rather than downgraded.

## Confidence

Assign confidence as a decimal from `0.0` through `1.0`:

- `0.90`-`1.0`: directly verifiable from code or explicit project guidance
- `0.80`-`0.89`: strong evidence with little uncertainty
- `0.70`-`0.79`: good evidence with contextual uncertainty
- `0.60`-`0.69`: moderate evidence; keep only for serious issues
- `0.0`-`0.59`: speculative or low confidence; preserve only when the
  uncertainty itself is useful to the validation pass

Do not clamp confidence upward to satisfy a reporting threshold. Validation and
deterministic tooling drop findings that do not meet severity-specific
thresholds.

## Anchors

Assign one `anchor_kind` to each finding:

- `changed_line`: the finding has a safe changed-file line anchor.
- `patch_level`: the finding is in scope for the change but has no safe
  changed-line anchor.
- `out_of_patch`: the finding is a relevant observation in unmodified code.

If changed code in one file affects behavior in an unmodified file, prefer
`changed_line` on the changed code that caused the behavior and explain the
downstream impact in the finding text.

Do not decide whether a finding is inline or HTML-only. Deterministic tooling
will calculate `reporting_mode` from severity, confidence, and changed scope.

## Quality Pass

Before emitting or accepting findings:

1. Confirm the finding is related to the current change or explicitly marked as
   a relevant out-of-patch observation.
2. Re-read the cited code and rule. If evidence is missing, drop it.
3. Ask whether a senior OpenStack reviewer would raise it in review.
4. Confirm the recommendation is specific and feasible.
5. Remove duplicates and combine closely related observations.
