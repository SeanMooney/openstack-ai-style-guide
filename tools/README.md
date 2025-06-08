# OpenStack AI Style Guide Tools

This directory contains validation and utility tools for maintaining the OpenStack AI style guide.

## Tools Overview

### `validate_style.py`
Python style validator for OpenStack compliance.

**Usage:**
```bash
# Validate single file
python tools/validate_style.py examples/good/basic_service.py

# Validate multiple files
python tools/validate_style.py examples/good/*.py

# Treat warnings as errors
python tools/validate_style.py --warnings-as-errors examples/good/*.py

# Quiet mode (errors/warnings only)
python tools/validate_style.py --quiet examples/good/*.py
```

**Checks performed:**
- Apache 2.0 license header presence
- Line length (79 character limit)
- Import organization
- Exception handling patterns (H201: bare except)
- Logging patterns (H702: delayed interpolation)
- Mock usage (H210: autospec requirement)
- Mutable default arguments (H232)

### `count_tokens.py`
Token counting utility for AI context management.

**Usage:**
```bash
# Count tokens in style guide files
python tools/count_tokens.py docs/quick-rules.md docs/comprehensive-guide.md

# Check against target
python tools/count_tokens.py --target 800 docs/quick-rules.md

# JSON output
python tools/count_tokens.py --format json docs/*.md

# Simple output
python tools/count_tokens.py --format simple docs/*.md
```

**Token targets:**
- `quick-rules.md`: ~800 tokens
- `comprehensive-guide.md`: ~2500 tokens
- Combined: ~3300 tokens

## Integration Examples

### Pre-commit Hook
Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: openstack-style
        name: OpenStack Style Validation
        entry: python tools/validate_style.py
        language: system
        files: \.py$
```

### CI/CD Pipeline
```bash
# In your CI script
python tools/validate_style.py --warnings-as-errors examples/good/*.py
python tools/count_tokens.py --target 800 docs/quick-rules.md
python tools/count_tokens.py --target 2500 docs/comprehensive-guide.md
```

### AI Tool Integration
```bash
# Before generating code
python tools/validate_style.py generated_code.py

# Context size management
TOKEN_COUNT=$(python tools/count_tokens.py --format simple docs/quick-rules.md | grep -o '[0-9]*')
if [ $TOKEN_COUNT -gt 1000 ]; then
  echo "Warning: Context file too large for efficient AI processing"
fi
```

## Development

### Adding New Validators
To add new validation rules to `validate_style.py`:

1. Add the check method to `OpenStackStyleValidator` class
2. Call it from `validate_file()` method
3. Use `self.errors.append()` for violations
4. Use `self.warnings.append()` for suggestions

Example:
```python
def _check_new_pattern(self, content):
    """Check for new pattern violations."""
    if 'bad_pattern' in content:
        self.errors.append("Custom rule: bad_pattern detected")
```

### Testing Tools
```bash
# Test validator with good examples (should pass)
python tools/validate_style.py examples/good/*.py

# Test validator with bad examples (should fail)
python tools/validate_style.py examples/bad/*.py

# Test token counter
python tools/count_tokens.py docs/*.md examples/*.py
```

## Performance Notes

- **`validate_style.py`**: Fast for individual files, may be slow for large codebases
- **`count_tokens.py`**: Very fast, suitable for frequent use
- Both tools are designed for offline use and don't require network access

## Dependencies

Both tools use only Python standard library modules:
- `ast` - For Python AST parsing
- `re` - For pattern matching
- `pathlib` - For file handling
- `argparse` - For command-line interface
- `json` - For JSON output (optional)

No external dependencies required!