#!/bin/bash
# Run molecule tests for all roles

set -e

# Ensure a valid locale for Ansible/molecule
export LC_ALL=C.UTF-8

# Anchor script to repo root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# List of roles with molecule tests
roles=(
    "ai_code_review"
    "run_claude_code"
    "ai_zuul_integration"
    "ai_html_generation"
)

for role in "${roles[@]}"; do
    echo "Running molecule tests for roles/$role"
    cd "${REPO_ROOT}/roles/${role}"
    make molecule
    cd - > /dev/null
done

echo "All molecule tests passed!"
