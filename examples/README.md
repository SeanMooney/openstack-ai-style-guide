# OpenStack Code Examples

This directory contains code examples demonstrating correct and incorrect patterns for OpenStack Python development.

## Directory Structure

- **`good/`** - Examples following OpenStack standards
- **`bad/`** - Anti-patterns and common mistakes to avoid

## Good Examples

### `good/basic_service.py`
Demonstrates:
- Proper Apache 2.0 license header
- Correct import organization
- OpenStack-style docstrings
- Exception handling best practices
- Logging with delayed interpolation
- Context manager usage
- Naming conventions

### `good/test_example.py`
Demonstrates:
- Proper test class structure
- Mock usage with `autospec=True`
- Correct assertion methods
- Exception testing patterns
- Logging verification

## Bad Examples (Anti-patterns)

### `bad/anti_patterns.py`
Shows common violations:
- H201: Bare except clauses
- H210: Missing autospec in mocks
- H216: Wrong mock imports
- H232: Mutable default arguments
- H304: Relative imports
- H501: Line length violations
- H702: Immediate string formatting in logging

## Using These Examples

### For AI Tools
Include relevant examples in your AI tool context:

```bash
# For code generation
cat examples/good/basic_service.py | ai-tool --context

# For validation
diff generated_code.py examples/good/basic_service.py
```

### For Learning
1. Study the good examples to understand proper patterns
2. Review bad examples to recognize anti-patterns
3. Use both for training AI models on OpenStack standards

### For Testing
```bash
# Validate good examples pass style checks
python -m py_compile examples/good/*.py
tox -e pep8

# Verify bad examples fail appropriately
python -m py_compile examples/bad/*.py  # Should show style violations
```

## Contributing Examples

When adding new examples:

1. **Good examples**: Must pass all OpenStack CI checks
2. **Bad examples**: Should demonstrate specific hacking rule violations
3. **Documentation**: Include comments explaining the patterns
4. **Attribution**: Follow AI contribution guidelines in CONTRIBUTING.md

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines on contributing examples.