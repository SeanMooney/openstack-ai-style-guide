---
source_url: Multiple sources consolidated
conversion_date: 2025-10-25
document_title: Developer Certificate of Origin (DCO) - Comprehensive Reference
source_type: Consolidated Documentation
sources:
  - https://openinfra.org/dco/
  - https://docs.openstack.org/contributors/common/dco.html
  - https://developercertificate.org
---

# Developer Certificate of Origin (DCO)

## Overview

The Developer Certificate of Origin (DCO) is a lightweight mechanism to confirm that contributors are entitled to submit code to open source projects[1][2][3]. It provides a legal framework that ensures contributors have the right to provide their contributions under the project's license[2].

The DCO approach has been adopted by major open source projects including the Linux kernel, Docker, Git, and many others[1]. OpenInfra Foundation projects transitioned from Contributor License Agreements (CLAs) to DCO on July 1, 2025[1].

## What is the DCO?

The Developer Certificate of Origin is an attestation attached to every contribution made by every developer[1]. Rather than requiring a separate legal agreement, contributors simply add a `Signed-off-by` statement to their commit message, thereby agreeing to the terms of the DCO[1][2].

This approach eliminates friction for new contributors while maintaining the legal clarity needed for open source projects[1]. It is simpler, more transparent, and aligns with industry best practices[1].

## The Developer Certificate of Origin Text

The full text of the DCO Version 1.1 is as follows[3]:

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

## Understanding the DCO Clauses

### Clause (a): Original Work

This clause covers contributions that you created yourself[2][3]. When you sign off using this clause, you certify that:
- You created the contribution in whole or in part
- You have the legal right to submit it under the project's open source license

### Clause (b): Derivative Work

This clause applies when your contribution is based on existing work[2][3]. You certify that:
- The original work is covered under an appropriate open source license
- You have the right to submit modifications under that license
- You're submitting under the same open source license (unless permitted otherwise)

### Clause (c): Third-Party Contributions

This clause covers situations where someone else provided the contribution to you[2][3]. You certify that:
- The original person certified under (a), (b), or (c)
- You have not modified the contribution

### Clause (d): Public Record

This clause ensures you understand the permanent and public nature of contributions[2][3]. You acknowledge that:
- The project and contribution are public
- A permanent record exists including your personal information
- The contribution may be redistributed consistent with the project's license

## How to Sign Your Commits

### Basic Sign-Off

Every commit you make to projects using DCO must be signed off[2]. Add this line to your commit message[2]:

```
Signed-off-by: Your Name <your.email@example.com>
```

This certifies that you have the right to submit the work and are doing so under the project's license[2].

### Using Git's Sign-Off Flag

Git provides a convenient flag to automatically add the sign-off line[2]:

```bash
git commit -s
```

Or use the long form:

```bash
git commit --signoff
```

## Setting Up Your Git Configuration

### Configure Your Identity

Before signing off commits, ensure your Git identity is properly configured[2]. The `Signed-off-by` line uses the name and email address from your Git configuration[2]:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Verify Your Configuration

Check your current configuration:

```bash
git config --get user.name
git config --get user.email
```

### Identity Requirements

- **Use Your Real Name**: The name and email in your `Signed-off-by` line should match your real identity[2]
- **Match Your Review Account**: For OpenStack projects, your identity should match the name and email configured in your `review.opendev.org (Gerrit)` account[2]
- **Consistency**: Maintain consistent identity across all your contributions[2]

## Commit Message Examples

### Single Author Commit

A typical commit message with DCO sign-off[2]:

```
Add feature X to OpenStack compute

Introduces a new API endpoint for managing compute instances
more efficiently. Includes updated documentation and tests.

Closes-Bug: #12345
Signed-off-by: Your Name <your.email@example.com>
Change-Id: 8244cbaf1c12ddc90843fe204e107192c96f6bb3
```

### Multiple Authors

When multiple people contribute to a commit, each must sign off[2]:

```
Add feature X to OpenStack compute

Introduces a new API endpoint for managing compute instances
more efficiently. Includes updated documentation and tests.

Closes-Bug: #12345
Co-authored-by: Another Contributor <another.contributor@example.com>
Signed-off-by: Your Name <your.email@example.com>
Signed-off-by: Another Contributor <another.contributor@example.com>
Change-Id: 277ad6ef2721a7081a9db10f63353b407c8b1ca8
```

**Note**: Subsequent developers who co-author or help shepherd a contribution must add their own `Signed-off-by` attestation[2]. `Co-authored-by` entries are not required, since `Signed-off-by` is treated as equivalent, but `Co-authored-by` is recommended to accommodate legacy tooling that credits all authors[2].

