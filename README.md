# zendev

Personal dev workflow toolkit: unified logging + emoji commit conventions.

## Reusable `commit-msg` hook

This repository now publishes a reusable `pre-commit`/`prek` hook: `zendev-commit-msg`.

It validates commit titles against zendev's emoji commit schema:

- `✨ feat: add export`
- `🐛 fix(parser): handle null token`
- `📝 docs: update README`

It also allows common git-generated commit messages such as merge, revert, `fixup!`, and `squash!`.

Messages like `feat: add export` are rejected because the emoji prefix is required.

### Use from another repository

With `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/your-org/zendev
    rev: v0.1.0
    hooks:
      - id: zendev-commit-msg
```

With `prek.toml`:

```toml
[[repos]]
repo = "https://github.com/your-org/zendev"
rev = "v0.1.0"
hooks = [
  { id = "zendev-commit-msg" },
]
```

Then install the hook:

```bash
uvx prek install --hook-type commit-msg
```

### GitHub Actions: validate PR titles

PR-title validation now lives in the standalone
[`zrr1999/zendev-actions`](https://github.com/zrr1999/zendev-actions) repository,
while this repository provides the underlying `zendev-validate-title` CLI.

Pin the standalone action and pass the PR title:

```yaml
# .github/workflows/ci-pr-checks.yml
name: CI - PR Checks

on:
  pull_request:
    types: [opened, edited, synchronize, reopened]

jobs:
  title:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: read
    steps:
      - uses: zrr1999/zendev-actions/validate-title@58f5b4600fba93a57cc340090b42da67d9f4ac70
        with:
          text: ${{ github.event.pull_request.title }}
```

The action wrapper shells out via `uvx --from git+...` to `zendev-validate-title`.
For stability, pin a commit SHA (or a future release tag) in production workflows.

### Use inside this repository

```bash
just install
```

That installs both `pre-commit` and `commit-msg` hooks for local development.
