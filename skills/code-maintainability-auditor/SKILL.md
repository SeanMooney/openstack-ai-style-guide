---
name: code-maintainability-auditor
description: Dedicated audit of dead code, unused dependencies, duplication, and refactoring opportunities in a component or repository. Report usage evidence, uncertainty, and removal or consolidation impact.
disable-model-invocation: true
license: Apache-2.0
---

# Code Maintainability Auditor

Run this audit only when the user explicitly requests it. Do not invoke it
automatically after implementation or as an extra stage of ordinary review.
The teim-review workflow owns its patch-review criteria and output contract.

## Scope and boundaries

Honor the requested symbol, component, dependency set, or repository scope.
Use targeted analysis for a specific suspected dead item; use broader usage
and dependency tracing for a repository audit. Record scope and coverage gaps.

Keep the checkout unchanged unless the user also requested implementation.
Return a report directly, or save it to the user's requested output path and
verify the complete report was written. Use available file tools without
requiring a particular tool name. Subagents are optional when supported and
permitted; continue in the current thread otherwise.

## Trace usage before declaring code dead

1. Locate definitions, imports, references, call sites, and registrations.
   Search source, tests, configuration, packaging metadata, build scripts,
   documentation, entry points, and plugin declarations.
2. Follow the usage chain from production entry points. Separate production
   reachability from test coverage and development-only usage.
3. Check dynamic imports, reflection, string-based dispatch, serialization,
   dependency injection, generated code, and platform-specific paths before
   treating an absent direct reference as evidence of non-use.
4. Identify exported APIs and possible external consumers. No internal caller
   does not prove an exported symbol is unused. Likewise, test-only references
   are a lead to investigate rather than proof that removal is safe.
5. Cross-check candidates with an appropriate analyzer, import inspection, or
   a second usage search. Explain any disagreement between methods.

Classify an item as **high-confidence dead code** only when its usage search
and entry-point tracing establish non-reachability within the supported scope,
with no unresolved dynamic registration or public compatibility obligation.
Put unresolved external or dynamic usage in a separate manual-verification list.
Do not report an unused import already enforced by the project's linter as a
substantive maintenance finding.

## Dependencies and consolidation

For each dependency candidate, inspect imports and executable, test, build,
packaging, and optional-feature usage. A dependency may be needed without a
Python import. If dead code is its only consumer, explain that chain. Distinguish
direct dependencies from transitives and do not claim removal savings without
checking the remaining dependency graph.

For duplication, compare behavior, callers, change patterns, and compatibility
constraints as well as similar syntax. Recommend a shared abstraction only
when it removes a concrete source of maintenance work. Show the occurrences,
the common behavior, the proposed boundary, and behavior that must stay distinct.
Keep recommendations backward compatible unless the user explicitly consents
to breaking-change proposals. Without that consent, place an incompatible
option in the manual-verification list as a compatibility constraint rather
than recommending it. When breaking proposals are authorized, identify every
API break, migration, and deployment coordination requirement. Prefer a small
compatible change when it addresses the same problem.

## Report

Present the useful sections for the scope; omit empty sections:

- **Scope and summary:** examined entry points, retained candidates, and limits.
- **High-confidence dead code:** symbol, file/line, evidence of non-use, test
  usage, dynamic/export checks, and removal impact.
- **Unused dependencies:** usage evidence, dependency chains, optional/build
  consumers checked, and specific removal steps.
- **Consolidation opportunities:** occurrences, shared behavior, the maintenance
  problem, proposed refactoring, compatibility risk, and verification steps.
- **Manual verification:** uncertain item, missing evidence, possible consumer,
  and the check needed to resolve it.
- **Priorities:** recommended order based on impact, confidence, and change risk.

Use concrete file references and label evidence versus inference. Include line
counts or effort estimates only when measured or explain how they were derived.
Stop when the requested scope has been traced and the actionable report is
complete. Report no supported findings when the evidence does not justify one.
Before finalizing, re-verify that every recommendation is backward compatible
or covered by the user's explicit consent, and that its compatibility impact
and verification steps are accurately documented.
