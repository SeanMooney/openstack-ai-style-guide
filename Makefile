.PHONY: help test test-cover lint molecule dev-install clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Testing with tox
test: ## Run all tests via tox
	tox

test-cover: ## Run tests with coverage via tox
	tox -e cover

# Molecule testing (delegates to role Makefiles)
molecule: ## Run molecule tests for all roles
	tox -e molecule

molecule-ai_code_review: ## Run molecule tests for ai_code_review role
	cd roles/ai_code_review && make molecule

molecule-run_claude_code: ## Run molecule tests for run_claude_code role
	cd roles/run_claude_code && make molecule

molecule-ai_zuul_integration: ## Run molecule tests for ai_zuul_integration role
	cd roles/ai_zuul_integration && make molecule

# Linting (fast, for pre-commit)
lint: ## Run all linters
	tox -e linters

# Development
dev-install: ## Install development dependencies with uv
	uv pip install -e ".[test]"
	uv pip install tox-uv pre-commit

pre-commit-install: ## Install pre-commit hooks
	pre-commit install
	pre-commit install --hook-type commit-msg

clean: ## Clean test artifacts
	rm -rf .stestr
	rm -rf cover
	rm -rf .tox
	rm -rf .uv_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
