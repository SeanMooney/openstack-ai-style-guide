# OpenStack AI Style Guide

A comprehensive style guide and ruleset specifically designed for AI code generation tools working with OpenStack Python projects.

## 🚀 Quick Start for AI Tools

### Primary Files
- **[`quick-rules.md`](docs/quick-rules.md)** (~800 tokens) - Essential rules for immediate use
- **[`comprehensive-guide.md`](docs/comprehensive-guide.md)** (~2500 tokens) - Detailed explanations and examples

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

## 📁 Repository Structure

```
openstack-ai-style-guide/
├── docs/                     # Style guide documentation
│   ├── quick-rules.md       # Concise reference (~800 tokens)
│   └── comprehensive-guide.md # Detailed guide (~2500 tokens)
├── examples/                # Code examples and patterns
│   ├── good/               # Correct OpenStack patterns
│   └── bad/                # Anti-patterns to avoid
├── tools/                  # Validation and helper scripts
├── CONTRIBUTING.md         # Contribution guidelines for AI-generated content
├── LICENSE                 # Apache 2.0 license
└── README.md              # This file

```

## 🎯 When to Use Which Guide

### Use `quick-rules.md` for:
- ✅ Real-time code generation
- ✅ Quick validation checks  
- ✅ Context-constrained AI tools
- ✅ Fast reference lookups

### Use `comprehensive-guide.md` for:
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
```
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
- [ ] AI attribution in commit message
- [ ] DCO sign-off included (required post July 1, 2025)

## 📊 Token Usage Guide

| Context | File | Tokens | Use Case |
|---------|------|--------|----------|
| Minimal | `quick-rules.md` | ~800 | Real-time generation |
| Standard | Both files | ~3300 | Complex implementations |
| Full | All docs + examples | ~5000+ | Learning/training |

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
