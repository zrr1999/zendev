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

### GitHub Actions: validate PR titles and bodies

This repository now ships both the Python CLIs and the thin composite-action
wrappers under [`actions/`](./actions), so one zendev revision owns the full PR
validation stack.

#### Use inside this repository

Check out the repo, then call the local actions:

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
      - uses: actions/checkout@v4
      - uses: ./actions/validate-title
        with:
          text: ${{ github.event.pull_request.title }}

  body:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: read
    steps:
      - uses: actions/checkout@v4
      - uses: ./actions/validate-body
        with:
          body: ${{ github.event.pull_request.body }}
```

#### Use from another repository

Pin the action path in this repository:

```yaml
jobs:
  title:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: read
    steps:
      - uses: zrr1999/zendev/actions/validate-title@<ref>
        with:
          text: ${{ github.event.pull_request.title }}
```

```yaml
jobs:
  body:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: read
    steps:
      - uses: zrr1999/zendev/actions/validate-body@<ref>
        with:
          body: ${{ github.event.pull_request.body }}
```

By default, each wrapper runs the CLI from the same checked-out or pinned zendev
revision as the action itself. That keeps the wrapper and Python logic in sync.

Both actions also accept an optional `zendev-ref` input. Leave it unset for the
same-revision default, or pass a git ref if you intentionally want the wrapper
to install `zendev` from a different revision during a rollout.

### Use inside this repository

```bash
just install
```

That installs both `pre-commit` and `commit-msg` hooks for local development.
