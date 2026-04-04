# OpenStack AI Review System

This repository packages the active pieces of an AI-assisted OpenStack review
workflow:

- shared provider-neutral review prompts and model profiles
- Claude plugin and marketplace metadata
- Codex plugin and skill tooling
- Cursor rules and custom mode template
- review agents and tool-native interactive entrypoints
- review report schema and helper transforms
- Zuul jobs and Ansible roles that run the workflow in CI

The repository started as a generic AI style-guide project. It has since
evolved into a review system with a growing internal knowledge base. The
runtime pipeline is the primary product, while standards snapshots and derived
review knowledge support that pipeline.

## Active Workflow

The current production path is:

1. Zuul checks out this repository as a required project.
2. `ai_review_setup` registers the local marketplace and installs the
   `teim-review` plugin.
3. `ai_code_review` invokes `teim-review-agent` in one Claude session.
4. The agent orchestrates context extraction, commit summarization,
   project-guideline extraction, and structured review generation.
5. Python helpers turn the JSON report into HTML and Zuul file comments.

Local interactive usage is now distributed through native tool adapters over
the same shared review core.

## Primary Entry Points

### Local review

#### Claude

```bash
/plugin marketplace add /path/to/openstack-ai-style-guide
/plugin install teim-review@openstack-ai-style-guide
/teim-review
```

#### Codex

```bash
npm install -g @openai/codex
codex login
scripts/install-codex-skill
codex
# restart Codex, then install teim-review from the Local Codex Plugins marketplace
# use /skills to discover the installed skill, then run:
$teim-review
```

Detailed installation, update, troubleshooting, and isolated validation steps
live in `docs/codex.md`.

#### Cursor

- versioned project rules live in `.cursor/rules/`
- `cursor/teim-review-mode-template.json` is the repository template for a
  Custom Mode backed by the same shared review workflow

Local output is written to `.teim-review/`:

- `zuul-context.md`
- `commit-summary.md`
- `project-guidelines.md`
- `review-report.json`
- `review-report.html`

### Zuul review

The live job entrypoint is `teim-code-review`, defined in
`zuul.d/jobs.yaml` and executed via `playbooks/teim-code-review/run.yaml`.

## Repository Layout

```text
openstack-ai-style-guide/
├── prompts/              # Shared provider-neutral review workflow
├── config/               # Shared semantic model profile mappings
├── .claude-plugin/        # Claude plugin and marketplace metadata
├── .agents/plugins/       # Codex repo marketplace catalog
├── .cursor/rules/         # Cursor-native project rules
├── plugins/teim-review/   # Codex-native plugin bundle
├── cursor/                # Cursor custom mode templates
├── agents/                # Review orchestration and specialist agents
├── skills/                # Interactive skill entrypoints
├── schemas/               # Structured output contracts
├── tools/                 # JSON → HTML and JSON → Zuul helpers
├── roles/                 # Ansible roles used by the Zuul workflow
├── playbooks/             # Zuul playbooks
├── zuul.d/                # Jobs, projects, semaphores
├── docs/                  # Baseline guides, knowledge overlays, and legacy docs
├── references/            # Canonical external standards snapshots
└── tests/                 # Unit and contract tests
```

## Knowledge Model

The repository now treats review knowledge in three layers:

1. **Canonical external snapshots**: `references/`
2. **Curated baseline and derived knowledge**: `docs/`
3. **Provider-neutral runtime behavior**: `prompts/`, `config/`, and
   `schemas/review-report-schema.json`
4. **Tool-native adapters**: `agents/`, `skills/`, `.claude-plugin/`,
   `.cursor/rules/`, and `plugins/teim-review/`

`references/` holds canonical snapshots of external coding standards, policy,
and review guidance. `docs/quick-rules.md` and
`docs/comprehensive-guide.md` are curated baseline guides distilled from those
references. `docs/knowledge/` is the starting point for internal overlays,
examples, and future RAG-oriented review knowledge.

`prompts/teim-review-core.md` and `schemas/review-report-schema.json` are
authoritative for workflow behavior and output contracts. Tool-native adapter
files translate that shared core into Claude, Codex, and Cursor delivery
surfaces.

See [docs/review-system-overview.md](docs/review-system-overview.md) for the
runtime model and [docs/archive/README.md](docs/archive/README.md) for legacy
material status.

## Compatibility Commitments

This restructuring pass preserves the current runtime contracts:

- plugin name: `teim-review`
- marketplace identity: `openstack-ai-style-guide`
- Claude skill entrypoint: `/teim-review`
- Codex skill entrypoint: `$teim-review`
- orchestrator: `teim-review-agent`
- shared workflow: `prompts/teim-review-core.md`
- output schema: `schemas/review-report-schema.json`
- local output directory: `.teim-review/`
- Zuul jobs: `teim-code-review` and `openstack-ai-style-guide-lint`

## Validation

Common checks:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
tox -e py3
tox -e linters
```

`tox` is the main developer path when available. The unit tests also cover
repo contracts such as plugin metadata, skill wiring, and workflow references.

## Supporting Material

The repo still includes `docs/quick-rules.md`,
`docs/comprehensive-guide.md`, a new `docs/knowledge/` area, and legacy
checklists/templates material. These serve different purposes:

- baseline review context for the current workflow
- constructed internal knowledge that will grow over time
- legacy support content pending further pruning or relocation

## License

Apache License 2.0. See [LICENSE](LICENSE).
