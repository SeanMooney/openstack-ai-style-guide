# Bad OpenStack Commit Message Examples

Examples of improperly formatted commit messages and why they're problematic.

## Example 1: Missing AI Attribution

```text
Add resource cleanup to compute manager

The compute manager was not properly releasing resources when
instances were terminated. This commit adds cleanup code.

Signed-off-by: Jane Doe <jane.doe@example.com>
Closes-Bug: #2001234
Change-Id: I1234567890abcdef1234567890abcdef12345678
```text

**Problems:**

- ❌ No AI attribution (Generated-By or Assisted-By) despite being AI-generated
- ❌ Body doesn't explain WHY (what problem does this solve?)
- ❌ Body doesn't explain WHAT changes were made
- ❌ No context about how AI was used
- ❌ Too vague - doesn't help reviewers understand the change

## Example 2: Missing DCO Sign-off

```text
Fix memory leak in compute manager

Added proper resource cleanup in the instance deletion path to
prevent memory leaks in long-running compute services.

I used Claude Code to generate the cleanup implementation.

Generated-By: claude-code
Closes-Bug: #2001234
Change-Id: I1234567890abcdef1234567890abcdef12345678
```text

**Problems:**

- ❌ **CRITICAL**: Missing DCO sign-off (Signed-off-by:)
- ❌ This commit will be REJECTED
- ✅ Has AI attribution (good)
- ✅ Has bug reference (good)

## Example 3: Wrong Subject Line Format

```text
Fixed the memory leak that was occurring in the compute manager during instance deletion.

The compute manager had a memory leak. I fixed it by adding
cleanup code. The leak was causing problems in production.

Generated-By: claude-code
Signed-off-by: Jane Doe <jane.doe@example.com>
Closes-Bug: #2001234
Change-Id: I1234567890abcdef1234567890abcdef12345678
```text

**Problems:**

- ❌ Subject line is 82 characters (limit is 50)
- ❌ Subject line is past tense ("Fixed"), should be imperative ("Fix")
- ❌ Subject line has period at end (should not)
- ❌ Body is too casual/conversational
- ❌ Doesn't explain technical approach

**Correct Subject:**

```text
Fix memory leak in compute manager
```text

## Example 4: Vague AI Attribution

```text
Add feature

Added a new feature to the system.

Generated-By: ai
Signed-off-by: John Smith <john.smith@example.com>
Change-Id: I2345678901bcdef2345678901bcdef234567890
```text

**Problems:**

- ❌ Subject too vague ("Add feature" - what feature?)
- ❌ Body doesn't explain what the feature is
- ❌ Body doesn't explain why it's needed
- ❌ "Generated-By: ai" is too vague (specify the tool)
- ❌ No explanation of what AI generated vs manual work
- ❌ No external references (bug, blueprint, etc.)

## Example 5: Missing Context for AI Usage

```text
Implement multi-queue virtio support

Adds multi-queue virtio network device support for better
network performance with multiple vCPUs.

Generated-By: chatgpt
Signed-off-by: Alice Johnson <alice.j@example.com>
Implements: blueprint multi-queue-virtio
Change-Id: I3456789012cdef3456789012cdef345678901234
```text

**Problems:**

- ❌ No explanation of what AI generated
- ❌ No explanation of manual modifications
- ❌ Doesn't demonstrate contributor understands the code
- ❌ Reviewer can't assess how much to scrutinize
- ⚠️  Missing "how" explanation for complex feature

**Better Version Should Include:**

- What context/prompts were given to the AI
- What specific code the AI generated
- What you modified or added manually
- Technical decisions you made

## Example 6: Commit Message Doesn't Match Commit Type

```text
Update documentation

Code changes to add new feature.

Assisted-By: github-copilot
Signed-off-by: Bob Martinez <bob.martinez@example.com>
Change-Id: I4567890123def4567890123def456789012345678
```text

**Problems:**

- ❌ Subject says "Update documentation" but body says "code changes"
- ❌ Wrong AI attribution (substantial code ≠ Assisted-By)
- ❌ Body too short - doesn't explain what, why, or how
- ❌ No external references

**Fix:**

- If substantial code: use "Generated-By"
- Subject should match the actual change
- Body must explain the change adequately

## Example 7: Horrible Everything

```text
updated stuff

i fixed some things in the code that were broken. used chatgpt to help.

Change-Id: I5678901234ef5678901234ef567890123456789012
```text

**Problems:**

