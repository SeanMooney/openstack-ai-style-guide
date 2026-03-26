=============================
OpenStack AI Style Guide Notes
=============================

This file documents intentional patterns that automated code review tools may
flag as issues. Reviewers and AI review agents should consult this file before
raising findings about the patterns listed here.

Known Intentional Patterns
==========================

Plugin Manifest: No ``agents_dir`` or ``skills_dir`` Fields
------------------------------------------------------------

``.claude-plugin/plugin.json`` does not declare ``agents_dir`` or
``skills_dir``. This is intentional.

Claude Code auto-discovers agents from ``agents/`` and skills from ``skills/``
by default. Explicit fields in ``plugin.json`` are only required when using
non-default directory names or paths. The repository uses the default layout,
so no manifest fields are needed.

**Do not flag** the absence of ``agents_dir``/``skills_dir`` as a missing
configuration issue.

Ansible: Jinja2 Variable Cross-References in ``defaults/main.yaml``
--------------------------------------------------------------------

Role defaults files (e.g. ``roles/ai_code_review/defaults/main.yaml``) contain
variables that reference other variables defined in the same file, for example::

    ai_code_review_style_guide_quick_rules: >-
      {{ ai_code_review_style_guide_project }}/docs/quick-rules.md

Ansible resolves variable references at play time, not at load time. Intra-file
cross-references in ``defaults/main.yaml`` are valid and work correctly. This is
a standard Ansible pattern, not a bug.

**Do not flag** variable self-references within defaults files as a Jinja2 error
or risk.

Ansible: ``regex_search`` on Possibly Empty ``stdout``
------------------------------------------------------

The post-task in ``playbooks/teim-code-review/run.yaml`` that computes
``teim_review_status`` uses ``regex_search`` against ``teim_review_stats.stdout``.
The task already guards against empty output with::

    {%- set raw = teim_review_stats.stdout | default('') -%}
    {%- set crit = (raw | regex_search('Critical: (\d+)', '\\1') or ['0'])[0] | int -%}

The ``| default('')`` filter handles ``None``/undefined stdout, and the
``or ['0']`` fallback handles ``regex_search`` returning ``None`` when there is
no match. Empty stdout is fully handled.

**Do not flag** this ``regex_search`` usage as unsafe or in need of additional
guards.
