# Contributing

- Use feature branches + PRs; `main` is protected and requires green CI.
- Install deps with `uv sync --locked` (lockfile is the source of truth).
- Run locally: `ruff check . && pytest -q && pre-commit run --all-files`.
- Merge with **Squash & merge** to keep linear history.
- Update `uv.lock` when changing deps: `uv lock` + commit both files.
- Performance work follows the spec’s **Complexity Gates**.
