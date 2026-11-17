# albert

albert is a generic financial spreading system. It reads financial statement PDFs (UK Companies House full accounts and US SEC 10-Ks) and produces a standard spread: balance sheet, income statement, cash flow and key ratios. Every number must trace back to its page in the source.

It is also the pilot for an AI-first XP experiment. The premise under test: humans own intent, constraints and validation; code is a regenerable build output. See `docs/plan.md` for the full plan, hypotheses (H1 to H4) and metrics.

## People and roles

- **John** is the developer and the customer. He writes and signs off stories, the spread template and the golden spreads. Ask him when intent is unclear; do not guess domain rules.
- Claude Code builds the system. OpenAI models run inside the product. Do not swap the in-product LLM without an ADR.

## Stack

- Python (typed, `mypy --strict`), formatted and linted with `ruff`.
- Neo4j for the graph store, with FIBO loaded via the neosemantics (n10s) plugin. Start with a small FIBO subset (legal entity, reporting period, statement type).
- OpenAI API with schema-constrained structured output for extraction.
- PDF text and tables via PyMuPDF or pdfplumber. OCR and scanned PDFs come later.
- FastAPI service plus a simple review screen.
- Everything runs locally as Docker containers (`docker compose`). No production credentials anywhere in the repo or the agent's environment.

## Architecture

Module boundaries, in pipeline order: `ingest` → `extract` → `map` → `check` → `store` → `serve`.

- Each module depends only on the ones before it. This will be enforced with import-linter rules; do not cross a boundary to make a test pass.
- Domain types are Pydantic models and JSON schemas. The spread template is a versioned file in the repo.
- Do not add a dependency without an ADR in `docs/adr/`.

## How we work (XP, enforced)

1. **TDD, always.** Red, green, refactor. Write a failing test before any production code. Run it and see it fail for the right reason before implementing.
2. **Tests are locked once agreed.** When implementing, do not edit or weaken tests that already exist. If a test looks wrong, stop and say why; a human or the test-author step changes it.
3. **Small increments.** One thin slice at a time, small diffs, frequent commits to trunk. If a change is getting large, split it.
4. **Stories carry executable examples** (a PDF in, the expected spread out). A story is done only when its acceptance tests pass.
5. **Refactor freely, but only on green.**
6. **Never skip, disable or xfail a test to get green.**

## Validation gates (every change, in order)

1. Tests first and locked.
2. Static checks: ruff, mypy strict, import-linter, bandit, pip-audit.
3. Test quality: mutation testing (mutmut) on changed code; property-based tests (Hypothesis) for the checks, e.g. "any balanced sheet passes the identity check".
4. Product evals: any change to extraction, mapping or prompts runs the golden dataset and reports field-level accuracy. A drop beyond tolerance blocks the merge.
5. Review: an independent reviewer pass with fresh context against the story and ADRs, then John reviews the story, test diff and eval report.
6. Release: feature flag per slice, smoke run on held-back PDFs inside the Docker stack.

## Domain rules

- **Accounting identities are oracles.** Assets = liabilities + equity; subtotals add up; sign conventions hold; periods are consistent. Failures are flagged, never hidden or silently "fixed".
- **Provenance is mandatory.** Every extracted value carries source document, page and position, and keeps it in Neo4j.
- **Spread template** is assembled, not invented:
  - Line items: EdgarTools standard concepts (MIT), about 95 normalised items mapped from US GAAP XBRL tags.
  - Subtotals and identities: Fundamental Accounting Concepts (Assets, LiabilitiesAndEquity, NetCashFlow).
  - UK mapping: FRC taxonomy suite (FRS 102 and IFRS) onto the same line items.
  - Layout and ratios: ProSight Guide to Spreading conventions (current/non-current split, common-size, ratios, net worth reconciliation).
- **UK filings must be full accounts.** Micro-entity and abridged accounts omit most of the income statement.
- **Golden dataset** (20 to 30 PDFs, UK and US): draft golden spreads are generated from the filings' iXBRL/XBRL tags, then John checks them. This dataset validates both the product and the agents; treat it as the most valuable asset in the repo.

## LLM calls in the product

- Prompts and output schemas are versioned files in the repo. Change them only with an eval run attached.
- Record OpenAI responses and replay them in unit tests, so tests are fast, deterministic and free. Live calls belong in the eval suite only.
- Never commit API keys. Read them from the environment (`.env` is git-ignored).

## Thin slices, in order

1. One digital PDF, balance sheet only, extracted to JSON and checked against its golden spread.
2. Balance-sheet identity checks, failures flagged.
3. Income statement and cash flow.
4. Neo4j storage with provenance.
5. Mapping to FIBO concepts.
6. Multi-period spreads and ratios.
7. Review screen for low-confidence items.
8. Varied layouts, then scanned PDFs.

## Agent skills

### Issue tracker

Issues and PRDs live in Jira project KAN at clogweeny.atlassian.net, accessed via the Atlassian MCP server (`.mcp.json`). See `docs/agents/issue-tracker.md`.

### Triage labels

Jira labels using the default names (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Open questions

- Token budget (OpenAI and Claude) per week: not decided yet. Keep usage visible in logs.
- GitHub repo (`iamjohnhawkins/albert`) and GitHub Actions CI are set up: ruff, mypy strict and pytest run on every push and pull request (KAN-5). Further gates are added as they become relevant.
