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

- **Output directory**: `.teim-review/` (relative to the current working
  directory)
- **Project directory**: current working directory
- **Context detection**: check whether `ZUUL_CHANGE` is set; if so, operate
  in Zuul CI mode; otherwise use local git context
- **Generate HTML**: yes — write `.teim-review/review-report.html`
- **Style guide**: use `./docs/quick-rules.md` and
  `./docs/comprehensive-guide.md` from the current repo
- **JSON schema**: `schemas/review-report-schema.json` (relative to the plugin root)
