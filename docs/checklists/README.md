# OpenStack AI Code Generation Checklists

Quick reference checklists for validating AI-generated OpenStack code at various stages of development.

## Available Checklists

### 1. `pre-submit.md` - Before Committing and Pushing Code

Complete workflow checklist covering local validation, commit preparation, and pre-push verification
to ensure your code meets all OpenStack requirements and will pass CI/CD checks.

### 2. `code-review.md` - Reviewing AI-Generated Code

Use this when reviewing code that was generated or assisted by AI tools.

## Quick Access

```bash
# Display checklist in terminal
cat docs/checklists/pre-submit.md

# Use with checklist tools
task-list docs/checklists/pre-submit.md

# Print for reference
markdown-pdf docs/checklists/pre-submit.md
```

## Integration with Workflow

### Git Hooks

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "=== OpenStack Pre-Submission Checklist ==="
cat docs/checklists/pre-submit.md
echo ""
read -p "Have you reviewed the checklist above? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi
```

### Pre-commit Framework

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: show-checklist
      name: Show Pre-Submission Checklist
      entry: cat docs/checklists/pre-submit.md
      language: system
      always_run: true
      pass_filenames: false
```

### IDE Integration

**VS Code** - Add to tasks.json:

```json
{
  "label": "Show Pre-Submission Checklist",
  "type": "shell",
  "command": "cat docs/checklists/pre-submit.md",
  "presentation": {
    "reveal": "always",
    "panel": "new"
  }
}
```

### Terminal Aliases

Add to `.bashrc` or `.zshrc`:

```bash
alias os-pre-submit='cat docs/checklists/pre-submit.md'
alias os-review='cat docs/checklists/code-review.md'
```

## Customization

Feel free to customize these checklists for your specific project:

1. Copy the checklist to your project
2. Add project-specific requirements
3. Remove items that don't apply
4. Keep in version control for team consistency

## Checklist Format

All checklists use the following format:

- `[ ]` for items to verify
- `[✓]` for completed items
- **Bold** for critical/required items
- Regular text for recommended items
- Code blocks for commands to run

## Automation

Some checklist items can be automated:

```bash
# Auto-check license headers
grep -r "Apache License" --include="*.py" . | wc -l

# Auto-check line length
flake8 --select=E501 .

# Auto-check DCO sign-off
git log -1 --pretty=%B | grep "Signed-off-by:"
```

See `/tools/` directory for validation scripts.
