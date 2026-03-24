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

### Use inside this repository

```bash
just install
```

That installs both `pre-commit` and `commit-msg` hooks for local development.
