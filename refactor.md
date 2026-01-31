# AI Code Review Refactor Progress

## Overview

This document tracks the incremental refactoring of the AI code review workflow
to use explicit task-based playbook orchestration with modular, well-isolated
Ansible roles.

**Strategy:** Progressive lint fixing with gating CI compatibility. Each commit
independently passes all CI checks.

**Total PRs:** 9 (originally planned as 11, Phases 5-6 combined into one PR)

---

## Refactor Plan

### Phase 1: Linting Infrastructure

#### PR #1: Enable linting with exclusions

- **Branch:** `01-enable-linting`
- **Base:** `master`
- **Status:** Completed
- **Changes:**
  - Added `.ansible-lint` with skip_list for current failures
  - Updated `.pre-commit-config.yaml` to add ansible-lint v25.11.0 hook
  - Excluded role naming violations (role-name)
  - Excluded variable naming violations (var-naming)
  - Excluded FQCN violations (fqcn, fqcn[action-core], fqcn[action])
  - Excluded meta tag violations (meta-no-tags)
  - Excluded name template violations (name[template])
  - Excluded YAML formatting issues (yaml, yaml[empty-lines])
  - Excluded idempotency issues (no-changed-when, risky-shell-pipe)
  - Excluded key order suggestions (key-order, key-order[play])
  - Excluded schema validation issues (schema)
  - Excluded Zuul-specific module file (roles/ai-zuul-integration/tasks/main.yaml)
- **Why CI passes:** All current failures explicitly excluded via skip_list

---

### Phase 2: Playbook Orchestration

#### PR #2: Task-based orchestration

- **Branch:** `02-playbook-orchestration`
- **Base:** `01-enable-linting`
- **Status:** Completed
- **Changes:**
  - Rewrite `playbooks/teim-code-review/run.yaml`
  - Remove `roles:` section (role dependency chain)
  - Add explicit `tasks:` with `include_role` for each role
  - Keep OLD role names (`ai-review-setup`, etc.)
  - Keep OLD variable names (unprefixed)
  - Update `playbooks/teim-code-review/post.yaml`
- **Why CI passes:** Uses existing roles/variables, only changes orchestration

---

### Phase 3: Role Renames

#### PR #3: Rename to underscores

- **Branch:** `03-rename-roles`
- **Base:** `02-playbook-orchestration`
- **Status:** Completed
- **Changes:**
  - Rename `roles/ai-*` to `roles/ai_*` (5 roles)
  - Update playbook references
  - Remove role naming exclusions from `.ansible-lint`
- **Why CI passes:** Playbook uses explicit include_role, just updating names

---

### Phase 4: Variable Prefixing (Per Role)

#### PR #4: Prefix variables - ai_review_setup

- **Branch:** `04-prefix-vars-setup`
- **Base:** `03-rename-roles`
- **Status:** Completed
- **Changes:**
  - Add `ai_review_setup_*` prefixes to defaults
  - Update task files to use prefixed variables
  - Update playbook to map job vars to role vars
  - Remove var-naming exclusions for this role
- **Why CI passes:** Playbook explicitly passes all needed variables

#### PR #5: Prefix variables - ai_context_extraction

- **Branch:** `05-prefix-vars-context`
- **Base:** `04-prefix-vars-setup`
- **Status:** Completed
- **Changes:** Same pattern as PR #4 for ai_context_extraction role
- **Why CI passes:** Same pattern

#### PR #6: Prefix variables - ai_code_review

- **Branch:** `06-prefix-vars-review`
- **Base:** `05-prefix-vars-context`
- **Status:** Completed
- **Changes:**
  - Same pattern as PR #4 for ai_code_review role
  - Update exported variables (e.g., `ai_code_review_has_critical_issues`)
  - Update status variable references in playbook summary
- **Why CI passes:** Same pattern

#### PR #7: Prefix variables - ai_html_generation

- **Branch:** `07-prefix-vars-html`
- **Base:** `06-prefix-vars-review`
- **Status:** Completed
- **Changes:** Same pattern as PR #4 for ai_html_generation role
- **Why CI passes:** Same pattern

#### PR #8: Prefix variables - ai_zuul_integration

