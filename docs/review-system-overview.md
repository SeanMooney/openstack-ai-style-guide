# Review System Overview

This document describes the active architecture of the OpenStack AI review
system contained in this repository.

## Purpose

The repository exists to package and run an AI-assisted review workflow for
OpenStack-style changes. It is not primarily a generic style guide anymore.

## Core Runtime Contracts

- **Interactive entrypoint**: `/teim-review`
- **Primary orchestrator**: `agents/teim-review-agent.md`
- **Review rubric**: `agents/code-review-agent.md`
- **Structured output**: `schemas/review-report-schema.json`
- **CI entrypoint**: `zuul.d/jobs.yaml` job `teim-code-review`

## Execution Model

### Local mode

- User installs the plugin from the local marketplace.
- `/teim-review` invokes `teim-review-agent`.
- The agent detects local git context and writes output to `.teim-review/`.

### Zuul mode

- The Zuul job copies executor inventory into the review output directory.
- `ai_review_setup` configures Claude and installs the plugin.
- `ai_code_review` invokes `teim-review-agent` once with structured output.
- `ai_html_generation` renders HTML from the JSON report.
- `ai_zuul_integration` converts the report into Zuul file comments and
  registers artifacts.

## Knowledge Ownership

### Authoritative

- `agents/` owns review intent, orchestration, and reviewer behavior.
- `skills/` owns interactive invocation shape.
- `schemas/` owns report shape and downstream compatibility.

### Canonical external knowledge

- `references/` contains canonical snapshots of upstream policy, coding
  standards, and review guidance.

### Derived internal knowledge

- `docs/quick-rules.md` and `docs/comprehensive-guide.md` are curated baseline
  guides distilled from references and internal review knowledge.
- `docs/knowledge/` is the growing internal knowledge base for overlays,
  examples, and retrieval-oriented review material consumed by the review
  workflow over time.

### Archived support

- `docs/checklists/`
- `docs/templates/`

These remain in the repository, but they are not the primary product surface.
See [archive/README.md](archive/README.md).
