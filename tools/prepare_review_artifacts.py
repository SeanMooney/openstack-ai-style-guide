#!/usr/bin/env python3
# Copyright 2026 Sean Mooney
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Prepare deterministic teim-review context artifacts."""

import argparse
import json
import shutil
import subprocess  # nosec B404 - fixed git commands are used for local repo metadata
import sys
from pathlib import Path
from typing import Any

import yaml


def run_git(project_dir: Path, args: list[str]) -> str:
    """Run a read-only git command and return trimmed stdout."""
    git_binary = shutil.which('git')
    if git_binary is None:
        return ''
    try:
        result = subprocess.run(  # noqa: S603 - fixed git command args
            [git_binary, '-C', str(project_dir), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ''
    if result.returncode != 0:
        return ''
    return result.stdout.strip()


def load_yaml(path: Path | None) -> Any:
    """Load optional YAML."""
    if path is None or not path.exists():
        return {}
    with path.open(encoding='utf-8') as stream:
        return yaml.safe_load(stream) or {}


def read_lines(path: Path | None) -> list[str]:
    """Read non-empty lines from an optional text file."""
    if path is None or not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding='utf-8').splitlines()
            if line.strip()]


def first_present(mapping: dict[str, Any], names: list[str]) -> Any:
    """Return the first present value from a dict."""
    for name in names:
        value = mapping.get(name)
        if value not in (None, ''):
            return value
    return None


def find_zuul_vars(data: Any) -> dict[str, Any]:
    """Find a likely Zuul variable mapping inside an inventory document."""
    if isinstance(data, dict):
        if isinstance(data.get('zuul'), dict):
            return data['zuul']
        vars_data = data.get('vars')
        if isinstance(vars_data, dict) and isinstance(vars_data.get('zuul'), dict):
            return vars_data['zuul']
        all_data = data.get('all')
        if isinstance(all_data, dict):
            found = find_zuul_vars(all_data)
            if found:
                return found
        children = data.get('children')
        if isinstance(children, dict):
            for value in children.values():
                found = find_zuul_vars(value)
                if found:
                    return found
        hosts = data.get('hosts')
        if isinstance(hosts, dict):
            for value in hosts.values():
                found = find_zuul_vars(value)
                if found:
                    return found
    return {}


def collect_git_context(
    project_dir: Path,
    base_ref: str | None = None,
) -> dict[str, str]:
    """Collect deterministic local repository context."""
    diff_range = f'{base_ref}..HEAD' if base_ref else 'HEAD~1..HEAD'
    return {
        'head': run_git(project_dir, ['rev-parse', 'HEAD']),
        'branch': run_git(project_dir, ['branch', '--show-current']),
        'subject': run_git(project_dir, ['log', '-1', '--format=%s']),
        'body': run_git(project_dir, ['log', '-1', '--format=%b']),
        'author': run_git(project_dir, ['log', '-1', '--format=%an <%ae>']),
        'stat': run_git(project_dir, ['diff', '--stat', diff_range]),
        'status': run_git(project_dir, ['status', '--short']),
    }


def build_context(args: argparse.Namespace) -> dict[str, Any]:
    """Build structured context metadata."""
    inventory = load_yaml(args.inventory_file)
    zuul = find_zuul_vars(inventory)
    git_context = collect_git_context(args.project_dir, args.review_base)
    changed_files = read_lines(args.changed_files)

    change = first_present(
        zuul,
        ['change_message', 'message', 'commit_message'],
    ) or git_context['subject'] or 'No change summary available'
    scope = (
        f'{len(changed_files)} changed file(s): {", ".join(changed_files[:12])}'
        if changed_files else 'No changed file list was provided'
    )
    impact = (
        'Review impact is derived from the changed files, commit summary, '
        'and accepted validated findings.'
    )

    return {
        'mode': 'zuul' if args.inventory_file else 'local',
        'project_dir': str(args.project_dir),
        'output_dir': str(args.output_dir),
        'change': str(change).strip(),
        'scope': scope,
        'impact': impact,
        'review_basis': 'OpenStack review guidance and project-specific files',
        'zuul': {
            'change': first_present(zuul, ['change']),
            'patchset': first_present(zuul, ['patchset']),
            'project': first_present(zuul, ['project', 'project_name']),
            'branch': first_present(zuul, ['branch']),
            'change_url': first_present(zuul, ['change_url']),
            'commit_id': first_present(zuul, ['commit_id']),
        },
        'git': git_context,
        'review': {
            'head': git_context['head'],
            'base': args.review_base,
            'scope_mode': args.scope_mode,
        },
        'changed_files': changed_files,
        'context_paths': {
            'project_dir': str(args.project_dir),
            'changed_files': str(args.changed_files) if args.changed_files else None,
            'quick_rules': str(args.quick_rules),
            'comprehensive_guide': str(args.comprehensive_guide),
            'finding_policy': str(args.finding_policy),
            'knowledge_root': str(args.knowledge_root),
            'candidate_schema': str(args.candidate_schema),
            'validated_schema': str(args.validated_schema),
        },
    }


def write_zuul_context(output_dir: Path, context: dict[str, Any]) -> None:
    """Write execution context markdown."""
    zuul = context['zuul']
    lines = [
        '# Execution Context',
        '',
        f'Mode: {context["mode"]}',
        f'Project: {zuul.get("project") or context["project_dir"]}',
        f'Branch: {zuul.get("branch") or context["git"].get("branch") or "unknown"}',
        f'Change: {zuul.get("change") or "local"}',
        f'Patchset: {zuul.get("patchset") or "unknown"}',
        f'Commit: {zuul.get("commit_id") or context["git"].get("head") or "unknown"}',
        '',
        '## Review Scope',
        '',
        context['scope'],
        '',
        '## Full Context Paths',
        '',
    ]
    for name, value in context['context_paths'].items():
        if value:
            lines.append(f'- {name}: `{value}`')
    output_dir.joinpath('zuul-context.md').write_text(
        '\n'.join(lines) + '\n',
        encoding='utf-8',
    )


def write_commit_summary(output_dir: Path, context: dict[str, Any]) -> None:
    """Write commit summary markdown."""
    git_context = context['git']
    body = git_context.get('body') or 'No commit body was available.'
    stat = git_context.get('stat') or 'No git diff stat was available.'
    lines = [
        '# Commit Summary',
        '',
        f'Subject: {git_context.get("subject") or context["change"]}',
        f'Author: {git_context.get("author") or "unknown"}',
        f'Commit: {git_context.get("head") or "unknown"}',
        '',
        '## Message Body',
        '',
        body,
        '',
        '## Diff Stat',
        '',
        '```text',
        stat,
        '```',
    ]
    output_dir.joinpath('commit-summary.md').write_text(
        '\n'.join(lines) + '\n',
        encoding='utf-8',
    )


def write_project_guidelines(args: argparse.Namespace) -> None:
    """Write project guidance markdown with paths available to Claude."""
    candidate_files = ['AGENTS.md', 'HACKING.rst', 'CLAUDE.md']
    lines = ['# Project Guidelines', '']
    found = False
    for name in candidate_files:
        path = args.project_dir / name
        if path.exists():
            found = True
            text = path.read_text(encoding='utf-8', errors='replace').strip()
            lines.extend([f'## {name}', '', text, ''])
    if not found:
        lines.extend([
            'No project-local AGENTS.md, HACKING.rst, or CLAUDE.md file was found.',
            '',
        ])
    lines.extend([
        '## Shared Guidance Paths',
        '',
        f'- Quick rules: `{args.quick_rules}`',
        f'- Comprehensive guide: `{args.comprehensive_guide}`',
        f'- Finding policy: `{args.finding_policy}`',
        f'- Knowledge root: `{args.knowledge_root}`',
    ])
    args.output_dir.joinpath('project-guidelines.md').write_text(
        '\n'.join(lines) + '\n',
        encoding='utf-8',
    )


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description='Prepare deterministic teim-review artifacts'
    )
    parser.add_argument('--project-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--inventory-file', type=Path)
    parser.add_argument('--changed-files', type=Path)
    parser.add_argument('--quick-rules', required=True, type=Path)
    parser.add_argument('--comprehensive-guide', required=True, type=Path)
    parser.add_argument('--finding-policy', required=True, type=Path)
    parser.add_argument('--knowledge-root', required=True, type=Path)
    parser.add_argument('--candidate-schema', required=True, type=Path)
    parser.add_argument('--validated-schema', required=True, type=Path)
    parser.add_argument('--review-base')
    parser.add_argument(
        '--scope-mode',
        choices=('branch', 'commit', 'local'),
        default='local',
    )
    return parser.parse_args()


def main() -> int:
    """Run the artifact preparation CLI."""
    args = parse_args()
    args.project_dir = args.project_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    context = build_context(args)
    write_zuul_context(args.output_dir, context)
    write_commit_summary(args.output_dir, context)
    write_project_guidelines(args)
    args.output_dir.joinpath('review-context.json').write_text(
        json.dumps(context, indent=2) + '\n',
        encoding='utf-8',
    )
    print(f'Prepared teim-review artifacts in {args.output_dir}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
