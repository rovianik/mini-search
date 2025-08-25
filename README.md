# mini-search

A mini search engine with ranked retrieval (inverted index + BM25).  
Built to learn IR fundamentals through a practical, testable project.

![CI](https://github.com/rovianik/mini-search/actions/workflows/ci.yml/badge.svg)

## Quickstart

```bash
uv sync --locked
uv run ruff check .
uv run pytest -q
```

## Run the API (later in M3)

```bash
uv run python -m mini_search.api.http
```

## Project structure

- `src/mini_search` - core, index, query, api
- `tests/` - unit + golden tests (see tests/conftest.py)
- `.github/workflows/ci.yml` - uv-native CI (lockfile enforced)

## Milestones

- M0 - Tokenizer & Normalizer
- M1 - Index & BM25
- M2 - Focus Track (quality / efficiency / evaluation)
- M3 - Polish & API & Phrase

See `SPEC.md` for scope and deliverables.
