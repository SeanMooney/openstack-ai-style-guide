# Teim Review Core Workflow

This file is the authoritative provider-neutral review workflow for this
repository. Tool-specific adapters may change invocation shape, packaging, and
model selection, but they must not redefine review behavior.

## Required Inputs

- `project_dir`: repository under review
- `output_dir`: directory for generated review artifacts
- `style_guide_quick_rules`: `docs/quick-rules.md`
- `style_guide_comprehensive`: `docs/comprehensive-guide.md`
- `finding_policy`: `prompts/teim-review-finding-policy.md`
- `knowledge_root`: `docs/knowledge/`
- `json_schema`: `schemas/review-report-schema.json`
- `candidate_findings_schema`: `schemas/candidate-findings-schema.json`
- `validated_findings_schema`: `schemas/validated-findings-schema.json`
- `tools_dir`: `tools/`
- Optional `changed_files_file`: newline-delimited files in the current patch
- Optional `changed_files_helper`: bundled skill helper script used to generate
  `changed_files_file`
- `execution_mode`: `local` or `zuul`
- Optional `inventory_file` for Zuul execution
- Optional scope hint: `base_branch`, `commit_sha`, or `uncommitted_only`

## Stable Outputs

Write all review artifacts into `output_dir`:

- `zuul-context.md`
- `commit-summary.md`
- `project-guidelines.md`
- `review-context.json`
- `changed-files.txt` when a tool adapter can provide patch scope
- `candidate-findings.json`
- `validated-findings.json`
- `validated-findings.raw.json` when a tool adapter captures raw structured
  output from Claude
- `review-report.raw.json` after deterministic report assembly
- `review-validation.json` when deterministic normalization runs
- `review-report.json`
- `review-report.html` when HTML generation is enabled

`review-report.json` must conform to `json_schema`.

## Workflow

1. Create `output_dir` if it does not exist.
2. Determine execution context:
   - In Zuul mode, use `inventory_file` when provided.
   - In local mode, inspect the git repository directly.
3. Generate `changed-files.txt` with the bundled deterministic skill helper
   when patch scope is available, then use that file as `changed_files_file`:
   - Zuul mode: use the helper default patchset scope.
   - `uncommitted_only`: pass `--uncommitted-only`.
   - `base_branch`: pass `--base-ref <base_branch>`.
   - Root commits: pass `--allow-root-commit` only when all tracked files are
     intentionally in scope.
4. Generate prepared context artifacts deterministically:
   - Zuul mode: summarize the inventory and execution context.
   - Local mode: summarize repository path, branch, status, and review scope.
   - Write `zuul-context.md`, `commit-summary.md`,
     `project-guidelines.md`, and `review-context.json`.
   - Include explicit full-context paths for the source repo, quick rules,
     comprehensive guide, finding policy, schemas, and knowledge root.
5. Generate `commit-summary.md` deterministically:
   - Use the requested review scope when one is provided.
   - Otherwise summarize the most relevant recent local changes.
6. Generate `project-guidelines.md` deterministically:
   - Read `AGENTS.md`, `HACKING.rst`, `CLAUDE.md` when present.
   - Apply `docs/knowledge/` overlays and examples when relevant.
7. Invoke the review orchestrator once for model reasoning. It must not invoke
   deterministic extraction subagents. It generates candidate findings with
   the code review agent using:
   - `zuul-context.md`
   - `commit-summary.md`
   - `project-guidelines.md`
   - `changed-files.txt`
   - `style_guide_quick_rules`
   - `style_guide_comprehensive`
   - `finding_policy`
8. The same orchestrator validates candidate findings with the finding
   validation agent using the same context. The validation pass assigns
   severity and confidence, drops weak candidates, writes
   `validated-findings.json`, and returns structured output conforming to
   `validated_findings_schema`.
9. Build `review-report.raw.json` deterministically from validated findings:
   - anchors inline issue locations only to files in the current patch
   - describes cross-file impacts on the changed file that caused the behavior
   - separates pre-existing out-of-patch observations from in-scope findings
   - prioritizes behavioral, maintainability, and security issues
   - avoids style-only noise that is already enforced mechanically
10. Run deterministic normalization when available to recalculate routing and
    statistics, filter unsafe inline comments, and write `review-validation.json`.
11. When HTML generation is requested, render `review-report.html` from the
   structured JSON report via `tools/render_html_from_json.py`.

## Review Policy

- Keep findings concise without sacrificing necessary evidence or actionable
  guidance. As writing targets, keep titles to one line within 120 characters,
  descriptions, impacts, recommendations, and validation rationale within 800
  characters, and evidence within 1500 characters. These are advisory targets,
  not hard limits: exceed them when needed, and never truncate a complete
  finding to satisfy them.
- Treat project-specific guidance as authoritative overrides of generic
  OpenStack guidance.
- Prefer behavioral regressions, correctness risks, maintainability issues, and
  security issues over formatting-only findings.
- Keep hardcoded internal test credentials and other documented exceptions out
  of findings when repository guidance marks them intentional.
- Put pre-existing observations outside the patch in
  `out_of_patch_observations`, not in `issues`.
- If changed code in one file affects behavior in an unmodified file, report the
  finding as an inline issue on the changed file and explain the unmodified file
  impact in the issue text.
- Put in-scope findings that cannot be safely anchored to a changed file in
  `patch_level_observations`.

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
