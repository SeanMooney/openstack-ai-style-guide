# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the **OpenStack AI Style Guide** repository containing comprehensive coding standards and guidelines specifically designed for AI code generation tools. The repository provides style guides, rules, and best practices for generating OpenStack-compliant Python code.

## Key Files and Purpose

- **`quick-rules.md`** (~800 tokens): Concise reference for AI tools with essential OpenStack Python coding standards
- **`comprehensive-guide.md`** (~2500 tokens): Detailed explanations and examples for complex OpenStack compliance requirements
- **`README.md`**: Instructions for AI tools on how to use these guides

## Usage Pattern for AI Tools

When working with OpenStack Python code generation:

1. **Primary Reference**: Always consult `quick-rules.md` first for essential rules
2. **Detailed Guidance**: Reference `comprehensive-guide.md` for complex scenarios requiring detailed explanations
3. **Integration**: Use the command suggested in README.md: `claude-code --context-file quick-rules.md`

## Content Structure

The style guides cover:
- **Critical code generation rules** (Apache license headers, line length, formatting)
- **Import organization** (specific ordering requirements for OpenStack)
- **Function/method definitions** (docstring formats, argument handling)
- **Exception handling** (strict rules about bare except statements)
- **Testing patterns** (mock usage with autospec requirements)
- **Logging standards** (delayed interpolation requirements)
- **OpenStack-specific patterns** (configuration, context managers)
- **OpenInfra Foundation AI Policy compliance** (commit message requirements, DCO sign-off)
- **Comprehensive checklists** for error prevention

## Key Compliance Requirements

This repository emphasizes compliance with:
- **OpenStack CI/CD pipeline requirements** (strict linting rules)
- **OpenInfra Foundation AI Policy** (mandatory AI attribution in commits)
- **Developer Certificate of Origin (DCO)** (required sign-off post July 1, 2025)
- **Apache 2.0 licensing** (required headers in all Python files)

## File Editing Guidelines

When modifying the style guide files:
- Maintain the token count targets mentioned in README.md
- Keep `quick-rules.md` concise for fast AI consumption
- Use `comprehensive-guide.md` for detailed explanations and examples
- Ensure consistency between the quick rules and comprehensive guide
- Update both files when adding new requirements or patterns