# Repository Guidance

This repository packages an AI review system for OpenStack projects. The
primary product is the review workflow, not the legacy generic style-guide
documentation.

## What Is Authoritative

- `references/` contains canonical external policy snapshots.
- `skills/teim-review/` is the single portable review package:
  - `SKILL.md` is the entrypoint.
  - `references/workflow.md` owns orchestration.
  - `references/finding-policy.md` owns finding admission and quality.
  - `references/reviewer.md` and `references/validator.md` define review roles.
  - `references/quick-rules.md`, `references/comprehensive-guide.md`, and
    `references/knowledge/` contain curated coding guidance.
  - `references/schemas/` owns output contracts; `scripts/` owns deterministic processing.
- Root `plugin.json` targets published Agent Plugins 1.0.0.
- `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`,
  `.agents/plugins/`, and `package.json` contain distribution metadata.
- `roles/`, `playbooks/`, and `zuul.d/` integrate the same skill with CI.
- `skills/security-auditor/` and `skills/code-maintainability-auditor/` are
  explicit-only standalone audits. Preserve both their frontmatter invocation
  flag and `agents/openai.yaml` policy.
- `skills/doc-to-markdown/` is discoverable by tools and documentation workflows.
- Standalone skills are siblings of teim-review, not extra stages in its CI flow.
  There is no native standalone agent directory or agent discovery alias.

## Runtime Contracts

Preserve these unless all dependent wiring and tests change together:

- plugin name `teim-review` and marketplace `openstack-ai-style-guide`
- entrypoint `skills/teim-review/SKILL.md`
- local output directory `.teim-review/` and existing artifact filenames
- published schema identifiers and report shape
- Zuul job `teim-code-review`

## Portability

Maintain one definition per skill and one set of teim-review role prompts. Do not add manually
maintained tool-specific copies, model profiles, or named-agent requirements.
Plugin manifests may expose the shared `skills/` tree. Keep bundled resource
links inside the skill so a copied installation works outside this checkout.
Resolve target project instructions from `project_dir`, not `skill_root`.

Use supported and permitted general-purpose subagents when available; otherwise
run reviewer and validator sequentially in the main thread. The artifacts and
finding policy stay the same. Never describe main-thread passes as independent
validation. Model selection belongs to the harness or CI configuration.

Claude Code still discovers the default `skills/` directory. Its CLI envelope,
authentication, model aliases, and publication wiring remain CI concerns.
Do not require custom execution adapters for another skills-compatible harness.

## Known Review Exceptions

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
- `tox -e linters` (includes pinned Skillsaw checks)

If `tox` is not installed locally, use `uvx tox ...` instead. `uvx` is the
preferred fallback for ad hoc verification in this repository.

When running multiple tox environments with `uvx tox`, use a comma-separated
env list in a single invocation, for example `uvx tox -e py3,linters`, rather
than launching multiple tox envs in parallel.

If a path move is intentional, update tests in the same change so the new
contract is explicit.
