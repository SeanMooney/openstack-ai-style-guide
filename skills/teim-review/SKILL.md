---
description: >-
  Run a full AI-powered OpenStack code review on the current repository.
  Automatically detects Zuul CI context or uses local git history.
  Orchestrates context extraction, commit analysis, project guidelines
  extraction, and code review in a single pass. Writes results to
  .teim-review/ in the current directory.
disable-model-invocation: false
---

Use the @teim-review-agent subagent to perform a complete code review.

The authoritative shared workflow is
`prompts/teim-review-core.md`. This skill is the Claude-native adapter for that
workflow.

- **Output directory**: `.teim-review/` (relative to the current working
  directory)
- **Project directory**: current working directory
- **Context detection**: check whether `ZUUL_CHANGE` is set; if so, operate
  in Zuul CI mode; otherwise use local git context
- **Changed files**: generate `.teim-review/changed-files.txt` by invoking the
  bundled deterministic helper
  `skills/teim-review/scripts/detect_changed_files.py`. In Zuul mode use the
  helper default; in local uncommitted review pass `--uncommitted-only`; when a
  base branch is selected pass `--base-ref`; pass `--allow-root-commit` only
  when intentionally treating all tracked files as changed.
- **Generate HTML**: yes — write `.teim-review/review-report.html`
- **Intermediate review artifacts**: write `.teim-review/candidate-findings.json`
  and `.teim-review/validated-findings.json` before producing the final report
- **Deterministic validation**: normalize the raw structured report into
  `.teim-review/review-report.json` and write diagnostics to
  `.teim-review/review-validation.json` when the normalizer is available
- **Style guide**: use `./docs/quick-rules.md` and
  `./docs/comprehensive-guide.md` from the current repo
- **Finding policy**: use `./prompts/teim-review-finding-policy.md`
- **Knowledge root**: use `./docs/knowledge/` from the current repo for
  overlays and example-backed review context
- **JSON schema**: `schemas/review-report-schema.json` (relative to the plugin root)
- **Intermediate schemas**: `schemas/candidate-findings-schema.json` and
  `schemas/validated-findings-schema.json`
- **Semantic profiles**: `config/tool-profiles.json` defines shared `fast` and
  `deep` aliases across tools
