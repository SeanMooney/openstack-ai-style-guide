# Teim Review Workflow

This is the authoritative provider-neutral review workflow. All paths below
are relative to `skill_root`, the directory containing `SKILL.md`, unless an
absolute path is supplied. The target repository is a separate `project_dir`.

## Inputs

- `project_dir`, `output_dir`, and the requested review scope.
- Optional `execution_mode`: `local` (default) or `zuul`.
- Optional `inventory_file` for Zuul context.
- Optional prepared context paths: `zuul_context_file`, `commit_summary_file`,
  `project_guidelines_file`, `review_context_file`, and `changed_files_file`.
- Optional resource overrides: `style_guide_quick_rules`,
  `style_guide_comprehensive`, `finding_policy`, `knowledge_root`,
  `candidate_findings_schema`, `validated_findings_schema`, and `json_schema`.
  Defaults are the corresponding bundled references and schemas.
- Optional `candidate_findings_file` and `validated_findings_file`; defaults
  are the corresponding files under `output_dir`.
- Optional `findings_only` (default false) and `generate_html` (default true).

Resolve all paths to absolute paths. Keep the target repository and installed
skill resources distinct. Install required Python dependencies in an available
environment; do not substitute model-authored context for deterministic tools.
Use an interpreter with the skill's dependencies, including PyYAML and
`jsonschema`, for the helper scripts and artifact checks. Record its absolute
path and pass it to both roles. The `python3` commands below assume that
interpreter; substitute its path when necessary. Do not write replacement
schema validators when an interpreter lacks a dependency; use or provision a
skill environment within the harness permissions, or report the setup failure.
This tooling permission does not authorize installing the reviewed project's
dependencies to execute it.

## 1. Prepare scope and context

Create `output_dir`. If the caller supplies prepared context, verify and use it.
Missing supplied artifacts are errors; do not silently use a different scope.
Otherwise use the bundled scripts below. Commands show shell variables for
absolute `SKILL_ROOT`, `PROJECT_DIR`, and `OUTPUT_DIR`; quote their values.

Generate the changed file list:

```bash
python3 "$SKILL_ROOT/scripts/detect_changed_files.py" "$PROJECT_DIR" \
  --output "$OUTPUT_DIR/changed-files.txt"
```

- Default/latest-commit review uses the command above.
- Uncommitted review adds `--uncommitted-only` (staged, unstaged, and untracked).
- Branch review adds `--base-ref <branch>`. Resolve its merge-base with HEAD
  and use that same resolved base for context preparation.
- For a named commit, inspect that revision in a separate worktree and run the
  latest-commit flow there. Do not move the user's checkout or review HEAD as a
  substitute. Keep the requested output directory absolute.
- For incremental patchset reviews, CI can generate changed-line scope with
  `scripts/detect_changed_lines.py` using `--ref1`, `--ref2`, and `--output`.
  Pass that file as `--changed-lines` to normalization when available.
- Root commits require `--allow-root-commit` only when all tracked files are
  intentionally in scope. Report missing history rather than broadening scope.

Prepare the context (append `--inventory-file <absolute-path>` for Zuul, and
`--review-base <resolved-base> --scope-mode branch` for branch review):

```bash
python3 "$SKILL_ROOT/scripts/prepare_review_artifacts.py" \
  --project-dir "$PROJECT_DIR" --output-dir "$OUTPUT_DIR" \
  --changed-files "$OUTPUT_DIR/changed-files.txt" \
  --quick-rules "$SKILL_ROOT/references/quick-rules.md" \
  --comprehensive-guide "$SKILL_ROOT/references/comprehensive-guide.md" \
  --finding-policy "$SKILL_ROOT/references/finding-policy.md" \
  --knowledge-root "$SKILL_ROOT/references/knowledge" \
  --candidate-schema "$SKILL_ROOT/references/schemas/candidate-findings-schema.json" \
  --validated-schema "$SKILL_ROOT/references/schemas/validated-findings-schema.json"
```

Substitute resource overrides when supplied. The tool writes `zuul-context.md`,
`commit-summary.md`, `project-guidelines.md`, and `review-context.json`.
Read these artifacts and the target project's applicable instructions.
For uncommitted reviews, use the changed-files list, worktree diff, and
untracked file contents as the review scope; historical commit summaries are
background context only.

## 2. Generate candidates

Execute `references/reviewer.md` once, in a supported subagent or the main
thread as described in `SKILL.md`. Supply:

- The prepared context and changed-file list.
- The requested revision or worktree scope and `project_dir`.
- Absolute paths to the finding policy, coding guidance, relevant knowledge,
  `references/schemas/candidate-findings-schema.json`, and candidate output file.
- The review-only execution boundary and the interpreter path for artifact
  tooling. Reference the bundled policy rather than copying it into the prompt.

