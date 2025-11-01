# Code Review Checklist for AI-Generated OpenStack Code

Use this checklist when reviewing code that was generated or assisted by AI tools.

## Initial Assessment

- [ ] **Commit message includes AI attribution** (Generated-By or Assisted-By)
- [ ] **DCO sign-off present** (Signed-off-by: Real Name &lt;email&gt;)
- [ ] **Commit message explains AI usage**: What was generated, what was manual
- [ ] **Contributor appears to understand** the code (explanation demonstrates knowledge)
- [ ] **AI tool disclosure is appropriate** (Generated-By for substantial, Assisted-By for minor)

## Apply Heightened Scrutiny

Per OpenInfra Foundation AI Policy, apply **extra scrutiny** to AI-generated code:

### Logic and Correctness

- [ ] **Algorithm correctness**: Logic is sound and handles edge cases
- [ ] **No obvious bugs**: Code doesn't have common AI-generation mistakes
- [ ] **Error handling**: All failure paths properly handled
- [ ] **Data validation**: Input validation is thorough
- [ ] **Boundary conditions**: Min/max values, empty inputs, null cases handled
- [ ] **Race conditions**: Concurrent access properly handled (if applicable)

### Security Review

- [ ] **No hard-coded credentials** or secrets
- [ ] **No SQL injection** vulnerabilities
- [ ] **Input sanitization**: User input properly validated/escaped
- [ ] **No command injection** (if using shell commands)
- [ ] **Proper access control**: Authorization checks in place
- [ ] **No information leakage** in error messages or logs
- [ ] **Cryptography**: If used, modern/approved algorithms only

### OpenStack Compliance

- [ ] **Apache 2.0 license header** in all new files
- [ ] **Line length ≤ 79 characters** strictly enforced
- [ ] **No bare except:** (H201)
- [ ] **autospec=True in all mocks** (H210)
- [ ] **Correct mock import** (unittest.mock, not third-party) (H216)
- [ ] **Delayed logging** (H702)
- [ ] **No relative imports** (H304)
- [ ] **Import order correct** (H306)
- [ ] **TODO comments have author** (H101)
- [ ] **No author tags** (H105)

### Code Quality

- [ ] **Follows existing patterns**: Consistent with project conventions
- [ ] **Proper docstrings**: All public functions/classes documented (H404/H405)
- [ ] **Clear variable names**: Self-documenting, not cryptic
- [ ] **Appropriate complexity**: Not overly complex or convoluted
- [ ] **DRY principle**: No unnecessary code duplication
- [ ] **Separation of concerns**: Each function has single responsibility
- [ ] **No dead code**: Commented-out code or unused imports removed

### Testing

- [ ] **Tests provided**: New functionality has test coverage
- [ ] **Tests are meaningful**: Not just checking mocked returns
- [ ] **Edge cases tested**: Boundary conditions, errors, empty inputs
- [ ] **Mock usage correct**: autospec=True, realistic behavior (H210)
- [ ] **Specific assertions**: assertIsNone, assertEqual, not generic assertTrue (H203-H215)
- [ ] **Exception testing**: Specific exceptions, not generic Exception (H202)
- [ ] **Test coverage**: Critical paths are covered

### Documentation

- [ ] **Commit message quality**: Clear explanation of WHY and WHAT
- [ ] **Docstrings complete**: :param, :returns:, :raises: documented
- [ ] **Inline comments**: Complex logic has explanations
- [ ] **No misleading comments**: Comments match actual code behavior
- [ ] **Documentation updated**: If API changes, docs reflect it

## AI-Specific Concerns

### Common AI Mistakes to Check

- [ ] **Hallucinated APIs**: AI didn't invent non-existent functions/modules
- [ ] **Outdated patterns**: Code uses current OpenStack conventions
- [ ] **Copy-paste errors**: Variable names consistent, no placeholder text
- [ ] **Incomplete refactoring**: If renaming occurred, all references updated
- [ ] **Inappropriate libraries**: Only approved dependencies used
- [ ] **License conflicts**: No GPL or incompatible license code patterns

### Verify Understanding

Ask contributor to explain:

- [ ] **Why this approach?** Can they justify the technical decisions?
- [ ] **What are the trade-offs?** Do they understand alternatives?
- [ ] **How does error handling work?** Can they walk through failure scenarios?
- [ ] **What are the limitations?** Are they aware of edge cases?

If contributor cannot explain, **request clarification or changes**.

## OpenStack-Specific Patterns

- [ ] **Context managers**: Used for files, database sessions, locks
- [ ] **oslo.config**: Configuration via CONF, not environment variables
- [ ] **oslo.log**: Logging via oslo_log.log, not standard logging
- [ ] **Exception handling**: Custom exceptions inherit from proper base
- [ ] **i18n**: Translatable strings use _() or_LE()/_LI()/_LW()
- [ ] **No mutable defaults**: `items=None` pattern, not `items=[]` (H232)

## Review Comments

When requesting changes:

### Constructive Feedback

- [ ] **Be specific**: Point to exact lines and explain the issue
- [ ] **Provide rationale**: Explain WHY change is needed (cite hacking rule)
- [ ] **Suggest solution**: Offer guidance on how to fix
- [ ] **Acknowledge AI use**: Recognize value while ensuring quality
- [ ] **Educational tone**: Help contributor learn, not just comply

### Example Comments

**Good:**
> Line 45: This uses a bare except: statement which violates H201.
> Please catch specific exceptions like (ValueError, TypeError) to
> avoid masking unexpected errors. See: https://docs.openstack.org/hacking/

**Bad:**
> This is wrong, fix it.

## Approval Criteria

Only approve if **ALL** of these are true:

- [ ] Code is technically correct and secure
- [ ] Contributor demonstrates understanding of the changes
- [ ] All OpenStack standards met (passes tox -e pep8)
- [ ] AI attribution is honest and appropriate
- [ ] DCO sign-off is present
- [ ] Tests are adequate and pass
- [ ] Documentation is complete and accurate

## Conditional Approval

If minor issues remain:

```text
This looks good overall. Before merging, please address:

1. Add autospec=True to mock.patch on line 42 (H210)
2. Break line 78 to stay under 79 characters
3. Add docstring to _process_item() helper function

With these changes, this will be ready to merge. Thanks for
the contribution and for properly attributing your AI usage!
```

## Rejection Criteria

Reject if ANY of these are true:

- [ ] **Security vulnerability** present
- [ ] **Contributor doesn't understand** the code
- [ ] **AI attribution missing** (policy violation)
- [ ] **DCO sign-off missing** (required)
- [ ] **License conflicts** or proprietary code patterns
- [ ] **Critical bugs** that would break functionality
- [ ] **No tests** for non-trivial functionality

## Final Checks

Before approving:

```bash
# Verify CI passes
# Check for DCO sign-off
git log -1 --pretty=%B | grep "Signed-off-by:"

# Check for AI attribution
git log -1 --pretty=%B | grep -E "(Generated-By|Assisted-By):"

# Verify style checks pass
# (CI should do this, but you can check locally)
git fetch origin
git checkout <change-ref>
tox -e pep8
```

## Post-Approval

- [ ] **Add to review queue**: If additional reviews needed
- [ ] **Watch CI**: Ensure automated tests pass
- [ ] **Follow up**: If you asked for changes, verify they were made

---

**Remember**: AI-generated code requires the same quality standards as
human-written code, plus additional scrutiny for AI-specific risks.
