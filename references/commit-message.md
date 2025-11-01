---
source_url: https://wiki.openstack.org/wiki/GitCommitMessages
conversion_date: 2025-10-25
document_title: Git Commit Good Practice
source_type: OpenStack Wiki Documentation
---

# Git Commit Good Practice

This document provides guidance on creating well-structured Git commits for OpenStack projects[1]. It is based on
experience from code development, bug troubleshooting, and code review across projects including libvirt, QEMU, and
OpenStack Nova[1].

## Executive Summary

This document demonstrates the value of splitting changes into individual commits and writing good commit messages[1].
When reviewing changes in Gerrit, reviewers should examine not only code correctness but also:

- Quality of commit messages
- Proper separation of logical changes
- Separation of whitespace changes from functional changes
- Separation of refactoring from functional changes[1]

The fundamental principle: Software is "read mostly, write occasionally," so optimize for long-term maintainability by
the community rather than convenience of a single author[1].

## Structural Split of Changes

### Cardinal Rule

There should be only one "logical change" per commit[1].

**Reasons for this rule:**

- Smaller code changes are quicker and easier to review
- Flawed changes are easier to revert when isolated
- Git bisect troubleshooting is more effective with small, well-defined changes
- Git annotate/blame provides clearer code history[1]

### Things to Avoid When Creating Commits

#### Mixing Whitespace Changes with Functional Code Changes

Whitespace changes obscure functional changes, making review harder[1].

Solution: Create two commits - one for whitespace, one for functional changes[1].

#### Mixing Two Unrelated Functional Changes

Makes review harder and complicates potential reverts[1].

#### Sending Large New Features in a Single Giant Commit

New features often involve refactoring. Refactoring should be in separate commits from new feature implementation[1].

Guidelines for feature commits:

- Separate commits for refactoring existing code
- Separate commits for new internal APIs/classes
- Separate commits for public HTTP APIs or RPC interfaces from internal implementation
- Use `APIImpact` flag for patches affecting public HTTP APIs[1]

Basic rule:

```text
If a code change can be split into a sequence of patches/commits, then it should be split.
Less is not more. More is more.
```

### Examples of Bad Practice

#### Example 1: Mixed Changes in Refactoring

```text
commit ae878fc8b9761d099a4145617e4a48cbeb390623
Author: [removed]
Date:   Fri Jun 1 01:44:02 2012 +0000

  Refactor libvirt create calls

   * minimizes duplicated code for create
   * makes wait_for_destroy happen on shutdown instead of undefine
   * allows for destruction of an instance while leaving the domain
   * uses reset for hard reboot instead of create/destroy
   * makes resume_host_state use new methods instead of hard_reboot
   * makes rescue/unrescue not use hard reboot to recreate domain
```

Problems:

- At least two independent changes: (1) switch to "reset" API for "hard_reboot" and (2) adjustment to internal
  driver methods
- The switch to libvirt 'reset' API was buried in refactoring, causing reviewers to miss a new libvirt version
  dependency
- Trivial revert is impossible due to entangled unrelated changes[2]

#### Example 2: Feature Implementation Mixed with Refactoring

```text
commit e0540dfed1c1276106105aea8d5765356961ef3d
Author: [removed]
Date:   Wed May 16 15:17:53 2012 +0400

  blueprint lvm-disk-images

  Add ability to use LVM volumes for VM disks.
  [abbreviated]
```

Problems:

This commit entangles significant code refactoring with new LVM feature code, making it hard to identify regressions
in QCow2/Raw image support[2].

Should have been split into:

1. Replace 'use_cow_images' config FLAG with 'libvirt_local_images_type' FLAG (with backward compatibility)
2. Creation of internal "Image" class and subclasses for Raw & QCow2
3. Refactor libvirt driver to use new "Image" class APIs
4. Introduce new "LVM" Image class implementation[2]

### Examples of Good Practice

#### Example 1: Separated API and Policy Changes

```text
commit 3114a97ba188895daff4a3d337b2c73855d4632d
Author: [removed]
Date:   Mon Jun 11 17:16:10 2012 +0100

  Update default policies for KVM guest PIT & RTC timers

commit 573ada525b8a7384398a8d7d5f094f343555df56
Author: [removed]
Date:   Tue May 1 17:09:32 2012 +0100

  Add support for configuring libvirt VM clock and timers
```

These two changes provide support for configuring KVM guest timers. The introduction of new APIs for creating libvirt
XML is clearly separated from the change to KVM guest creation policy[3].

#### Example 2: Incremental RPC Refactoring

