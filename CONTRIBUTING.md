# Contributing to GridPulse

Thanks for your interest! This project keeps a high, **enforced** quality bar — the CI
gates below are hard failures, so run them locally before pushing.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (manages the Python 3.11 toolchain and dependencies)
- Node 20+ (for the frontend, once it lands)

## Setup

```bash
uv sync --extra dev          # creates .venv (Python 3.11) and installs deps
uv run pre-commit install    # optional: run the gates on every commit
```

## Quality gates (must pass before a PR)

```bash
uv run ruff check .          # lint
uv run ruff format --check . # formatting
uv run mypy pipeline tests   # strict static types
uv run pytest                # tests + coverage threshold (see pyproject.toml)
```

`uv run ruff format .` and `uv run ruff check --fix .` auto-fix most issues.

## Conventions

- **Pure core, side effects at the edges.** Logic in `pipeline/` is pure and
  deterministic; I/O lives in CLIs and (later) the service layer.
- **Type everything.** `mypy --strict` is enforced.
- **Test the behavior, not the threshold.** If coverage drops, add a test that exercises
  the real gap rather than lowering the gate.
- **No secrets in the repo.** Use Application Default Credentials / environment variables.
- Keep changes small and behavior-preserving; document user-facing changes in
  `CHANGELOG.md`.
