---
name: security-auditor
description: Dedicated security audit of a code change, component, or repository. Trace exploitable vulnerabilities and report evidence, impact, confidence, and remediation.
disable-model-invocation: true
license: Apache-2.0
---

# Security Auditor

Run this audit only when the user explicitly requests it. Do not invoke it as
an extra stage of ordinary code review or because changed code handles input,
credentials, or authentication. The teim-review workflow owns its review policy.

## Scope

Use the repository, revision range, component, or vulnerability question supplied
by the user. For a whole-repository audit, inspect existing behavior as well as
recent changes; for a patch audit, distinguish introduced issues from existing
ones. Record the files and entry points examined and any material coverage gaps.

Read the project's instructions and security assumptions before tracing code.
Keep the checkout unchanged unless the user also requested fixes. Use the
current thread; supported and permitted subagents are optional, never required.

## Investigation

1. Identify trust boundaries, externally reachable entry points, authentication,
   authorization, and privileged operations relevant to the requested scope.
2. Trace each suspected path from attacker-controlled input through validation
   to a sensitive operation. Confirm which protections apply along that path.
3. Check the deployment and caller assumptions that determine reachability.
   Configuration, command-line arguments, and environment variables are not
   attacker-controlled merely because code reads them; establish who can set
   them. Do not assume URLs are free of credentials or sensitive query data.
4. Verify concrete exploit preconditions against code and available tests.
   Prefer local fixtures or reasoning from code; active probes of external
   systems need authorization for those targets.
5. Deduplicate findings by root cause and retain actionable vulnerabilities
   supported by evidence. Stop when the requested scope is examined; report
   unresolved paths as limitations rather than repeatedly seeking confirmation.

Prioritize code execution, authentication or authorization bypass, privilege
escalation, unsafe deserialization, injection, unsafe file access, and disclosure
of secrets or private data. Framework protections matter only where the code
actually uses them. Test files, documentation, CI, and memory-safe languages do
not prove a vulnerability absent; assess their reachable impact.

## Admission and classification

Each reported vulnerability needs an attacker capability, a reachable path, a
missing or bypassed protection, and a demonstrated security impact. A pattern
match, dependency age, missing hardening setting, or hypothetical race alone
does not establish a vulnerability.

- **High severity:** an established path to code execution, significant private
  data disclosure, or authentication/authorization bypass with major impact.
- **Medium severity:** an established vulnerability with narrower impact or
  additional concrete preconditions and significant impact. Report it only
  when the exploit path is obvious and concrete.
- Keep lower-impact hardening suggestions separate when the user requested
  them; do not inflate their severity to fit the main report.
- Use confidence from 0 to 1. Include a vulnerability only at confidence 0.80
  or higher with a supported exploit path. State uncertainty separately when
  missing deployment details prevent that conclusion.

Calibrate confidence from the evidence, independently of severity:

- **0.90–1.00:** a certain exploit path is identified; test it locally when
  possible and record whether it was tested or established by code tracing.
- **0.80–0.89:** a clear vulnerability pattern has known exploitation methods
  and the relevant attacker control and protections have been checked.
- **0.70–0.79:** a suspicious pattern depends on specific exploit conditions;
  investigate further but do not include it in the vulnerability report.
- **Below 0.70:** omit as too speculative. Never raise a score to pass the gate.

## Exclusions and security precedents

Keep these exclusions separate from the exploitability admission test:

- Exclude denial of service, resource exhaustion, rate limiting, memory leaks,
  theoretical races, missing audit logging, and defense-in-depth hardening
  from the high/medium vulnerability report.
- Exclude dependency-age findings managed outside the reviewed change.
- Do not report safely stored secrets or trusted environment/CLI values merely
  because they exist. Establish attacker control before treating them as input.
- Test files and documentation alone are not vulnerabilities. Trace any claim
  to a supported execution path and security impact.
- CI expressions and script commands require a concrete untrusted-input path
  to a shell or sensitive operation before qualifying as injection.
- Framework-escaped React/Angular output is not XSS; investigate unsafe rendering
  such as `dangerouslySetInnerHTML` or `bypassSecurityTrustHtml` and verify that
  attacker input reaches it without an effective protection.
- Do not demand client-side authorization when an unchanged backend enforces it,
  or report memory-safety defects prevented by the language's guarantees.
- Ordinary log output and URLs are not leaks without secrets or private data;
  verify their actual contents. UUID use alone does not require brute-force
  protection or establish an authorization failure.
- Regex syntax, AI prompt text, or an SSRF path alone is insufficient: establish
  attacker control of the relevant execution or target and a sensitive impact.
- Subtle web issues such as tabnabbing or XS-Leaks require confidence of at
  least 0.90 and a concrete exploit path.

## Report

Start with scope, coverage limits, and high/medium finding counts. For each
finding include:

- Category and short title, with exact file and line references.
- Severity, confidence, and concrete impact.
- Evidence and an exploit path identifying attacker control and preconditions.
- The relevant existing protection and why it fails on this path.
- A specific remediation with a working code fix example in the relevant
  language, including the configuration change when configuration is the fix.
- Verification performed and a regression check the maintainer can run.

Before returning the report, re-check every finding against the exclusions,
severity and confidence calibration, exact code locations, exploit scenario,
working fix example, and verification steps. Record untested assumptions and
do not describe an unexecuted example or exploit as tested.

Report zero findings when no examined path meets the admission criteria; do not
claim the entire system is secure. If an output path was requested, write the
report there using available file tools, verify the file exists and contains
the complete report, and return its path. Otherwise return the report directly.
