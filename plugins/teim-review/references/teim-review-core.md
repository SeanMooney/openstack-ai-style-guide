# Teim Review Core Workflow

This file is the authoritative provider-neutral review workflow for this
repository. Tool-specific adapters may change invocation shape, packaging, and
model selection, but they must not redefine review behavior.

## Required Inputs

- `project_dir`: repository under review
- `output_dir`: directory for generated review artifacts
- `style_guide_quick_rules`: `docs/quick-rules.md`
- `style_guide_comprehensive`: `docs/comprehensive-guide.md`
- `knowledge_root`: `docs/knowledge/`
- `json_schema`: `schemas/review-report-schema.json`
- `tools_dir`: `tools/`
- `execution_mode`: `local` or `zuul`
- Optional `inventory_file` for Zuul execution
- Optional scope hint: `base_branch`, `commit_sha`, or `uncommitted_only`

## Stable Outputs

Write all review artifacts into `output_dir`:

- `zuul-context.md`
- `commit-summary.md`
- `project-guidelines.md`
- `review-report.json`
- `review-report.html` when HTML generation is enabled

`review-report.json` must conform to `json_schema`.

## Workflow

1. Create `output_dir` if it does not exist.
2. Determine execution context:
   - In Zuul mode, use `inventory_file` when provided.
   - In local mode, inspect the git repository directly.
3. Generate `zuul-context.md`:
   - Zuul mode: summarize the inventory and execution context.
   - Local mode: summarize repository path, branch, status, and review scope.
4. Generate `commit-summary.md`:
   - Use the requested review scope when one is provided.
   - Otherwise summarize the most relevant recent local changes.
5. Generate `project-guidelines.md`:
   - Read `AGENTS.md`, `HACKING.rst`, `CLAUDE.md` when present.
   - Apply `docs/knowledge/` overlays and examples when relevant.
6. Review the code in `project_dir` using:
   - `zuul-context.md`
   - `commit-summary.md`
   - `project-guidelines.md`
   - `style_guide_quick_rules`
   - `style_guide_comprehensive`
7. Produce a structured review report that:
   - separates in-patch findings from out-of-patch observations
   - prioritizes behavioral, maintainability, and security issues
   - avoids style-only noise that is already enforced mechanically
8. When HTML generation is requested, render `review-report.html` from the
   structured JSON report via `tools/render_html_from_json.py`.

## Review Policy

- Treat project-specific guidance as authoritative overrides of generic
  OpenStack guidance.
- Prefer behavioral regressions, correctness risks, maintainability issues, and
  security issues over formatting-only findings.
- Keep hardcoded internal test credentials and other documented exceptions out
  of findings when repository guidance marks them intentional.
- Put observations outside the patch in `out_of_patch_observations`, not in
  `issues`.

## Local Review Scope

When a tool adapter provides an explicit scope hint, apply it consistently:

- `uncommitted_only`: review staged, unstaged, and untracked changes
- `base_branch`: review the current branch against the named base branch
- `commit_sha`: review the named commit

If no scope hint is provided, review the current local change context using the
most relevant git history and worktree state.

## Tool Adapter Rules

Adapters may choose different native delivery mechanisms:

- Claude: plugin marketplace, agents, and skills
- Codex: plugins and skills
- Cursor: project rules and custom modes

Adapters may also choose different tool-native models for the semantic
profiles `fast` and `deep`, but the workflow and outputs above must remain the
same.
