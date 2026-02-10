# Ensure a valid locale for Ansible/molecule in minimal environments
export LC_ALL ?= C.UTF-8

.PHONY: help molecule test create converge verify destroy

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

molecule: test ## Run molecule tests (alias for test)

test: ## Run full molecule test suite
	uvx --with molecule-plugins[docker] molecule test

create: ## Create molecule instances
	uvx --with molecule-plugins[docker] molecule create

converge: ## Run molecule converge
	uvx --with molecule-plugins[docker] molecule converge

verify: ## Run molecule verify
	uvx --with molecule-plugins[docker] molecule verify

destroy: ## Destroy molecule instances
	uvx --with molecule-plugins[docker] molecule destroy

side-effect: ## Run molecule side-effect
	uvx --with molecule-plugins[docker] molecule side-effect

login: ## Login to molecule instance
	uvx --with molecule-plugins[docker] molecule login
