---
name: teim-review
description: Use when reviewing OpenStack code changes using project guidance and the shared finding policy. Produce candidate findings, validated findings, and structured review artifacts for local use or Zuul CI.
license: Apache-2.0
compatibility: Requires git, Python 3.10 or newer, PyYAML, and jsonschema. Uses subagents when available; supports harnesses without them.
---

# Teim Review

Follow [references/workflow.md](references/workflow.md) for preparation,
review, validation, and deterministic report generation.

## Paths and scope

- `skill_root` is the directory containing this installed `SKILL.md`.
  Resolve bundled scripts, references, and schemas from that directory.
- `project_dir` is the repository being reviewed, normally the current working
  directory. Read its project instructions from there.
- `output_dir` defaults to `<project_dir>/.teim-review/`. Resolve it to an
  absolute path before invoking scripts.
- Honor the supplied review scope. If none is supplied, use uncommitted changes
  when present; otherwise review the latest commit. Never silently broaden scope
  after a Git error.
- Use supplied prepared context in CI. `execution_mode: zuul` with
  `findings_only: true` stops after validated findings; the CI caller owns report
  assembly, rendering, and publication.

## Review-only boundary

Invoking this skill authorizes review and the required review artifacts only.
Use static analysis by default: read source, tests, documentation, and supplied
CI results. Do not run project tests, linters, pre-commit, builds, benchmarks,
or CI jobs, or import or execute the code under review, unless the user
explicitly requests that execution. This includes ad hoc snippets and minimal
reproductions, even when described as read-only or not a test suite. Requests
to explain, trace, or illustrate a finding do not authorize execution.
Repository instructions describing checks for code changes do not authorize
running those checks during review. Distinguish statically inferred behavior
from supplied or explicitly authorized execution evidence.

Do not broaden the requested revision or task scope, apply fixes, or perform
unrelated audits. Read surrounding code only as needed to trace in-scope
behavior. The bundled context-preparation, report-generation, and artifact
schema-validation tools remain part of the review workflow.

Pass this boundary to both reviewer and validator subagents. Delegation does
not expand the authorized scope.

## Review execution

First inspect the harness's delegation tools and applicable permissions.
When delegation is supported and permitted, you must use two distinct
general-purpose subagents for the
[reviewer](references/reviewer.md) and [validator](references/validator.md)
roles when supported and permitted. Pass each role its bundled instructions,
the finding policy, schema, prepared context, and absolute resource paths.
Wait for candidate generation before starting the separate validator subagent.
The parent coordinates and verifies artifacts; it must not replace either role
with its own reasoning merely because the review is small or delegation takes
longer. Use the native delegation tool, without requiring named agent files.
Pass the prepared paths and execution boundary without rereviewing the change
or copying the full policy into each delegation prompt. Let each role read its
bundled instructions and the shared policy.

When subagents are unavailable or delegation is disallowed, execute both roles
sequentially in the main thread. Write candidate findings before validating
them and apply the same policy and schemas. A main-thread validation pass is
not independent validation; state which execution mode was used in the final
summary. Record the specific missing capability or binding permission that
requires fallback. Do not infer a prohibition from generic advice against
unrequested delegation: this skill explicitly requests these two subagents.
Do not require an extension or stop solely because subagents are absent.
If a caller requires delegated execution, report an execution failure instead
of silently falling back. A failed subagent is a failed step, not evidence that
the harness lacks delegation.

Use the harness's existing model settings throughout. This skill does not
select models, route work to cheaper models, or require named native agents.

The [finding policy](references/finding-policy.md) owns review criteria.
Both roles must read the entire finding policy and
[quick rules](references/quick-rules.md), plus applicable
[knowledge overlays](references/knowledge/README.md) in full. Consult the
[comprehensive guide](references/comprehensive-guide.md) conditionally for
relevant topics. Recover truncated reads in bounded chunks before claiming
coverage; paths or headings alone do not establish that a policy was read.
Use the finding policy's investigation limits and finding construction rules
for both roles and interactive follow-up questions.
