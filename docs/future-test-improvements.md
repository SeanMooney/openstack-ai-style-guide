# Future Test & Lint Improvements

Longer-term improvements for the testing and linting infrastructure.
These items are out of scope for the initial test harness merge but
should be tracked for follow-up work.

## 1. Add a Zuul CI job for unit tests

Currently `zuul.d/projects.yaml` only runs linting and code review.
Add a job that runs `tox -e py3`:

```yaml
- project:
    check:
      jobs:
        - teim-code-review
        - openstack-ai-style-guide-lint
        - openstack-ai-style-guide-test  # new: tox -e py3
```

## 2. Add `ruff format --check` to pre-commit

The pre-commit config runs `ruff` (linter) but not `ruff format`
(formatter). Adding the formatter hook ensures consistent code
formatting:

```yaml
- id: ruff-format
  args: [--check]
```

## 3. Add molecule tests for remaining roles

`ai_review_setup` and `ai_context_extraction` are harder to molecule
test because they depend on:

- **ai_review_setup**: Live Claude CLI (`claude --version`),
  `ansible.posix.synchronize` (rsync), package installation (`jq`)
- **ai_context_extraction**: Live `zuul` inventory variables
  (`zuul.executor.inventory_file`, `zuul.project.src_dir`), Claude
  CLI, git repository with commits

Approaches:

- Mock Claude CLI with a script that prints a version string
- Mock `zuul` vars in molecule inventory host_vars
- Set up a test git repo in converge for `ai_context_extraction`
- Use `delegate_to: localhost` override for synchronize

## 4. Add unit tests for `generate_zuul_comments.py`

This is the most complex Python script (456 lines, 11 functions) with
zero unit test coverage. Priority functions to test:

- `parse_location()` -- parsing "file:line" strings
- `normalize_file_path()` -- path normalization
- `format_issue_message()` -- message formatting
- `extract_file_comments()` -- the core logic
- `validate_zuul_schema()` -- duplicated from the separate
  `validate_zuul_schema.py` that IS tested

## 5. Add coverage threshold enforcement

Wire up `tox -e cover` with a minimum coverage threshold (e.g.,
`coverage report --fail-under=60`) and integrate coverage reporting
into the Zuul job as an artifact.

## 6. Create integration/pipeline tests

Test the full review pipeline (context extraction -> AI review -> HTML
generation -> Zuul comments) with mocked services. This validates data
contracts between roles -- e.g., that the JSON output from
`ai_code_review` matches what `ai_html_generation` and
`ai_zuul_integration` expect.

## 7. Consolidate duplicate code between Python scripts

`render_html_from_json.py` and `generate_zuul_comments.py` both
implement `extract_review_data()` and `load_json_with_trailing_text()`
with near-identical logic. When you refactor into a package in the
future, extract these into a shared utility module.

## 8. Add pre-commit hook for running fast unit tests

Add a local pre-commit hook that runs a subset of fast unit tests
(e.g., schema validation, HTML escaping) to catch regressions before
push. Keep the full suite in tox.

## 9. Deduplicate role Makefiles

All three role Makefiles are byte-for-byte identical. Options:

- Single `Makefile.role` at repo root, included via
  `include ../../Makefile.role`
- Remove them entirely -- top-level `make molecule-<role>` targets
  already exist

## 10. Refactor into a uv-managed Python package

When ready, add `[build-system]` to pyproject.toml with uv, move
shared utilities into a proper package, and switch tox to
`usedevelop = true` with `deps = .[test]`. This eliminates the
importlib workaround and enables proper dependency resolution.