## Best Practices

### Always Sign Off

- Every commit must include a `Signed-off-by` line[2]
- If you amend a commit or rebase an existing change, you may need to sign off the new commit even if you're not the original author[2]

### Rebasing and Squashing

When rebasing or squashing commits, new commit hashes are generated[2]. This means:
- You must re-sign off the commits[2]
- During interactive rebase, ensure each `pick` or `reword` action includes the `-s` flag if manually running `git commit`[2]

### Interactive Rebase Example

```bash
git rebase -i HEAD~3
# In the editor, for each commit you pick or reword:
# After editing, use: git commit --amend -s
```

## OpenInfra Foundation Transition

### From CLA to DCO

Starting July 1, 2025, OpenInfra Foundation projects transitioned from requiring Contributor License Agreements (CLAs) to using the Developer Certificate of Origin (DCO) approach[1].

### Benefits of DCO Over CLA

- **Lower Friction**: No separate legal documents to sign[1]
- **More Transparent**: The agreement is part of the contribution itself[1]
- **Industry Standard**: Aligns with major open source projects[1]
- **Simpler Process**: Single command to sign off commits[1]

### License Combination

OpenInfra Foundation projects use the Apache License, Version 2.0 in combination with the Developer Certificate of Origin (DCO)[1]. This provides:
- Clear intellectual property licensing for contributions[1]
- Legal protection for both contributors and the project[1]
- Compatibility with enterprise requirements[1]

## Troubleshooting

### Forgotten Sign-Off

If you forget to sign off a commit, you can amend it:

```bash
git commit --amend -s
```

For older commits, use interactive rebase:

```bash
git rebase -i HEAD~N  # N is the number of commits back
# Mark commits for 'edit' in the editor
# For each commit:
git commit --amend -s
git rebase --continue
```

### Wrong Email Address

If you committed with the wrong email address:

1. Update your Git configuration:
```bash
git config user.email "correct.email@example.com"
```

2. Amend the commit:
```bash
git commit --amend -s --reset-author
```

### Multiple Sign-Offs Required

If multiple people worked on a commit, each person should add their sign-off:

```bash
# First author
git commit -s

# Second author (when taking over the commit)
git commit --amend -s
# This adds a second Signed-off-by line
```

## Integration with OpenStack Workflow

### Gerrit Requirements

For OpenStack projects using Gerrit[2]:
- The `Signed-off-by` name and email must match your Gerrit account[2]
- Gerrit may reject commits without proper sign-off
- The DCO check runs automatically on each patchset

### Automated Checks

Many projects implement automated checks to ensure DCO compliance:
- CI systems verify each commit has a `Signed-off-by` line
- Email addresses are validated against known contributors
- Missing sign-offs block the merge process

## Getting Help

### OpenInfra Foundation Support

If you need assistance with the DCO process or have questions about contributing to OpenInfra Foundation projects[1]:
- **Email**: Contact the foundation directly for guidance[1]
- **Documentation**: Refer to project-specific contribution guides
- **Community**: Ask in project IRC channels or mailing lists

### Common Questions

**Q: Do I need to sign off on every commit in a series?**
A: Yes, every commit must be signed off individually[2].

**Q: What if I'm committing code from someone else?**
A: Include their `Signed-off-by` line and add your own, certifying under clause (c)[2][3].

**Q: Can I use a pseudonym?**
A: No, you must use your real name and email[2].

**Q: What happens to old CLA signatures?**
A: Previous CLAs remain valid for past contributions, but new contributions use DCO[1].

## Legal Considerations

### Copyright Retention

The DCO does not transfer copyright[1][2][3]. Contributors retain copyright to their work while granting the project rights under the specified open source license[2].

### Employer Rights

If you're contributing as part of your employment:
- Ensure your employer permits you to contribute[2]
- You may need employer authorization for substantial contributions[2]
- The sign-off certifies you have the right to contribute on behalf of your employer[2]

### Indefinite Record

The DCO explicitly states that contribution records, including personal information, are maintained indefinitely[2][3]. This ensures:
- Long-term project viability
- Clear provenance of all code
- Ability to track contribution history

## References

[1] OpenInfra Foundation DCO Page: https://openinfra.org/dco/
    - Section: Overall DCO Page
    - Retrieved: 2025-10-25

[2] OpenStack Contributors Guide - DCO: https://docs.openstack.org/contributors/common/dco.html
    - Section: Complete DCO Guide
    - Retrieved: 2025-10-25

[3] Developer Certificate of Origin: https://developercertificate.org
    - Section: Official DCO Text
    - Retrieved: 2025-10-25
