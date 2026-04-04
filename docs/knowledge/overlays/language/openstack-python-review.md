# OpenStack Python Review Overlay

This overlay captures reusable OpenStack Python review guidance that sits
between the canonical external references and the runtime review prompts.

## Purpose

Use this overlay when reviewing Python changes in OpenStack-style repositories.
It adds reusable review emphasis that is too specific for the canonical
references alone, but still broad enough to apply across multiple projects.

## Derived From

- `references/hacking.md`
- `references/pep8.md`
- `docs/quick-rules.md`
- `docs/comprehensive-guide.md`

## Review Emphasis

- Respect project-local overrides from `HACKING.rst`, `AGENTS.md`, and linter
  configuration before applying generic style feedback.
- Prefer behavioral, maintainability, and security findings over formatting
  issues already enforced by tooling.
- Treat examples and patterns as supporting evidence for review, not as
  standalone authority.