- ❌ Subject is lowercase (should be capitalized)
- ❌ Subject is past tense ("updated")
- ❌ Subject is vague ("stuff")
- ❌ Body is lowercase and casual
- ❌ Body doesn't explain anything specific
- ❌ **Missing DCO sign-off** (CRITICAL)
- ❌ No proper AI attribution format
- ❌ No bug/blueprint reference
- ❌ Would be immediately rejected

## Example 8: Too Much Detail in Subject

```text
Fix race condition in network port allocation code by adding proper locking around check-and-update operations

[Body omitted for brevity]

Signed-off-by: Carol Zhang <carol.zhang@example.com>
```text

**Problems:**

- ❌ Subject is 104 characters (limit is 50)
- ⚠️  Details belong in body, not subject
- ❌ Missing AI attribution (if AI was used)

**Correct Subject:**

```text
Fix race in network port allocation
```text

## Example 9: Missing Important Information

```text
Add cleanup code

Added resource cleanup.

Generated-By: claude-code
Signed-off-by: David Lee <david.lee@example.com>
Change-Id: I6789012345f6789012345f678901234567890123
```text

**Problems:**

- ❌ No explanation of WHY (what problem does this solve?)
- ❌ No explanation of WHAT resources are being cleaned up
- ❌ No explanation of WHERE in the code
- ❌ No context for AI usage
- ❌ No bug reference (this fixes a bug, should have Closes-Bug)
- ❌ Reviewer has no context to review effectively

## Example 10: Incorrect Use of Assisted-By

```text
Implement entire authentication system

Complete rewrite of the authentication system using OAuth2.
Includes token management, role-based access control, and
session handling.

Assisted-By: chatgpt
Signed-off-by: Emily White <emily.white@example.com>
Implements: blueprint oauth2-auth
Change-Id: I7890123456f7890123456f789012345678901234
```text

**Problems:**

- ❌ **Wrong AI attribution**: Complete rewrite = Generated-By, not Assisted-By
- ❌ Doesn't explain what AI generated vs manual
- ❌ Doesn't explain the technical approach
- ⚠️  Complex feature needs more explanation

**Fix:**

- Use "Generated-By:" for substantial code generation
- Explain specifically what the AI created
- Describe your manual additions/modifications

## Example 11: Missing Signed-off-by Name

```text
Fix typo in documentation

Fixed spelling error in API documentation.

Generated-By: claude-code
Signed-off-by: <>
Change-Id: I8901234567f8901234567f890123456789012345
```text

**Problems:**

- ❌ **CRITICAL**: Empty Signed-off-by (requires real name and email)
- ❌ Must use your actual name, not anonymous
- ❌ This violates DCO requirements

**Fix:**

```text
Signed-off-by: Your Real Name <your.email@example.com>
```text

## Example 12: No Explanation of Manual Changes

```text
Add network isolation feature

Implemented network isolation for tenant networks using
VLANs and security groups.

Generated-By: claude-code
Signed-off-by: Frank Brown <frank.brown@example.com>
Implements: blueprint network-isolation
Change-Id: I9012345678f9012345678f901234567890123456
```text

**Problems:**

- ❌ Says "Generated-By" but doesn't explain what was generated
- ❌ No explanation of manual modifications
- ❌ Doesn't demonstrate understanding of the code
- ❌ Reviewer doesn't know how much was AI vs human
- ⚠️  Complex feature needs technical approach explanation

**What Should Be Added:**

- What prompts/context you gave the AI
- What code the AI generated
- What you modified, added, or fixed manually
- Why you made those manual changes
- Technical decisions and trade-offs

---

## Common Anti-Patterns Summary

### Subject Line Issues

- Past tense instead of imperative
- Too long (>50 characters)
- Too vague
- Has period at end
- Not capitalized

### Body Issues

- Doesn't explain WHY
- Doesn't explain WHAT
- Too vague or casual
- Missing AI context
- No technical approach for complex changes

### AI Attribution Issues

- Missing entirely
- Wrong type (Generated-By vs Assisted-By)
- No explanation of what AI did
- No explanation of manual work
- Too vague ("ai" instead of tool name)

### Required Elements Missing

- DCO sign-off (Signed-off-by:)
- Real name in sign-off
- Bug/blueprint reference
- Change-Id (added by hook, but check it's there)

### Content Issues

- Doesn't demonstrate understanding
- Missing context for reviewers
- No mention of testing
- No mention of limitations or future work

---

## How to Fix Bad Commit Messages

If you realize your commit message is bad:

```textbash
# Amend the most recent commit
git commit --amend -s

# For older commits, use interactive rebase
git rebase -i HEAD~N  # N = number of commits back
# Mark commits for 'reword' in the editor
# Update each message as prompted
```text

**Important:** Always re-sign with `-s` when amending!
