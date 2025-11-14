# AI Code Review Refactor Progress

## Overview

This document tracks the incremental refactoring of the AI code review workflow
to use explicit task-based playbook orchestration with modular, well-isolated
Ansible roles.

**Strategy:** Progressive lint fixing with gating CI compatibility. Each commit
independently passes all CI checks.

**Total PRs:** 11 stacked pull requests

---

## Refactor Plan

### Phase 1: Linting Infrastructure

#### PR #1: Enable linting with exclusions

- **Branch:** `01-enable-linting`
- **Base:** `master`
- **Status:** ✅ Completed
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
- **Status:** ⏳ Not started
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
- **Status:** ⏳ Not started
- **Changes:**
  - Rename `roles/ai-*` → `roles/ai_*` (5 roles)
  - Update playbook references
  - Remove role naming exclusions from `.ansible-lint`
- **Why CI passes:** Playbook uses explicit include_role, just updating names

---

### Phase 4: Variable Prefixing (Per Role)

#### PR #4: Prefix variables - ai_review_setup

- **Branch:** `04-prefix-vars-setup`
- **Base:** `03-rename-roles`
- **Status:** ⏳ Not started
- **Changes:**
  - Add `ai_review_setup_*` prefixes to defaults
  - Update task files to use prefixed variables
  - Update playbook to map job vars → role vars
  - Remove var-naming exclusions for this role
- **Why CI passes:** Playbook explicitly passes all needed variables

#### PR #5: Prefix variables - ai_context_extraction

- **Branch:** `05-prefix-vars-context`
- **Base:** `04-prefix-vars-setup`
- **Status:** ⏳ Not started
- **Changes:** Same pattern as PR #4 for ai_context_extraction role
- **Why CI passes:** Same pattern

#### PR #6: Prefix variables - ai_code_review

- **Branch:** `06-prefix-vars-review`
- **Base:** `05-prefix-vars-context`
- **Status:** ⏳ Not started
- **Changes:**
  - Same pattern as PR #4 for ai_code_review role
  - Update exported variables (e.g., `ai_code_review_has_critical_issues`)
  - Update status variable references in playbook summary
- **Why CI passes:** Same pattern

#### PR #7: Prefix variables - ai_html_generation

- **Branch:** `07-prefix-vars-html`
- **Base:** `06-prefix-vars-review`
- **Status:** ⏳ Not started
- **Changes:** Same pattern as PR #4 for ai_html_generation role
- **Why CI passes:** Same pattern

#### PR #8: Prefix variables - ai_zuul_integration

- **Branch:** `08-prefix-vars-zuul`
- **Base:** `07-prefix-vars-html`
- **Status:** ⏳ Not started
- **Changes:**
  - Same pattern as PR #4 for ai_zuul_integration role
  - Remove ALL variable naming exclusions from `.ansible-lint`
- **Why CI passes:** All roles now have proper variable prefixing

---

### Phase 5: Helper Role Extraction

#### PR #9: Extract run_claude_code helper

- **Branch:** `09-extract-helper`
- **Base:** `08-prefix-vars-zuul`
- **Status:** ⏳ Not started
- **Changes:**
  - Create `roles/run_claude_code/` with all files
  - Extract Claude CLI execution logic
  - Role not used yet
- **Why CI passes:** New unused helper role

#### PR #10: Integrate run_claude_code

- **Branch:** `10-integrate-helper`
- **Base:** `09-extract-helper`
- **Status:** ⏳ Not started
- **Changes:**
  - Update ai_review_setup to use run_claude_code
  - Update ai_context_extraction to use run_claude_code
  - Update ai_code_review to use run_claude_code
  - Delete old extracted task files
- **Why CI passes:** Refactored to use helper, functionally equivalent

---

### Phase 6: Final Cleanup

#### PR #11: Final cleanup

- **Branch:** `11-final-cleanup`
- **Base:** `10-integrate-helper`
- **Status:** ⏳ Not started
- **Changes:**
  - Python script improvements
  - Minor code quality updates
  - Verify no lint exclusions remaining
- **Why CI passes:** Minor improvements to working code

---

## Progress Checklist

- [x] Phase 1: Linting Infrastructure (PR #1)
- [ ] Phase 2: Playbook Orchestration (PR #2)
- [ ] Phase 3: Role Renames (PR #3)
- [ ] Phase 4: Variable Prefixing
  - [ ] PR #4: ai_review_setup
  - [ ] PR #5: ai_context_extraction
  - [ ] PR #6: ai_code_review
  - [ ] PR #7: ai_html_generation
  - [ ] PR #8: ai_zuul_integration
- [ ] Phase 5: Helper Role Extraction
  - [ ] PR #9: Extract run_claude_code
  - [ ] PR #10: Integrate helper
- [ ] Phase 6: Cleanup (PR #11)

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

---

## Next Steps

1. Stage and commit PR #1 changes
2. Begin Phase 2: Task-based playbook orchestration (PR #2)
