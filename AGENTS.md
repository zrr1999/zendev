# AGENTS.md

## Cursor Cloud specific instructions

**zendev** is a pure-Python CLI toolkit (unified logging + emoji commit conventions). No external services, databases, or Docker required.

### Prerequisites (installed in VM snapshot)

- `uv` (Python package manager) — `~/.local/bin/uv`
- `just` (task runner) — `~/.local/bin/just`
- Both are on `$PATH` via `~/.local/bin`

### Key commands (all defined in `justfile`)

| Task | Command |
|---|---|
| Install deps | `uv sync --all-groups` |
| Run tests | `just test` (or `uv run pytest -v`) |
| Lint | `uvx ruff check` |
| Format check | `uvx ruff format --check` |
| Type check | `uv run pyright` |
| Full CI suite | `just ci` (format + check + coverage) |

### Gotchas

- The project uses `hatch-vcs` for versioning from git tags. If you see version-related build errors, ensure the workspace is a git repo with tags available (`git fetch --tags`).
- `just install` also runs `uvx prek install` which sets up git hooks. For cloud agents, `uv sync --all-groups` alone is sufficient for dependency installation.
- The `zendev-commit` CLI is interactive (uses `questionary`); test the commit functionality programmatically via `zendev-commit-msg <file>` or by importing `zendev.commit.message()` / `zendev.commit.commit_msg_hook()` directly.
- `pyproject.toml` `[tool.pytest]` uses `addopts` with `--strict-markers` and `--tb=short`.