```text
commit 62bea64940cf629829e2945255cc34903f310115
Author: [removed]
Date:   Fri Jun 1 14:49:42 2012 -0400

  Add a comment to rpc.queue_get_for().

commit cf2b87347cd801112f89552a78efabb92a63bac6
Author: [removed]
Date:   Wed May 30 14:57:03 2012 -0400

  Add shared_storage_test methods to compute rpcapi.
...
  Add get_instance_disk_info to the compute rpcapi.
...
  [many more commits]
```

This sequence refactored the entire RPC API layer to allow pluggable messaging implementations. Splitting into many
commits enabled meaningful code review and tracking of regressions at each step[3].

## Information in Commit Messages

### Key Principles

#### Do Not Assume the Reviewer Understands What the Original Problem Was

The commit message should clearly state the original problem. The bug is historical context for how the problem was
identified[4].

#### Do Not Assume the Reviewer Has Access to External Web Services or Sites

Commit messages should be self-contained. In 6 months, when troubleshooting offline, the message must provide all
necessary context without access to bug trackers or blueprint documents[4].

#### Do Not Assume the Code is Self-Evident or Self-Documenting

Always document the original problem and how it is being fixed, except for obvious typos or whitespace-only commits[4].

#### Describe Why a Change is Being Made

Document the intent and motivation behind changes, not just how the code was written. Describe overall code structure
for large changes, but focus on the reasoning[4].

#### Read the Commit Message to See if it Hints at Improved Code Structure

If describing a commit reveals it should have been split into multiple parts, rebase and split it[4].

#### Ensure Sufficient Information to Decide Whether to Review

Gerrit email alerts contain minimal information. The commit message must alert potential reviewers that this patch
requires their attention[4].

#### The First Commit Line is the Most Important

The first line appears in email subject lines, git annotate, gitk, merge commits, and many other space-constrained
contexts. It should summarize the change and identify the affected component [e.g., "libvirt"](4).

#### Describe Any Limitations of the Current Code

Mention future scope for improvements or known limitations to show the broader picture has been considered[4].

#### Do Not Assume the Reviewer Has Knowledge of the Tests Executed

For changes requiring manual testing, include a 'Test Plan' section listing test cases performed[4].

#### Do Not Include Patch Set-Specific Comments

Comments like "Patch set 2: rebased" or "Added unit tests" should go in Gerrit comments, not commit messages. They
are not relevant after merge[4].

Main rule:

```text
The commit message must contain all the information required to fully understand & review
the patch for correctness. Less is not more. More is more.
```

### Including External References

Commit messages include metadata for machine interpretation[5]:

### Change-Id

- Unique hash generated by Git commit hook
- Used by Gerrit to track patch versions
- Do not change when rebasing[5]

### Bug References

For **Storyboard:**

```text
Story: 1234567
Task: 98765
```

- Use both `Story` and `Task` if commit fully implements the task
- Use only `Story` if merely related without implementing tasks[5]

For **Launchpad:**

```text
Closes-Bug: #1234567    - use if commit fully fixes and closes the bug
Partial-Bug: #1234567   - use if commit is only a partial fix
Related-Bug: #1234567   - use if commit is merely related to the bug
```

### Blueprint

```text
Implements: blueprint blueprint-name
```

References a Launchpad blueprint for feature implementation[5].

### DocImpact

```text
DocImpact
```

Use when patch contains documentation or requires documentation updates. Include as much information as possible.
Gerrit creates a bug for the openstack-manuals project[5].

### APIImpact

```text
APIImpact
```

