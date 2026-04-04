# Repository Guidance

This repository packages an AI review system for OpenStack projects. The
primary product is the review workflow, not the legacy generic style-guide
documentation.

## What Is Authoritative

When changing review behavior, distinguish between knowledge tiers and runtime
contracts:

1. `references/` for canonical snapshots of external coding standards and
   policy
2. `docs/quick-rules.md`, `docs/comprehensive-guide.md`, and `docs/knowledge/`
   for curated baseline and derived internal review knowledge
3. `schemas/review-report-schema.json`, `agents/`, and `skills/` for runtime
   behavior and report contracts
4. `roles/`, `playbooks/`, `zuul.d/`, and `tools/` for execution glue

Do not update README or supporting docs to introduce runtime behavior that is
not encoded in the schema, agents, skills, or workflow glue.

## Runtime Contracts

Preserve these unless the change explicitly updates all dependent wiring and
tests in the same commit:

- plugin name `teim-review`
- marketplace identity `openstack-ai-style-guide`
- skill path `skills/teim-review/SKILL.md`
- orchestrator `agents/teim-review-agent.md`
- review schema `schemas/review-report-schema.json`
- local output directory `.teim-review/`
- Zuul jobs `teim-code-review` and `openstack-ai-style-guide-lint`

## Review-System Layout

```text
.claude-plugin/  plugin metadata and marketplace catalog
agents/          operational review intent and orchestration
skills/          interactive entrypoints
schemas/         structured output contracts
tools/           report transforms and validators
roles/           Ansible implementation units
playbooks/       workflow orchestration
zuul.d/          CI job definitions
docs/            active docs plus legacy support content
references/      canonical external standards snapshots
```

## Knowledge Areas

- `references/` contains canonical external source snapshots.
- `docs/quick-rules.md` and `docs/comprehensive-guide.md` are curated baseline
  guides distilled from references and internal review knowledge.
- `docs/knowledge/` is the growing internal knowledge base for overlays,
  examples, and retrieval-oriented review material.
- `docs/checklists/` and `docs/templates/` are archived/legacy support areas.

## Known Review Exceptions

### Plugin manifest defaults

`.claude-plugin/plugin.json` intentionally omits explicit `agents_dir` and
`skills_dir` fields because Claude Code auto-discovers the default layout.

### Ruff formatting

Python formatting issues that are enforced by ruff or pre-commit should not be
the focus of review findings. Review logic should prefer behavioral,
maintainability, and security issues.

### Embedded LiteLLM test credential

The hardcoded token in `zuul.d/jobs.yaml` is intentional for the internal test
environment. Do not flag it as a production secret leak.

## Testing Expectations

When changing the repo structure or wiring:

- keep helper-script unit tests green
- keep repo contract tests green
- update path references in jobs, roles, skills, and docs together
- keep the distinction between canonical references, derived knowledge, and
  runtime behavior explicit

Preferred local commands:

- `tox -e py3`
- `tox -e linters`

If `tox` is not installed locally, use `uvx tox ...` instead. `uvx` is the
preferred fallback for ad hoc verification in this repository.

When running multiple tox environments with `uvx tox`, use a comma-separated
env list in a single invocation, for example `uvx tox -e py3,linters`, rather
than launching multiple tox envs in parallel.

If a path move is intentional, update tests in the same change so the new
contract is explicit.
