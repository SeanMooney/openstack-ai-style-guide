# Codex Installation and Usage

This repository supports Codex through a native local plugin and interactive
skill flow.

## Prerequisites

Install the Codex CLI and authenticate:

```bash
npm install -g @openai/codex
codex login
```

The supported native install flow follows the local marketplace guidance from
the OpenAI Codex plugin documentation.

## Install the Teim Review Plugin

From the repository root:

```bash
scripts/install-codex-skill
```

That helper:

- copies `plugins/teim-review/` into `${CODEX_HOME:-$HOME/.codex}/plugins/`
- creates or updates a personal marketplace at `${AGENTS_HOME:-$HOME/.agents}/plugins/marketplace.json`
- preserves unrelated marketplace entries and top-level metadata when the file already exists
- writes the installed `teim-review` entry with an absolute plugin path that matches the effective `CODEX_HOME`

After running it:

1. Restart Codex.
2. Open the plugin directory in Codex.
3. Install `teim-review` from the `Local Codex Plugins` marketplace.

If you prefer a repo-local marketplace instead, this repository also ships
`.agents/plugins/marketplace.json` for testing inside the repo checkout.

## Run Reviews

Use the installed skill interactively with `/skills` or by invoking:

```text
$teim-review
```

Output is written to `.teim-review/`:

- `zuul-context.md`
- `commit-summary.md`
- `project-guidelines.md`
- `review-report.json`
- `review-report.html`

## Profiles

- `fast`: `gpt-5.4-mini` for context-style extraction tasks
- `deep`: `gpt-5.4-mini` for context-style extraction tasks
- interactive Codex skill runs should keep the final review in the current
  session model
- `$teim-review` is the supported Codex-native interactive entrypoint for this
  repository

Profile mappings are defined in `config/tool-profiles.json`.

## Updating the Plugin

After pulling repository changes:

```bash
scripts/install-codex-skill
```

Then restart Codex so the updated local plugin copy is visible.

## Troubleshooting

### Codex cannot find the plugin

- Verify `${CODEX_HOME:-$HOME/.codex}/plugins/teim-review` exists.
- Verify `${AGENTS_HOME:-$HOME/.agents}/plugins/marketplace.json` contains a
  `teim-review` entry whose `source.path` matches the installed plugin path.
- Restart Codex after reinstalling or updating the plugin.

### Invalid personal marketplace JSON

If `${AGENTS_HOME:-$HOME/.agents}/plugins/marketplace.json` is invalid JSON,
`scripts/install-codex-skill` now exits without rewriting it. Repair or remove
the file, then rerun the installer.

### Network or approval failures

Codex review execution needs working OpenAI authentication and network access.
If a sandboxed environment blocks that, rerun with the needed approval flow.

### Bubblewrap warning

If Codex warns that system `bubblewrap` is missing, install it through your OS
package manager. Codex can often proceed with the vendored copy, but the system
package is preferred.

### Repo-root `.codex` file

Some native Codex runs create a local `.codex` artifact. The repository ignores
that file via `.gitignore`.

## Isolated Validation

Use this flow to validate the installed plugin with a separate Codex instance:

```bash
git worktree add /tmp/openstack-ai-style-guide-codex-test HEAD
cd /tmp/openstack-ai-style-guide-codex-test
export CODEX_HOME=/tmp/openstack-ai-style-guide-codex-home
export AGENTS_HOME=/tmp/openstack-ai-style-guide-agents-home
scripts/install-codex-skill
codex
# restart if needed, install teim-review from Local Codex Plugins, then run:
$teim-review
```

Expected results:

- the plugin installs into the temporary `CODEX_HOME`
- the personal marketplace keeps any unrelated entries and points `teim-review`
  at the temporary install path
- running `$teim-review` from the isolated checkout writes `.teim-review/`
  artifacts into that checkout
- `.teim-review/review-report.json` and `.teim-review/review-report.html` exist