Use when patch creates, updates, or deletes a public HTTP API or changes API behavior. All associated reviews can be
found in [this report](https://review.openstack.org/#/q/status:open+AND+(message:ApiImpact+OR+message:APIImpact),n,z)
for API Working Group review[5].

### SecurityImpact

```text
SecurityImpact
```

Indicates change has security implications requiring OpenStack Security Group review[5].

### UpgradeImpact

```text
UpgradeImpact
```

Indicates change has upgrade implications for continuous deployment or N to N+1 upgrades. Consider updating 'Upgrade
Notes' in release notes[5].

### Co-Authored-By

```text
Co-Authored-By: name <name@example.com>
```

Recognizes multiple authors. Statistics tools should observe this convention[5].

### Signed-off-by (REQUIRED)

All authors and contributors must adhere to the
[Developer Certificate of Origin](https://developercertificate.org/) and indicate this with `Signed-off-by` in commit
messages[5].

**Creating signed commits:**

```bash
git commit -s
```

On subsequent patches, preserve all prior `Signed-off-by` lines[5].

### Summary of Git Commit Message Structure

**Structure:**

1. Brief description of change in first line (50 characters max, no period)
2. Single blank line
3. Detailed description in following lines (wrap at 72 characters)
4. Optional 'Test Plan' section with test case titles
5. Metadata at the very end: Change-Id, Story/Task or Closes-Bug/blueprint lines[6]

**vim configuration for line wrapping:**

- Copy example vimrc (e.g., `/usr/share/vim/vim74/vimrc_example.vim`) to `~/.vimrc`
- Re-wrap paragraph: press Escape, ensure cursor is in paragraph, type `gqip`[6]

**Example commit message:**

```text
Switch libvirt get_cpu_info method over to use config APIs

The get_cpu_info method in the libvirt driver currently uses
XPath queries to extract information from the capabilities
XML document. Switch this over to use the new config class
LibvirtConfigCaps. Also provide a test case to validate
the data being returned.

DocImpact
Closes-Bug: #1003373
Implements: blueprint libvirt-xml-cpu-model
Signed-off-by: Stacky McStackFace <stacky@openstack.org>
Change-Id: I4946a16d27f712ae2adf8441ce78e6c0bb0bb657
```

### Examples of Bad Practice

#### Example 1: Missing Import Details

```text
commit 468e64d019f51d364afb30b0eed2ad09483e0b98
Author: [removed]
Date:   Mon Jun 18 16:07:37 2012 -0400

  Fix missing import in compute/utils.py

  Fixes bug 1014829
  Signed-off-by: Stacky McStackFace <stacky@openstack.org>
```

Problem: Does not mention what imports were missing or why they were needed[7].

Better version:

```text
Add missing import of 'exception' in compute/utils.py

nova/compute/utils.py makes a reference to exception.NotFound,
however exception has not been imported.
```

#### Example 2: Missing Format Details

```text
commit 2020fba6731634319a0d541168fbf45138825357
Author: [removed]
Date:   Fri Jun 15 11:12:45 2012 -0600

 Present correct ec2id format for volumes and snaps

 Fixes bug 1013765
 * Add template argument to ec2utils.id_to_ec2_id() calls

 Signed-off-by: Stacky McStackFace <stacky@openstack.org>
 Change-Id: I5e574f8e60d091ef8862ad814e2c8ab993daa366
```

Problem: Does not mention current (broken) format, new fixed format, or what earlier change caused the regression[7].

Better version:

```text
Present correct ec2id format for volumes and snaps

During the volume uuid migration, done by changeset XXXXXXX,
ec2 id formats for volumes and snapshots was dropped and is
now using the default instance format (i-xxxxx). These need
to be changed back to vol-xxx and snap-xxxx.

Adds a template argument to ec2utils.id_to_ec2_id() calls

Fixes bug 1013765
Signed-off-by: Stacky McStackFace <stacky@openstack.org>
```

#### Example 3: Missing Context and Behavior

```text
commit f28731c1941e57b776b519783b0337e52e1484ab
Author: [removed]
Date:   Wed Jun 13 10:11:04 2012 -0400

  Add libvirt min version check.

  Fixes LP Bug #1012689.

  Signed-off-by: Stacky McStackFace <stacky@openstack.org>
  Change-Id: I91c0b7c41804b2b25026cbe672b9210c305dc29b
```

Problem: Only documents what was done, not why. Missing information about what changeset introduced the requirement
and what happens when the check fails[7].

Better version:

```text
Add libvirt version check, min 0.9.7

The commit XXXXXXXX introduced use of the 'reset' API
which is only available in libvirt 0.9.7 or newer. Add a check
performed at startup of the compute server against the libvirt
connection version. If the version check fails the compute
service will shutdown.

Fixes LP Bug #1012689.

Signed-off-by: Stacky McStackFace <stacky@openstack.org>
Change-Id: I91c0b7c41804b2b25026cbe672b9210c305dc29b
```

### Examples of Good Practice

#### Example 1: Complete Timer Policy Change

```text
commit 3114a97ba188895daff4a3d337b2c73855d4632d
Author: [removed]
Date:   Mon Jun 11 17:16:10 2012 +0100

  Update default policies for KVM guest PIT & RTC timers

  The default policies for the KVM guest PIT and RTC timers
  are not very good at maintaining reliable time in guest
  operating systems. In particular Windows 7 guests will
  often crash with the default KVM timer policies, and old
  Linux guests will have very bad time drift

  Set the PIT such that missed ticks are injected at the
  normal rate, ie they are delayed

  Set the RTC such that missed ticks are injected at a
  higher rate to "catch up"

  This corresponds to the following libvirt XML

    <clock offset='utc'>
      <timer name='pit' tickpolicy='delay'/>
      <timer name='rtc' tickpolicy='catchup'/>
    </clock>

  And the following KVM options

    -no-kvm-pit-reinjection
    -rtc base=utc,driftfix=slew

  This should provide a default configuration that works
  acceptably for most OS types. In the future this will
  likely need to be made configurable per-guest OS type.

  Closes-Bug: #1011848

  Signed-off-by: Stacky McStackFace <stacky@openstack.org>
  Change-Id: Iafb0e2192b5f3c05b6395ffdfa14f86a98ce3d1f
```

Notable aspects:

- Describes original problem (bad KVM defaults)
- Describes functional change (new PIT/RTC policies)
- Describes result of change (new XML/QEMU args)
- Describes scope for future improvement (per-OS type config)
- Uses Closes-Bug notation[8]

#### Example 2: CPU Architecture Filter

```text
commit 31336b35b4604f70150d0073d77dbf63b9bf7598
Author: [removed]
Date:   Wed Jun 6 22:45:25 2012 -0400

  Add CPU arch filter scheduler support

  In a mixed environment of running different CPU architecutres,
  one would not want to run an ARM instance on a X86_64 host and
  vice versa.

  This scheduler filter option will prevent instances running
  on a host that it is not intended for.

  The libvirt driver queries the guest capabilities of the
  host and stores the guest arches in the permitted_instances_types
  list in the cpu_info dict of the host.

  The Xen equivalent will be done later in another commit.

  The arch filter will compare the instance arch against
  the permitted_instances_types of a host
  and filter out invalid hosts.

  Also adds ARM as a valid arch to the filter.

  The ArchFilter is not turned on by default.

  Signed-off-by: Stacky McStackFace <stacky@openstack.org>
  Change-Id: I17bd103f00c25d6006a421252c9c8dcfd2d2c49b
```

Notable aspects:

- Describes problem scenario (mixed arch deployments)
- Describes intent of fix (scheduler filter on arch)
- Describes rough architecture (how libvirt returns arch)
- Notes limitations [work needed on Xen](8)

#### Example 3: Parallel Collection Tool with Test Plan

```text
commit 71f0e301132a7576f238fc1e51ae0ebc399dce43
Author: [removed]
Date:   Wed Jul 21 08:47:13 2021 -0400

  Add parallel option to the collect tool

  The current implementation of collect cycles through
  the specified host list, one after the other.

  This update adds a parallel (-p|--parallel) option to
  collect with the goal to decrease the time it takes to
  collect logs/data from all hosts in larger systems.

  This update does not change any of the current collect
  default options. The collect tool will take advantage
  of this new feature if the -p or --parallel option is
  specified on the command line when starting collect.

  Unless specified, all of the following test cases
  were executed for both serial and parallel collects.

  Test Plan:

  PASS: Verify collect output and logging

  Failure Cases: Failure Handling = FH

  PASS: Verify collect FH for an offline host
  PASS: Verify collect FH for host that recently rebooted
  PASS: Verify collect FH for host that reboots during collect
  PASS: Verify collect FH for host mgmnt network drop during collect
  PASS: Verify collect FH of various bad command line options
  PASS: Verify parallel collect overall timeout failure handling

  Regression:

  PASS: Verify dated collect
  PASS: Verify handling of unknown host
  PASS: Verify ^C|TERM|KILL running collect removes all child processes
  PASS: Verify Single host collect (any host)
  PASS: Verify Listed hosts collect (many different groupings)

  Soak:

  PASS: Verify repeated collects (50+) until after local fs is full

  Signed-off-by: Stacky McStackFace <stacky@openstack.org>
  Change-Id: I91814d14341cdc438a6d5af999b6c12d39c7d97c
```

Notable aspects:

- Describes original limitation (sequential collection)
- Describes functional change (parallel option)
- Describes intent (decrease time)
- Describes tests executed [comprehensive Test Plan](8)

## References

[1] https://wiki.openstack.org/wiki/GitCommitMessages
    - Section: Git Commit Good Practice
    - Retrieved: 2025-10-25

[2] https://wiki.openstack.org/wiki/GitCommitMessages
    - Section: Examples of bad practice
    - Retrieved: 2025-10-25

[3] https://wiki.openstack.org/wiki/GitCommitMessages
    - Section: Examples of good practice
    - Retrieved: 2025-10-25

[4] https://wiki.openstack.org/wiki/GitCommitMessages
    - Section: Information in commit messages
    - Retrieved: 2025-10-25

[5] https://wiki.openstack.org/wiki/GitCommitMessages
    - Section: Including external references
    - Retrieved: 2025-10-25

[6] https://wiki.openstack.org/wiki/GitCommitMessages
    - Section: Summary of Git commit message structure
    - Retrieved: 2025-10-25

[7] https://wiki.openstack.org/wiki/GitCommitMessages
    - Section: Some examples of bad practice
    - Retrieved: 2025-10-25

[8] https://wiki.openstack.org/wiki/GitCommitMessages
    - Section: Examples of good practice (commit messages)
    - Retrieved: 2025-10-25
