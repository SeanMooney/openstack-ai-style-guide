# OpenStack AI Style Guide

A comprehensive style guide and ruleset designed for AI code generation tools working with
OpenStack Python projects.

## 🚀 Quick Start for AI Tools

### Primary Files

- **[`quick-rules.md`](docs/quick-rules.md)** (710 tokens) - Essential rules for immediate use
- **[`comprehensive-guide.md`](docs/comprehensive-guide.md)** (4700 tokens) - Detailed explanations and examples

### Integration Commands

```bash
# Claude Code
claude-code --context-file docs/quick-rules.md

# Cursor
# Add to .cursorrules: @docs/quick-rules.md

# Generic AI tool
curl https://raw.githubusercontent.com/username/openstack-ai-style-guide/main/docs/quick-rules.md

# Local usage
cat docs/quick-rules.md | pbcopy  # macOS
cat docs/quick-rules.md | xclip -selection clipboard  # Linux
```

## 📦 Claude Code Plugin

This repository is a Claude Code plugin providing the `/teim-review` skill and
a suite of AI agents for OpenStack code review.

### Install as a Plugin

```bash
# Add this repo as a marketplace (local clone)
/plugin marketplace add /path/to/openstack-ai-style-guide

# Install the teim-review plugin
/plugin install teim-review@openstack-ai-style-guide
```

### Local Code Review

Once installed, run `/teim-review` in any OpenStack project to get a full
AI-assisted review:

```bash
# In your OpenStack project directory:
/teim-review
```

Output is written to `.teim-review/` (gitignored):

- `review-report.json` — structured findings
- `review-report.html` — visual HTML report

### Included Agents

| Agent | Purpose |
|-------|---------|
| `teim-review-agent` | Orchestrates the full review pipeline |
| `code-review-agent` | OpenStack code review with confidence scoring |
| `zuul-context-extractor` | Extracts Zuul CI job context from inventory |
| `commit-summary` | Summarises commits and generates file trees |
| `project-guidelines-extractor` | Reads HACKING.rst, AGENTS.md, CLAUDE.md |
| `code-maintainability-auditor` | Dead code and refactoring analysis |
| `security-auditor` | Security vulnerability assessment |

## 📁 Repository Structure

```text
openstack-ai-style-guide/
├── .claude-plugin/                # Claude Code plugin manifest
│   ├── plugin.json               # Plugin definition (agents, skills)
│   └── marketplace.json          # Marketplace catalog
├── agents/                        # Agent definitions (*.md)
├── skills/                        # Slash command skills
│   └── teim-review/
│       └── SKILL.md              # /teim-review command
├── docs/                          # Style guide documentation
│   ├── quick-rules.md            # Concise reference (710 tokens)
│   ├── comprehensive-guide.md    # Detailed guide (4700 tokens)
│   ├── examples/                 # Code examples and patterns
│   │   ├── good/                # Correct OpenStack patterns
│   │   └── bad/                 # Anti-patterns to avoid
│   ├── checklists/              # Validation checklists
│   │   ├── pre-submit.md       # Before committing and pushing
│   │   └── code-review.md      # Reviewing AI code
│   └── templates/               # Code and commit templates
│       ├── python_module.py.template
│       ├── python_test.py.template
│       ├── commit_message.txt
│       └── pre-commit-config.yaml
├── references/                   # Authoritative source documents
│   ├── ai-policy.md             # OpenInfra AI Policy
│   ├── dco.md                   # Developer Certificate of Origin
│   ├── hacking.md               # OpenStack Hacking Rules
│   └── pep8.md                  # PEP 8 Style Guide
├── tools/                        # Standalone helper scripts
│   └── render_html_from_json.py # HTML report generator (uv-compatible)
├── CONTRIBUTING.md               # Contribution guidelines
├── LICENSE                       # Apache 2.0 license
└── README.md                     # This file

```

## 🎯 When to Use Which Guide

### Use `quick-rules.md` for

- ✅ Real-time code generation
- ✅ Quick validation checks
- ✅ Context-constrained AI tools
- ✅ Fast reference lookups

### Use `comprehensive-guide.md` for

- 📚 Learning OpenStack patterns
- 🐛 Complex debugging scenarios
- 📝 Policy and compliance questions
- 🔍 Detailed implementation guidance

## 🛠 AI Tool Configuration

### Claude Code

```bash
# Include in system prompt or use context file
claude-code --context-file docs/quick-rules.md --model claude-3-sonnet
```

### GitHub Copilot

Add to your `.github/copilot-instructions.md`:

```markdown
Follow the OpenStack style guide at docs/quick-rules.md for all Python code generation.
```

### Cursor

Add to `.cursorrules`:

```text
@docs/quick-rules.md

Always follow OpenStack Python style guidelines for code generation.
```

### Custom AI Tools

Include the quick rules as system context:

```python
with open('docs/quick-rules.md', 'r') as f:
    style_guide = f.read()

# Pass style_guide as system context to your AI model
```

## 🚦 Compliance Checklist

Before submitting AI-generated OpenStack code:

- [ ] Apache 2.0 license header included
- [ ] Line length ≤ 79 characters
- [ ] No bare `except:` statements
- [ ] `autospec=True` in all mock decorators
- [ ] Delayed logging interpolation used
- [ ] Proper import organization
- [ ] AI attribution in commit message (Generated-By/Assisted-By)
- [ ] **DCO sign-off included** (git commit -s - REQUIRED)

## 📊 Token Usage Guide

| Context | File | Tokens | Use Case |
|---------|------|--------|----------|
| Minimal | `quick-rules.md` | 710 | Real-time generation |
| Standard | Both files | 5410 | Complex implementations |
| Full | All docs + examples | ~7100+ | Learning/training |

**Token Constraints:**

- `quick-rules.md`: Target < 1000 tokens for standalone copying to other repos
- `comprehensive-guide.md`: Target < 5000 tokens for comprehensive reference
- Both files designed to be self-contained and readable without external dependencies

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Adding new rules and patterns
- Contributing examples
- AI-generated content attribution
- Community review process

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Resources

- [OpenStack Contributor Guide](https://docs.openstack.org/contributors/)
- [OpenInfra Foundation AI Policy](https://openinfra.dev/ai-policy)
- [Python PEP 8 Style Guide](https://pep8.org/)
- [Hacking Style Checks](https://docs.openstack.org/hacking/latest/)
