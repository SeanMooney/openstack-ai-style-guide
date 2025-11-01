# OpenStack Code Templates

This directory contains templates for generating OpenStack-compliant code with proper licensing, formatting, and structure.

## Available Templates

### 1. `python_module.py.template`

Complete Python module template with:

- Apache 2.0 license header
- Proper import organization
- Module-level docstring
- Class and function examples with OpenStack-style docstrings
- Exception handling patterns
- Logging with delayed interpolation

**Usage:**

```bash
cp templates/python_module.py.template myproject/new_module.py
# Edit placeholders: MODULE_NAME, DESCRIPTION, etc.
```

### 2. `python_test.py.template`

Test file template with:

- Apache 2.0 license header
- Proper test class structure
- Mock usage with `autospec=True`
- Correct assertion methods
- Exception testing patterns

**Usage:**

```bash
cp templates/python_test.py.template myproject/tests/test_new_module.py
# Edit placeholders: MODULE_NAME, test methods, etc.
```

### 3. `commit_message.txt`

Commit message template with:

- Proper subject line format
- Body structure (WHY, WHAT, HOW)
- AI attribution (Generated-By/Assisted-By)
- DCO sign-off
- External references

**Usage:**

```bash
git commit -s -F templates/commit_message.txt
# Edit the template file first with your specific changes
```

### 4. `pre-commit-config.yaml`

Pre-commit hook configuration for:

- Python linting (flake8, hacking)
- Import sorting
- License header verification
- Line length checks

**Usage:**

```bash
cp templates/pre-commit-config.yaml .pre-commit-config.yaml
pip install pre-commit
pre-commit install
```

## Using Templates with AI Tools

### Claude Code

```bash
# Include template as context
cat templates/python_module.py.template | claude-code "Create a new service module for managing instances"
```

### GitHub Copilot

Add to your `.github/copilot-instructions.md`:

```markdown
When creating new Python files, use the template from templates/python_module.py.template
```

### General Pattern

1. Copy the template to your target location
2. Use AI tool to fill in the implementation
3. Ensure all placeholders are replaced
4. Run validation: `tox -e pep8`

## Template Placeholders

All templates use these standard placeholders:

- `MODULE_NAME` - Name of the module/class
- `DESCRIPTION` - Brief description
- `AUTHOR_NAME` - Your name for TODO comments
- `YOUR_NAME` - Full name for DCO sign-off
- `YOUR_EMAIL` - Email for DCO sign-off

## Customizing Templates

You can customize these templates for your project:

1. Add project-specific imports
2. Include common utility patterns
3. Add standard configuration options
4. Update license headers if needed (while maintaining Apache 2.0)

## Validation

After using templates, always validate:

```bash
# Check syntax
python -m py_compile your_new_file.py

# Run style checks
tox -e pep8

# Verify license header
grep -q "Apache License" your_new_file.py && echo "License OK" || echo "Missing license"
```

## Examples

See the `docs/examples/` directory for complete working examples that use these templates.
