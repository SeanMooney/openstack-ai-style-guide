# Contributing

This repository is maintained as an AI review system for OpenStack-oriented
projects. Contributions should improve one of these areas:

- portable review behavior in `skills/teim-review/`
- distribution metadata in native plugin and marketplace files
- structured output contracts in `skills/teim-review/references/schemas/`
- CI/runtime wiring in `roles/`, `playbooks/`, and `zuul.d/`
- helper transforms in `skills/teim-review/scripts/`
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

Review behavior belongs in `skills/teim-review/`: schemas define artifact
shape, the finding policy defines reportable issues, the workflow defines
sequencing, and role prompts define candidate generation and validation.
Supporting prose must describe that implementation. Keep resources inside the
skill so direct installation includes everything required at runtime.

Skillsaw is pinned in `.pre-commit-config.yaml` and runs in the normal lint
environment. Keep the common skill layout (`scripts/`, `references/`, and
optional `assets/`); place schemas under `references/schemas/`. Fix structural
errors without introducing a baseline or suppressing new package findings.

Maintain one definition per skill and one set of teim-review role prompts. Do not add tool-specific
copies or model profiles. Model selection belongs to the harness or CI.
Subagents are optional; preserve the sequential main-thread fallback.
Keep security and maintainability audits explicit-only in both frontmatter
and `agents/openai.yaml`. Document conversion retains tool/model discovery.

## Compatibility Rules

This repository currently preserves these entrypoints:

- `teim-review@openstack-ai-style-guide`
- Claude: `/teim-review`
- Codex: `$teim-review`
- `skills/teim-review/SKILL.md`
- `skills/teim-review/references/schemas/review-report-schema.json`
- `teim-code-review`

Do not rename or move them without updating all dependent wiring and tests in
the same change.

## Testing

Preferred checks:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
tox -e py3
tox -e linters
```

If `tox` is unavailable, use `uvx tox -e py3,linters`.

## AI Attribution

AI-assisted contributions must still be reviewed by a human and attributed in
the commit message according to the OpenInfra AI policy.

Typical footer lines:

```text
Generated-By: claude-code
Signed-off-by: Your Name <your.email@example.com>
```
