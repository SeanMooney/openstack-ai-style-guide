# OpenStack AI Style Guide - Authoritative References

This directory contains converted versions of authoritative source documents that inform the OpenStack AI Style Guide.

## Available References

### 1. `ai-policy.md`
**Source:** [OpenInfra Foundation AI Policy](https://openinfra.org/legal/ai-policy)
**Retrieved:** 2025-10-25
**Status:** Official OpenInfra Foundation Policy

**Key Content:**
- AI contribution requirements (Generated-By vs Assisted-By)
- Contributor checklist for AI usage
- Reviewer checklist for AI-generated code
- Key principles: human-in-loop, treat as untrusted source
- Tool configuration requirements

**Why Important:** This is the **official policy** governing all AI-generated contributions to OpenInfra Foundation projects, including OpenStack.

**Use Cases:**
- Understanding AI attribution requirements
- Configuring AI tools for compliance
- Reviewing AI-generated contributions
- Writing commit messages with proper labels

### 2. `dco.md`
**Source:** Multiple sources consolidated:
- [OpenInfra Foundation DCO Page](https://openinfra.org/dco/)
- [OpenStack Contributors Guide - DCO](https://docs.openstack.org/contributors/common/dco.html)
- [Developer Certificate of Origin](https://developercertificate.org)

**Retrieved:** 2025-10-25
**Status:** Mandatory Requirement (Effective July 1, 2025 - NOW IN EFFECT)

**Key Content:**
- Full text of DCO Version 1.1
- Explanation of each DCO clause
- How to sign off commits (git commit -s)
- Git configuration requirements
- Troubleshooting common issues

**Why Important:** **DCO sign-off is REQUIRED** for all contributions. Missing DCO will result in immediate rejection.

**Use Cases:**
- Setting up Git for DCO compliance
- Understanding what you certify when signing off
- Troubleshooting DCO-related issues
- Training new contributors

### 3. `hacking.md`
**Source:** [OpenStack Hacking Style Guide](https://opendev.org/openstack/hacking/raw/commit/abff65f29b7b00d38bce651a546b05a3eb27b71c/HACKING.rst)
**Commit:** abff65f29b7b00d38bce651a546b05a3eb27b71c
**Retrieved:** 2025-10-25
**Status:** Authoritative OpenStack Style Rules

**Key Content:**
- Complete list of H-codes (H101, H201, H210, etc.)
- OpenStack-specific Python conventions
- Import organization rules (H301, H303, H304, H306)
- Docstring requirements (H401, H403, H404, H405)
- Testing requirements (H202, H203, H210, H214, H216)
- Licensing requirements (H102, H103, H104)

**Why Important:** These are the **actual rules** enforced by OpenStack CI. Code that violates these rules will fail automated checks.

**Use Cases:**
- Understanding specific hacking violations
- Configuring linters and AI tools
- Writing compliant code
- Debugging CI failures

### 4. `pep8.md`
**Source:** [PEP 8 - Style Guide for Python Code](https://raw.githubusercontent.com/python/peps/refs/heads/main/peps/pep-0008.rst)
**Retrieved:** 2025-10-25
**Status:** Python Community Standard (Foundation for OpenStack style)

**Key Content:**
- Python code layout and formatting
- Indentation rules (4 spaces)
- Maximum line length (79 characters)
- Import conventions
- Naming conventions
- Programming recommendations
- Whitespace rules

**Why Important:** PEP 8 is the **foundation** of Python style. OpenStack builds on PEP 8 with additional hacking rules.

**Use Cases:**
- Understanding core Python style principles
- Learning rationale behind formatting rules
- Reference for Python-wide conventions
- Resolving style questions

### 5. `commit-message.md`
**Source:** [OpenStack Git Commit Messages Wiki](https://wiki.openstack.org/wiki/GitCommitMessages)
**Retrieved:** 2025-10-25
**Status:** Official OpenStack Commit Message Guidelines

**Key Content:**
- Structural split of changes (one logical change per commit)
- Cardinal rule: separate whitespace, refactoring, and functional changes
- Commit message information requirements (WHY, WHAT, HOW)
- Subject line format (50 characters max, imperative mood)
- Body wrapping (72 characters)
- Self-contained messages (no external dependencies)
- Test Plan section for manual testing
- Metadata tags (Closes-Bug, Implements, DocImpact, APIImpact, etc.)
- DCO sign-off requirements (Signed-off-by)
- Examples of good and bad practice

**Why Important:** These are the **official OpenStack guidelines** for creating well-structured commits with proper messages. Following these ensures your commits pass review and provide long-term value.

**Use Cases:**
- Writing commit messages for OpenStack projects
- Understanding commit structure best practices
- Learning proper metadata tag usage
- Reviewing commit quality
- Training AI tools on commit message format

## Document Conversion Process

These documents were converted from their original formats to markdown for AI consumption:

1. **Fetch Original Source:** Downloaded from authoritative URL
2. **Convert to Markdown:** HTML/RST → Markdown (preserving structure)
3. **Add Metadata:** Source URL, retrieval date, document type
4. **Add Citations:** Section references for traceability
5. **Quality Check:** Verify accuracy and completeness

## Document Updates

### Update Frequency

- **ai-policy.md:** Check quarterly (OpenInfra Foundation updates)
- **dco.md:** Rarely changes (stable specification)
- **hacking.md:** Check monthly (OpenStack releases)
- **pep8.md:** Check semi-annually (Python core updates)
- **commit-message.md:** Check quarterly (OpenStack community updates)

### How to Update

When updating reference documents:

1. **Check Source for Changes:**
   ```bash
   # Compare current version to source
   diff <(curl -sL SOURCE_URL) references/document.md
   ```

2. **Document Changes:**
   - Update `conversion_date` in frontmatter
   - Note what changed in commit message
   - Update relevant sections in main guides

3. **Update Dependent Files:**
   - `docs/comprehensive-guide.md`
   - `docs/quick-rules.md`
   - Templates and examples as needed

4. **Create PR:**
   ```bash
   git add references/document.md
   git commit -s -m "Update reference: document-name

   Updated document-name reference from authoritative source.
   Changes include:
   - DESCRIPTION_OF_CHANGES

   Source: SOURCE_URL
   Retrieved: DATE

   Generated-By: doc-to-markdown-agent
   Signed-off-by: Your Name <your.email>"
   ```

## Relationship to Main Guides

```
┌──────────────────────┐
│ Authoritative        │
│ Sources              │
│ (web, RST, etc.)     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ references/          │  ◄── You are here
│ (converted markdown) │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ docs/                │
│ comprehensive-guide  │  ◄── Main style guide
│ quick-rules          │      (distilled from references)
└──────────────────────┘
```

The reference documents are **sources of truth**. The main guides are **AI-optimized distillations** of these sources.

## Using References

### For Contributors

When writing the style guide:

1. **Always check references first** before adding new content
2. **Cite specific sections** when referencing rules
3. **Link to references** for detailed explanations
4. **Keep guides in sync** with reference updates

### For AI Tools

These references can be provided as context to AI tools, but the main guides are optimized for AI consumption:

**For Generation:**
- Use `docs/quick-rules.md` (concise, AI-optimized)
- Use `docs/comprehensive-guide.md` (detailed examples)

**For Deep Dive:**
- Use references for complete, authoritative information
- Use when quick-rules don't answer the question

### For Developers

When you have questions:

1. **Quick answer:** Check `docs/quick-rules.md`
2. **Detailed explanation:** Check `docs/comprehensive-guide.md`
3. **Official source:** Check `references/` directory
4. **Deepest dive:** Follow `source_url` to original document

## Citation Format

When citing these references in commits or documentation:

```markdown
According to the OpenInfra Foundation AI Policy [1], all AI-generated
contributions must include proper attribution.

[1] references/ai-policy.md, Section: "Contributor Checklist"
    Original source: https://openinfra.org/legal/ai-policy
    Retrieved: 2025-10-25
```

## Validation

To ensure references are current:

```bash
# Check for updates to sources
./tools/check-reference-updates.sh

# Or manually check each source
curl -sI https://openinfra.org/legal/ai-policy | grep "last-modified"
```

## Contributing Reference Updates

If you find the references are out of date:

1. **Open an issue** describing what's outdated
2. **Fetch updated content** from authoritative source
3. **Convert to markdown** (use doc-to-markdown agent if available)
4. **Update metadata** (conversion_date, source_url)
5. **Submit PR** with DCO sign-off

See [CONTRIBUTING.md](../CONTRIBUTING.md) for full contribution guidelines.

## Important Notes

### These Are NOT the Style Guide

The files in this directory are **reference sources**, not the style guide itself.

**The style guide is:**
- `docs/comprehensive-guide.md`
- `docs/quick-rules.md`

**These references are:**
- Source material for the style guide
- Authoritative documentation for deep dives
- Verification for accuracy

### Authoritative Sources

When there's a conflict or question:

1. **Official source** (linked in frontmatter) is authoritative
2. **Reference file** reflects official source at time of conversion
3. **Style guide** distills references for AI consumption

If you find a discrepancy, check the official source and update accordingly.

## License and Copyright

All reference documents retain their original licenses:

- **ai-policy.md:** OpenInfra Foundation content
- **dco.md:** Linux Foundation / Developer Certificate of Origin
- **hacking.md:** Apache 2.0 (OpenStack project)
- **pep8.md:** Python Software Foundation License
- **commit-message.md:** OpenStack project content (Creative Commons Attribution 3.0)

This repository's formatting and organization is Apache 2.0, but the **content** of reference documents belongs to their respective copyright holders.

## Questions?

For questions about:

- **Content of references:** Check the official source URLs
- **Updates to references:** Open an issue
- **Style guide interpretation:** See docs/comprehensive-guide.md
- **Contributing:** See CONTRIBUTING.md

---

**Last Updated:** 2025-10-25
**Maintainer:** See CONTRIBUTING.md for current maintainers
