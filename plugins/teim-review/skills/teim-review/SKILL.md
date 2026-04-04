---
name: teim-review
description: Use when the user wants a full OpenStack code review in Codex
  using the repository's shared review core and `.teim-review/` outputs.
---

# Teim Review

This skill provides the Codex-native adapter for the repository's shared review
workflow.

## Use

- Invoke this skill with `$teim-review` or discover it via `/skills`.
- Follow the authoritative workflow in
  [`../../references/teim-review-core.md`](../../references/teim-review-core.md).
- Use the shared model profile mapping in
  [`../../references/tool-profiles.json`](../../references/tool-profiles.json).
- Keep the stable output contract:
  - `.teim-review/zuul-context.md`
  - `.teim-review/commit-summary.md`
  - `.teim-review/project-guidelines.md`
  - `.teim-review/review-report.json`
  - `.teim-review/review-report.html`

## Interactive Codex Path

- Generate the context artifacts first using the lightweight Codex context
  model from `tool-profiles.json`.
- Keep the final structured review in the current Codex session model rather
  than downgrading it to the lightweight context model.
- Write all outputs into `.teim-review/`.
- Use this installed plugin for the interactive `$teim-review` flow only.
- If you want to inspect or modify the shared workflow implementation, work
  from a checkout of the repository rather than assuming the installed plugin
  bundle ships repo-local helper scripts.
