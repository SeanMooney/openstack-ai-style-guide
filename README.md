# OpenStack AI Review System

This repository packages the active pieces of an AI-assisted OpenStack review
workflow:

- Claude plugin and marketplace metadata
- review agents and the `/teim-review` skill
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

Local interactive usage follows the same model through `/teim-review`.

## Primary Entry Points

### Local review

```bash
/plugin marketplace add /path/to/openstack-ai-style-guide
/plugin install teim-review@openstack-ai-style-guide
/teim-review
```

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
├── .claude-plugin/        # Claude plugin and marketplace metadata
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
3. **Runtime behavior and contracts**: `agents/`, `skills/`, and
   `schemas/review-report-schema.json`

`references/` holds canonical snapshots of external coding standards, policy,
and review guidance. `docs/quick-rules.md` and
`docs/comprehensive-guide.md` are curated baseline guides distilled from those
references. `docs/knowledge/` is the starting point for internal overlays,
examples, and future RAG-oriented review knowledge.

Agents and the schema remain authoritative for review behavior, orchestration,
and output contracts.

See [docs/review-system-overview.md](docs/review-system-overview.md) for the
runtime model and [docs/archive/README.md](docs/archive/README.md) for legacy
material status.

## Compatibility Commitments

This restructuring pass preserves the current runtime contracts:

- plugin name: `teim-review`
- marketplace identity: `openstack-ai-style-guide`
- skill entrypoint: `/teim-review`
- orchestrator: `teim-review-agent`
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
