# Contributing

This repository is maintained as an AI review system for OpenStack-oriented
projects. Contributions should improve one of these areas:

- review behavior in `agents/` and `skills/`
- structured output contracts in `schemas/`
- CI/runtime wiring in `roles/`, `playbooks/`, and `zuul.d/`
- helper transforms in `tools/`
- supporting docs and references that explain the active workflow

## Contribution Priorities

### High priority

- better review quality and lower false positives
- clearer orchestration and runtime contracts
- reduced duplication across prompts, docs, and workflow glue
- stronger tests for plugin, skill, schema, and Zuul wiring

### Lower priority

- expanding legacy generic style-guide content
- adding more checklists or templates unless they support a live workflow

## Source of Truth

Use this precedence order when making changes:

1. `schemas/review-report-schema.json`
2. `agents/`
3. `skills/`
4. `roles/`, `playbooks/`, `zuul.d/`, `tools/`
5. `docs/` and `references/`

If behavior changes, encode it in the schema or agent prompts first.

## Compatibility Rules

This repository currently preserves these entrypoints:

- `teim-review@openstack-ai-style-guide`
- `/teim-review`
- `agents/teim-review-agent.md`
- `schemas/review-report-schema.json`
- `teim-code-review`

Do not rename or move them without updating all dependent wiring and tests in
the same change.

## Legacy Material

`docs/checklists/`, `docs/examples/`, and `docs/templates/` are retained for
compatibility and reference. They are not the primary product surface. Avoid
adding new authoritative rules there.

## Testing

Preferred checks:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
tox -e py3
tox -e linters
```

If `tox` is unavailable, run the unit tests directly and note the gap.

## AI Attribution

AI-assisted contributions must still be reviewed by a human and attributed in
the commit message according to the OpenInfra AI policy.

Typical footer lines:

```text
Generated-By: claude-code
Signed-off-by: Your Name <your.email@example.com>
```