The parent verifies prepared inputs and coordinates the roles; candidate
investigation belongs to the reviewer. Use the shared policy's investigation
limits rather than performing a preliminary full review in the parent.

Write `candidate-findings.json`, including an empty findings list when there
are no candidates. Verify it exists and conforms to the candidate schema before
starting validation. Do not generate findings in parallel with validation.
Require the finding policy's coverage statement in `context.review_basis`.
Confirm both roles read the full shared policy and quick rules, recovering
truncated reads; an empty candidate list does not waive those reads.

## 3. Validate findings

Execute `references/validator.md` once with the candidates and the same context,
scope, and guidance. Write `validated-findings.json` conforming to
`references/schemas/validated-findings-schema.json`. The validator may reject or revise
candidates but must not introduce new findings.

Validate both artifacts with Python's `jsonschema` library and the supplied
schemas using the selected interpreter. The parent owns these deterministic
checks; the roles produce findings rather than devising validation tools.
Do not proceed with invalid artifacts or replace an unsuccessful review with
an empty successful report.

If `findings_only` is true, return the validated findings object as the final
response and stop here. Also write both findings artifacts. This lets CI own
structured-output envelopes, report assembly, rendering, and publication.

## 4. Assemble, normalize, and render

For full local reviews, use deterministic tooling:

```bash
python3 "$SKILL_ROOT/scripts/build_review_report.py" \
  --validated-findings "$OUTPUT_DIR/validated-findings.json" \
  --review-context "$OUTPUT_DIR/review-context.json" \
  --output "$OUTPUT_DIR/review-report.raw.json"
python3 "$SKILL_ROOT/scripts/normalize_review_report.py" \
  --raw-report "$OUTPUT_DIR/review-report.raw.json" \
  --project-dir "$PROJECT_DIR" \
  --candidate-findings "$OUTPUT_DIR/candidate-findings.json" \
  --validated-findings "$OUTPUT_DIR/validated-findings.json" \
  --schema "$SKILL_ROOT/references/schemas/review-report-schema.json" \
  --changed-files "$OUTPUT_DIR/changed-files.txt" \
  --output "$OUTPUT_DIR/review-report.json" \
  --diagnostics "$OUTPUT_DIR/review-validation.json"
```

Honor supplied artifact paths and schema overrides. Validate the final report
against `json_schema`. Deleted files remain in review scope, but a finding
anchored to a path absent from `project_dir` is retained as HTML-only rather
than published inline. `/COMMIT_MSG` remains a supported synthetic anchor.
Normalization requires `--validated-findings`: the validator role's output
must exist and pass its schema even when both findings lists are empty. A
missing, invalid, or failed validator result is an execution failure, not an
optional diagnostic artifact. Both review roles must complete before report
assembly; an empty review never skips the validator role.
When HTML is requested:

```bash
python3 "$SKILL_ROOT/scripts/render_html_from_json.py" \
  "$OUTPUT_DIR/review-report.json" "$OUTPUT_DIR/review-report.html" \
  --schema "$SKILL_ROOT/references/schemas/review-report-schema.json"
```

Report generation owns routing and statistics. The finding policy owns review
criteria, severity, confidence, and safe anchors. Do not duplicate or weaken it.
Publication to external services remains the caller's responsibility.

## Completion

For a full review, summarize the scope, accepted/rejected finding counts,
artifact paths, and whether review used subagents or the main thread. State
missing context or failed steps that limit the result. Do not claim independent
validation when both passes ran in the main thread.
For zero candidates, explicitly distinguish completed candidate generation from
an incomplete or failed review, and state that validation had no individual
claims to check. Report coverage and evidence limits, rather than treating an
empty list as proof of correctness or approval to merge. Report assembly must
retain this coverage statement for the HTML report as well as the final reply.
Use `No findings` for a valid review with no accepted findings, retaining the
distinction between zero candidates and all candidates rejected in the summary.
Use `No retained findings` when publication filtering removed the findings;
never infer completed review coverage from that label. Missing completion
evidence must remain explicit as `Incomplete` or an execution failure.
Identify the reviewer and validator subagents when delegated, or the specific
capability or permission that required main-thread fallback. A supported and
permitted delegation tool must be used for both roles.

## Interactive follow-up

Apply the finding policy's challenge-handling rules when a user questions a
finding. Answer the disputed premise directly, revisiting only the necessary
evidence. An explanation or example request retains the static-analysis
boundary. Provide a concise, paste-ready comment when requested, with a minimal
input example where useful and any material scope qualification preserved.
If a reassessment changes an accepted finding or its disposition, update the
candidate and validated artifacts as appropriate and regenerate any reports
already produced so the saved review agrees with the corrected conclusion.
