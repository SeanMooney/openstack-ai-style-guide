# Archived and Legacy Support Material

This repository retains some directories from its earlier life as a generic
AI style-guide project. They are kept for compatibility and reference, but they
are not the authoritative runtime surface of the review system.

## Current Status

### Active runtime surface

- `.claude-plugin/`
- `agents/`
- `skills/`
- `schemas/`
- `tools/`
- `roles/`
- `playbooks/`
- `zuul.d/`

### Baseline and derived knowledge

- `docs/quick-rules.md`
- `docs/comprehensive-guide.md`
- `docs/knowledge/`
- `references/`

### Archived support material

- `docs/checklists/`
- `docs/templates/`
- older style-guide-first prose in contributor documentation

## How To Treat Legacy Material

- Do not make legacy docs the source of truth for review behavior.
- Do not duplicate agent or schema rules into legacy areas.
- Prefer updating `agents/`, `skills/`, and `schemas/` first.
- Trim or relocate legacy content when it no longer supports a live workflow.

## Compatibility Note

Some active prompts still reference `docs/quick-rules.md` and
`docs/comprehensive-guide.md` directly. The new `docs/knowledge/` layer is
intended to grow alongside those guides and start feeding review context
through the guideline extraction path.
