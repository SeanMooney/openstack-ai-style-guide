# OpenStack AI Review System

Portable skills for Claude Code, Codex, Cursor, OpenCode, and Pi. The
teim-review skill contains its workflow, finding policy, reviewer and validator
prompts, coding guidance, schemas, and deterministic scripts.

## Local review

Install the shared skill into your chosen tools with the Agent Skills CLI:

```bash
npx skills add . --skill teim-review -a claude-code codex cursor opencode pi
```

Run this from the source checkout to install the local version. Select only
one installation method per tool to avoid duplicate skills. Native plugin
metadata exposes the same `skills/` directory without a separate skill body.

For Claude Code, the existing marketplace installation remains supported:

```text
/plugin marketplace add /path/to/openstack-ai-style-guide
/plugin install teim-review@openstack-ai-style-guide
/teim-review
```

Codex users can retain `scripts/install-codex-skill` and invoke `$teim-review`;
see [docs/codex.md](docs/codex.md). Pi can also install the repository as a
native package with `pi install ./` and invoke `/skill:teim-review`.

The skill reviews the target repository and writes `.teim-review/` artifacts.
It runs candidate generation followed by finding validation, then assembles,
normalizes, and renders the report deterministically. If the harness supports
and permits subagents it uses them; otherwise both passes run in the main
thread. It uses the harness's model settings throughout.

## Standalone skills

| Skill | Purpose | Invocation |
| --- | --- | --- |
| `security-auditor` | Dedicated security audit with exploit-path evidence | Explicit user request only |
| `code-maintainability-auditor` | Dead code, dependency, and consolidation audit | Explicit user request only |
| `doc-to-markdown` | Convert source documentation into cited Markdown | Tool/model discovery or explicit request |

These are sibling packages under `skills/`, each usable independently. Native
plugin installation includes all four skills. To install an individual sibling
with the Skills CLI, select its name with `--skill`. The audit skills use
`disable-model-invocation: true` and Codex's `allow_implicit_invocation: false`;
document conversion retains normal discovery. Each audit also requires an
explicit user request in its instructions for hosts without matching controls.

The old preparation agents have been removed. Deterministic context preparation
remains part of teim-review. Standalone skills are not additional stages in the
CI/local review pipeline, and no native agent registration is required.

## CI review

Zuul job `teim-code-review` uses the same skill through Claude Code:

1. Prepare Git scope and context with bundled Python scripts.
2. Run one Claude CLI invocation with the shared skill and `findings_only: true`.
3. Assemble and normalize the structured findings deterministically.
4. Render HTML and publish Zuul comments and artifacts.

The job selects its model. The skill contains no model IDs or tier routing.
Claude CLI authentication, model alias configuration, structured-output
handling, and publication remain in the CI roles.

## Repository layout

```text
skills/
  teim-review/
    SKILL.md               Portable review entrypoint
    references/            Workflow, role prompts, policy, coding knowledge
    references/schemas/    Candidate, validated, and final report contracts
    scripts/               Scope, preparation, assembly, normalization, HTML
  security-auditor/        Explicit-only security audit
  code-maintainability-auditor/
                           Explicit-only maintenance audit
  doc-to-markdown/         Discoverable document conversion
plugin.json                Agent Plugins 1.0.0 portable manifest
.claude-plugin/            Claude plugin and marketplace metadata
.codex-plugin/             Codex plugin metadata
.cursor-plugin/            Cursor plugin metadata
.agents/plugins/           Codex repository marketplace
package.json               Pi package metadata
roles/, playbooks/, zuul.d/ CI integration
references/                Canonical external standards snapshots
docs/                      Usage, architecture, and legacy support documents
tools/                     Standalone legacy utilities
tests/                     Unit, installation, and contract tests
```

The curated coding guides and knowledge live inside the skill. External
standards snapshots remain in root `references/`; they are source material
for maintaining that curated guidance, not installation dependencies.

See [the architecture](docs/review-system-overview.md) and
[contribution guidance](CONTRIBUTING.md).

## Validation

```bash
uvx tox -e py3,linters
```

Tests exercise installed skill resources against a separate target repository,
report schemas, deterministic processing, marketplace metadata, and CI wiring.
Skillsaw runs through pre-commit and the existing Zuul lint job. Its reviewed
revision is pinned in `.pre-commit-config.yaml`; `.skillsaw.yaml` enables the
common skill directory layout policy and gates structural errors. Advisory
findings remain visible without a baseline. Live model behavior needs a
separate smoke review in each supported harness.

## License

Apache License 2.0. See [LICENSE](LICENSE).
