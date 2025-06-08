# Contributing to OpenStack AI Style Guide

Thank you for your interest in improving the OpenStack AI Style Guide! This document provides guidelines for contributing to this repository, with special attention to AI-generated content.

## 🎯 Contribution Types

### 1. Style Rule Updates
- Adding new OpenStack compliance rules
- Updating existing patterns based on community feedback
- Clarifying ambiguous guidelines

### 2. Example Code
- Good patterns that follow OpenStack standards
- Anti-patterns showing what to avoid
- Real-world scenarios and edge cases

### 3. AI Tool Integration
- Configuration examples for new AI tools
- Usage patterns and best practices
- Token optimization strategies

### 4. Documentation Improvements
- Clarity enhancements
- Better organization
- Additional use cases

## 🤖 AI-Generated Content Policy

### Allowed AI Assistance
- ✅ Code examples and patterns
- ✅ Documentation improvements
- ✅ Style rule clarifications
- ✅ Grammar and formatting fixes

### Required Attribution
All AI-assisted contributions MUST include proper attribution in commit messages:

```
Add new exception handling patterns

This commit adds comprehensive examples of proper OpenStack
exception handling patterns, including specific exceptions,
logging practices, and error propagation techniques.

The initial examples were generated using Claude Code based on
existing OpenStack nova and neutron patterns. Manual modifications
included adding project-specific context, improving documentation,
and ensuring compliance with current hacking rules.

Generated-By: claude-code
Signed-off-by: Jane Doe <jane.doe@example.com>
```

### Review Requirements
- All AI-generated content must be reviewed by a human contributor
- Examples must be tested for compliance with OpenStack CI
- Documentation must be accurate and up-to-date

## 📝 Contribution Process

### 1. Fork and Clone
```bash
git clone https://github.com/yourusername/openstack-ai-style-guide.git
cd openstack-ai-style-guide
```

### 2. Create Feature Branch
```bash
git checkout -b feature/new-pattern-examples
```

### 3. Make Changes
Follow the repository structure:
- Style rules: Update `docs/quick-rules.md` and `docs/comprehensive-guide.md`
- Examples: Add to `examples/good/` or `examples/bad/`
- Tools: Add scripts to `tools/`

### 4. Test Changes
```bash
# Validate token counts are within targets
wc -w docs/quick-rules.md    # Should be ~800 tokens
wc -w docs/comprehensive-guide.md  # Should be ~2500 tokens

# Test any code examples
python -m py_compile examples/good/*.py
```

### 5. Commit with Proper Attribution
```bash
git commit -s -m "Commit title following OpenStack style

Detailed commit message explaining the changes and AI usage.

Generated-By: tool-name  # or Assisted-By: tool-name
Signed-off-by: Your Name <your.email@example.com>"
```

### 6. Submit Pull Request
- Clearly describe the changes and motivation
- Include AI usage information in the PR description
- Reference any related issues

## 📏 Content Guidelines

### Style Rules
- Must be enforceable by automated tools
- Include specific examples of correct/incorrect patterns
- Reference specific OpenStack hacking rules (H201, H210, etc.)
- Provide rationale for the rule

### Code Examples
- Must pass OpenStack CI checks
- Include appropriate license headers
- Follow all established patterns
- Be self-contained and clear

### Documentation
- Use clear, concise language
- Provide context for rules and patterns
- Include practical usage scenarios
- Maintain consistent formatting

## 🔍 Token Management

### Quick Rules (`docs/quick-rules.md`)
- **Target**: ~800 tokens
- **Maximum**: 1000 tokens
- **Focus**: Essential rules only
- **Format**: Bullet points and brief code snippets

### Comprehensive Guide (`docs/comprehensive-guide.md`)
- **Target**: ~2500 tokens
- **Maximum**: 3000 tokens
- **Focus**: Detailed explanations and context
- **Format**: Full examples and thorough explanations

### Token Counting
```bash
# Count words (approximate token count)
wc -w docs/quick-rules.md
wc -w docs/comprehensive-guide.md

# More accurate token counting (if available)
tiktoken count docs/quick-rules.md
```

## 🚀 Priority Areas

### High Priority
1. New OpenStack hacking rules
2. Critical compliance patterns
3. Common AI tool integration issues
4. DCO sign-off examples (post July 1, 2025)

### Medium Priority
1. Additional code examples
2. Edge case documentation
3. Performance optimization patterns
4. Advanced AI tool configurations

### Low Priority
1. Minor documentation improvements
2. Formatting enhancements
3. Additional tool integrations

## 📊 Quality Standards

### Code Quality
- All Python code must pass `tox -e pep8`
- Examples must be production-ready
- No security vulnerabilities
- Proper error handling

### Documentation Quality
- Clear and unambiguous language
- Accurate technical information
- Consistent formatting and style
- Appropriate level of detail

### AI Content Quality
- Properly attributed in commits
- Reviewed and validated by humans
- Compliant with OpenInfra Foundation AI Policy
- Does not contain proprietary patterns

## 🛠 Development Setup

### Prerequisites
```bash
# Python development
python3 -m venv venv
source venv/bin/activate
pip install tox pre-commit

# Git configuration for DCO
git config user.name "Your Real Name"
git config user.email "your.email@example.com"
```

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

### Validation Tools
```bash
# Style checking
tox -e pep8

# Documentation linting
markdownlint docs/

# Token counting
python tools/count_tokens.py docs/quick-rules.md
```

## 🤝 Community Guidelines

### Communication
- Be respectful and constructive
- Focus on technical merit
- Provide specific, actionable feedback
- Acknowledge AI assistance in discussions

### Collaboration
- Work together to improve OpenStack AI tooling
- Share knowledge and best practices
- Help newcomers understand the guidelines
- Maintain high standards for code quality

### Conflict Resolution
- Discuss technical disagreements openly
- Seek consensus on style decisions
- Escalate to OpenStack technical committees if needed
- Document decisions for future reference

## 📞 Getting Help

### Questions and Support
- Open an issue for clarification requests
- Use descriptive titles and provide context
- Include AI tool information if relevant
- Be patient and respectful

### Reporting Issues
- Security vulnerabilities: Report privately
- Style inconsistencies: Open public issues
- AI tool compatibility: Provide detailed environment info
- Documentation errors: Include specific locations

---

## 📜 Legal Compliance

By contributing to this repository, you agree to:

1. **License Compatibility**: All contributions are licensed under Apache 2.0
2. **AI Attribution**: Properly attribute AI-generated content
3. **DCO Compliance**: Sign-off all commits (required post July 1, 2025)
4. **OpenInfra Foundation AI Policy**: Follow all applicable guidelines
5. **No Proprietary Content**: Do not contribute proprietary or copyrighted material

Thank you for helping make OpenStack development more accessible and efficient for AI-assisted workflows!