- **Branch:** `08-prefix-vars-zuul`
- **Base:** `07-prefix-vars-html`
- **Status:** Completed
- **Changes:**
  - Same pattern as PR #4 for ai_zuul_integration role
  - Remove ALL variable naming exclusions from `.ansible-lint`
- **Why CI passes:** All roles now have proper variable prefixing

---

### Phase 5: Helper Role Extraction, Integration, and Final Cleanup

#### PR #9: Extract run_claude_code, integrate, and fix all lint violations

- **Branch:** `09-final-cleanup`
- **Base:** `08-prefix-vars-zuul`
- **Status:** Completed
- **Changes:**
  - Fix double-prefix bug in ai_zuul_integration
    (`ai_zuul_integration_ai_zuul_integration_html_report_file`)
  - Create `roles/run_claude_code/` helper role with properly prefixed
    variables (`run_claude_code_*`), FQCN modules, and retry/error logic
  - Integrate run_claude_code into ai_context_extraction and ai_code_review
    via `include_role` with explicit variable mapping
  - Add claude_binary, anthropic_auth_token, anthropic_api_url to
    ai_context_extraction defaults and playbook vars
  - Delete old `ai_review_setup/tasks/run-claude-command.yaml` and
    `check-claude-result.yaml`
  - Fix all 68 remaining ansible-lint violations:
    - FQCN: add `ansible.builtin.*` prefix to all bare module names
    - meta-no-tags: `code-review` to `codereview`, `ci-cd` to `cicd`
    - risky-shell-pipe: add `set -o pipefail` and `executable: /bin/bash`
    - no-changed-when: add `changed_when` to HTML generation command
    - yaml[truthy]: `yes` to `true` for synchronize recursive
    - yaml[line-length]: break long Jinja conditional into multi-line
    - key-order[play]: reorder play keys in both playbooks
  - Remove entire skip_list from `.ansible-lint` (empty list)
  - Remove ai_zuul_integration from exclude_paths (mock_modules handles
    zuul_return)
- **Why CI passes:** All violations fixed, full production profile enforced

---

## Progress Checklist

- [x] Phase 1: Linting Infrastructure (PR #1)
- [x] Phase 2: Playbook Orchestration (PR #2)
- [x] Phase 3: Role Renames (PR #3)
- [x] Phase 4: Variable Prefixing
  - [x] PR #4: ai_review_setup
  - [x] PR #5: ai_context_extraction
  - [x] PR #6: ai_code_review
  - [x] PR #7: ai_html_generation
  - [x] PR #8: ai_zuul_integration
- [x] Phase 5: Helper Role Extraction, Integration, and Final Cleanup
  - [x] PR #9: Extract run_claude_code, integrate, fix all lint violations

---

## Key Principles

1. **Gating CI Compatible:** Every commit passes CI independently
2. **No Duplication:** No side-by-side old/new roles
3. **Progressive Fixing:** Fix lint issues incrementally
4. **Self-Validating:** Each PR verifies its own changes

---

## Session Notes

### Session 1 - Initial Planning

- Created refactor plan
- Identified gating CI constraint
- Established 11-PR approach

### Session 2 - PR #1 Implementation

- Implemented ansible-lint configuration with comprehensive skip_list
- Added ansible-lint v25.11.0 to pre-commit hooks
- Discovered 87 total lint violations across 11 rule types
- Key findings:
  - 64 FQCN violations (missing ansible.builtin.* prefixes)
  - 6 meta tag violations (hyphens in tags)
  - 7 name[template] violations (Jinja in task names)
  - Various other violations (yaml, no-changed-when, key-order, etc.)
- Excluded Zuul-specific module file (syntax-check is unskippable)
- All playbooks and roles now pass ansible-lint
- Pre-commit hooks installed and verified

### Session 3 - PRs #2-8 Implementation

- Implemented task-based playbook orchestration
- Renamed all roles from hyphenated to underscore format
- Prefixed all role variables across 5 roles
- Progressively removed skip_list entries

### Session 4 - PR #9 Final Cleanup

- Combined original PRs #9, #10, #11 into single PR #9
- Fixed double-prefix bug in ai_zuul_integration
- Created run_claude_code helper role
- Integrated helper into ai_context_extraction and ai_code_review
- Fixed all 68 remaining ansible-lint violations
- Removed entire skip_list (empty)
- Removed ai_zuul_integration from exclude_paths
- Full production profile now enforced with zero violations
