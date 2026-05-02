# Copilot Instructions

## Scope
- This repository is a Python data project for the Benin Insights Challenge.
- Prefer small, explicit, reviewable changes.
- Optimize for Phase 1 delivery and reproducibility.

## Engineering Standards

### Code
- Pure functions by default, no hidden side effects.
- Immutability unless explicitly needed.
- One function = one thing, one abstraction level.
- Naming reveals intent, use domain language.
- Comments explain why, never what.
- Exceptions only — never return null, never pass null.
- No duplication — DRY (duplicate once, abstract on second repetition).
- No speculative code — YAGNI.
- Simplest solution that works — KISS.
- Boy Scout Rule — always leave code better than you found it.

### Design
- One reason to change per class — SRP.
- Depend on abstractions, not implementations — DIP.
- Hide third-party libs behind your own interfaces.
- Separation of concerns — UI / domain / infra never mix.
- Ubiquitous language — code vocabulary = business vocabulary.
- Design by contract — explicit preconditions, postconditions, invariants.

### Safety
- Data flow first — define inputs/outputs before any abstraction.
- Validate at boundaries — all external data is untrusted.
- Fail fast — crash loudly on invalid state, never silently continue.
- Structured logs only — JSON, correlation ID on every request.

### Tests
- Tests written before implementation — TDD.
- Test code = production code in quality.
- FIRST: Fast, Independent, Repeatable, Self-validating, Timely.

### Meta
- Complexity must earn its place.
- Start simple, evolve on real needs not hypothetical ones.
- Working → tests green → clean. Always in this order.

### Security
- Shift left — security is design, not an afterthought.
- OWASP Top 10 as baseline.
- Zero trust — never trust, always verify.
- Dependencies audited and updated regularly.

### API
- Contract first — define interface before implementation.
- Versioned from day one (/v1/).
- Errors documented as thoroughly as success cases.
- Documentation lives in the repo, updated in CI.

### Performance
- No premature optimization — profile first, optimize on evidence.
- Measure in production, not assumptions.
- Caching, pagination, query optimization by default on data-heavy paths.

## Repo Map
- `pipeline/` — extraction, transformation, load, validation.
- `notebooks/` — executable analysis scripts and experiments.
- `models/` — reusable ML logic.
- `dashboard/` — Streamlit app.
- `data/raw/` — source data.
- `data/processed/` — cleaned and aggregated data.
- `reports/` — summaries and deliverables.
- `docs/` — specs, context, and task definitions.

## Commands
```bash
make install
make lint
make test
```

## What To Do
- Check `docs/ml_specs.md` before coding.
- Keep `docs/ml_todo.md` updated as the ML work evolves; add/remove items when scope changes.
- Keep scripts idempotent.
- Validate inputs at file boundaries.
- Prefer the simplest implementation that satisfies the spec.

## What Not To Do
- Do not add logic in places that should only orchestrate.
- Do not invent abstractions before the second repetition.
- Do not hardcode paths or model settings when they belong in config.
- Do not return `None` for failure.
- Do not silently ignore missing or invalid data.

## Output Contract
- Every runnable script should define its input, output, and failure mode clearly.
- Every data export should be reproducible.
- Every change should keep the project understandable for the next contributor.
