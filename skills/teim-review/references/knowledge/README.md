# Derived Review Knowledge

This directory is the repository's internal review knowledge base.

It sits between the canonical external snapshots in `references/` and the
runtime review behavior encoded in the portable workflow, role prompts, and schemas.

## Purpose

Use this area to build and evolve:

- reusable overlays
- example-backed review guidance
- topic-specific review knowledge
- future RAG-oriented context for `teim-review`

## Structure

```text
references/knowledge/
  overlays/
    language/
    repo/
    topic/
  examples/
    good/
    bad/
```

## Usage Model

- `quick-rules.md` and `comprehensive-guide.md` remain curated baseline guides.
- Files here provide additional, more composable review knowledge.
- The reviewer and validator read applicable overlays and examples using the
  paths recorded by deterministic context preparation.
- Examples here are supporting evidence, not standalone authoritative rules.

## Authoritative Boundaries

- `references/` is canonical for external standards and policy snapshots.
- `references/knowledge/` is derived and constructed internal review knowledge.
- The skill workflow, role prompts, and `references/schemas/` define runtime
  behavior and contracts.
