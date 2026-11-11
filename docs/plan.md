# AI-first XP: pilot and methodology plan

> Snapshot exported on 2026-11-11 from the living plan doc: https://claude.ai/artifact/67uLMExvBa8LHLgQbzeBh6. Edit there or here, but say which copy is current.

Nov 10, 2026 · @John Hawkins

## Purpose and hypotheses

We will build a real financial spreading system with a team of 1 to 2 humans plus AI agents, and measure whether quality holds while velocity rises. The working premise is that human effort should go into constraints on the LLM and validation before production, not into writing code.

Hypotheses to confirm or reject:

1. **H1, regenerability:** a module can be deleted and regenerated from its specs, tests and constraints alone, and still pass every gate.
2. **H2, quality holds:** escaped defects and change failure rate are no worse than a typical 4 to 6 person XP team.
3. **H3, velocity rises:** lead time per story falls and throughput per human rises, at an acceptable token cost.
4. **H4, XP still applies:** TDD, small releases and pairing remain the core loop. What changes is who does each part.

Three outcomes: a tooling harness, an evaluated pilot, and a written methodology.

## Pilot: a generic financial spreading system

The pilot takes financial statement PDFs and produces a standard spread: balance sheet, income statement, cash flow and key ratios, with every number traceable to its page in the source. Stack: Python, OpenAI models, Neo4j, and the FIBO ontology, running as Docker containers locally.

**Why it is a good test.** The system is itself LLM-based, so we have to solve validation twice: once for the code the agents write, and once for the answers the product gives. Accounting also gives us hard, checkable rules (assets equal liabilities plus equity, subtotals add up), which make strong oracles.

**Components**

- **Ingest:** PDF text and table extraction (PyMuPDF or pdfplumber). Scanned documents and OCR come later.
- **Extract:** OpenAI calls with schema-constrained structured output, returning line items with page and position.
- **Map:** line items mapped to a canonical spread template and to FIBO concepts (legal entity, reporting period, statement type).
- **Check:** accounting identities, subtotal sums, sign conventions and period-to-period consistency.
- **Store:** Neo4j graph of entity, period, statement and line item, with provenance back to the source. FIBO loaded via the neosemantics (n10s) plugin, using a small subset of FIBO at first.
- **Serve:** a FastAPI service and a simple review screen where a human confirms or corrects low-confidence items.

**Golden dataset.** We need 20 to 30 annotated PDFs to start, with the correct spread for each. The sources are UK Companies House accounts and US SEC 10-K reports. Both are filed with inline XBRL tags, so a draft golden spread can be generated from the tags and John checks it, rather than typing every number. For UK filings we need full accounts, because micro-entity and abridged accounts leave out most of the income statement. This dataset is the most valuable asset in the project, because it validates both the product and the agents.

**Thin slices, in order**

1. One digital PDF, balance sheet only, extracted to JSON and checked against its golden spread.
2. Balance-sheet identity checks, with failures flagged rather than hidden.
3. Income statement and cash flow.
4. Graph storage in Neo4j with provenance.
5. Mapping to FIBO concepts.
6. Multi-period spreads and ratios.
7. Review screen for low-confidence items.
8. Varied layouts, then scanned PDFs.

## Spread template

No free, complete bank spread template exists. The common ones (ProSight Annual Statement Studies, formerly RMA, and Moody's CreditLens) are proprietary. The proposal is to assemble one from three open sources rather than invent it.

| Part | Source | What it gives us |
| --- | --- | --- |
| Line items | [EdgarTools standard concepts](https://edgartools.readthedocs.io/en/latest/xbrl/concepts/standardization/) (MIT licence) | About 95 normalised line items across balance sheet, income statement and cash flow, already mapped from US GAAP XBRL tags |
| Subtotals and identities | [Fundamental Accounting Concepts](https://xbrlsite.azurewebsites.net/2024/prototypes/ListOfFundamentalAccountingConcepts.html) (XBRL US and Charles Hoffman) | The roll-up concepts (Assets, LiabilitiesAndEquity, NetCashFlow) that our identity checks use |
| UK mapping | [FRC taxonomy suite](https://www.frc.org.uk/library/standards-codes-policy/accounting-and-reporting/frc-taxonomies/current-frc-taxonomy-suites/2025-uk-and-irish-digital-reporting-taxonomies/) (FRS 102 and IFRS) | The tags in Companies House filings, mapped onto the same line items |
| Layout and ratios | [ProSight Guide to Spreading](https://www.prosightfa.org/wp-content/uploads/2025/10/ProSight-Guide-to-Spreading.pdf) | Banking conventions: current and non-current split, common-size statements, ratios, net worth reconciliation |

The template becomes a versioned file in the repository, and is the first thing John signs off as customer.

## Constraint layers on the LLM

Constraints are what humans author and review. Each layer should be enforced by a tool wherever possible, because prose instructions alone are advisory to an LLM.

| Layer | What it holds | How it is enforced |
| --- | --- | --- |
| Intent | Stories with executable acceptance criteria, written as examples (a PDF in, the expected spread out) | Acceptance tests run in CI; a story is done only when they pass |
| Domain | Spread template, FIBO subset, accounting rules | Pydantic models and JSON schemas; graph schema constraints in Neo4j |
| Architecture | Module boundaries (ingest, extract, map, check, store, serve), ADRs | import-linter rules in CI; agents may not add dependencies without an ADR |
| Conventions | Coding style, test style, naming | CLAUDE.md, skills, ruff, mypy in strict mode |
| Process | Red-green-refactor, small diffs | Claude Code hooks: no production edit without a failing test; test files locked to the implementing agent; diff size limit |
| Blast radius | What agents may touch and run | Sandboxed containers, scoped permissions, no production credentials |
| Product prompts | Prompts and output schemas for the OpenAI calls | Versioned in the repo, changed only with an eval run attached |

## Validation gates

Every change passes the same gates in order, and any failure goes back to the agent, not to a human. Humans review at gate 5 only, and they review intent and evidence rather than lines of code.

1. **Tests first and locked.** A test-author agent (or a human) writes the failing tests from the acceptance criteria. The implementing agent cannot change them.
2. **Static checks.** ruff, mypy strict, import-linter, plus security and dependency scans (bandit, pip-audit).
3. **Test quality.** Mutation testing (mutmut) on changed code, and property-based tests (Hypothesis) for the checks, such as "any balanced sheet passes the identity check". This catches tests that only confirm what the AI wrote.
4. **Product evals.** Any change to extraction, mapping or prompts runs the golden dataset and reports field-level accuracy. A drop beyond a set tolerance blocks the merge. OpenAI calls are recorded and replayed in unit tests so they stay fast and repeatable.
5. **Review.** An independent reviewer agent with fresh context checks the diff against the story and the ADRs. Then a human reviews the story, the test diff and the eval report.
6. **Release.** Small merges to trunk, a feature flag per slice, and a smoke run on a held-back set of PDFs inside the Docker stack.

## XP practices and team roles

The XP values stay the same. What changes is who does each part of the work.

| XP practice | Who does it now | What changes |
| --- | --- | --- |
| Planning game | Humans with the customer | Stories must carry executable examples before an agent picks them up |
| TDD | Human owns the test list; agents run red-green-refactor | Tests are locked from the implementer, and mutation score proves they bite |
| Pair programming | Human navigates, agent drives; or an author agent paired with a critic agent | The human pairs with several agent streams in turn |
| Small releases | Agents, behind gates | Slices shrink to hours, not days |
| Refactoring | Agents, continuously | Nearly free, but only as safe as the tests |
| Collective ownership | Humans own specs, tests and constraints | Code is treated as a regenerable build output |
| Continuous integration | CI runs every gate on every change | Product evals join unit tests in CI |
| Customer on site | Domain expert in credit or spreading | Writes and checks the golden spreads |

**Team shape.** Two humans instead of four to six. One leans towards intent (stories, golden data, acceptance tests). The other leans towards constraints (harness, gates, evals). They swap roles each iteration, keeping XP's shared knowledge and bus-factor protection.

## Metrics

The harness records these automatically from git, CI and agent logs, so measuring costs no human time.

| Metric | Tests | Source |
| --- | --- | --- |
| Lead time per story (hours) | H3 | Story start to merge |
| Stories per human per week | H3 | Tracker and git |
| Human hours per story | H3 | Simple time log |
| Token cost per story (USD) | H3 | Agent and OpenAI usage logs |
| Change failure rate (%) | H2 | Reverted or hot-fixed merges |
| Escaped defects per slice | H2 | Bugs found after release |
| Mutation score (%) | H2 | mutmut in CI |
| Field-level extraction accuracy (%) | H2 | Golden dataset evals |
| Gate catch rate (%) | H2 | Injected faults caught before merge |
| Regeneration pass rate (%) | H1 | Modules regenerated from specs that pass all gates |
| Rework rate (%) | H4 | Agent attempts rejected at gates |

**Baseline.** There is no 4 to 6 person team building this in parallel. The comparison will be against your estimates for a traditional team, made before each slice starts, plus published DORA benchmarks.

## Phased plan

The proposed plan runs for about 14 weeks, part time, with each phase ending at a clear exit test. The durations are first estimates, to revisit after phase 1.

| Phase | Weeks | Work | Exit test |
| --- | --- | --- | --- |
| 0 Frame | 1 to 2 | Hypotheses and metrics; spread template; first 10 golden PDFs | Baseline set |
| 1 Harness | 3 to 5 | Repo and CLAUDE.md; TDD hooks and test lock; CI gates and eval runner; metrics capture | Slice 1 green |
| 2 Pilot | 6 to 11 | Weekly iterations on slices 1 to 6; retros tune the constraints | Slices shipped |
| 3 Experiments | 12 to 13 | Regenerate modules; inject faults; compare to baseline | H1 to H4 judged |

Methodology document: drafted in week 1, updated at every retro, final in week 14.

The methodology document is a living document from day one. Each retro adds what worked, what failed and which constraints changed, so the final version describes practice we actually followed.

## Assumptions and open questions

Assumptions made so far, to confirm or change:

- Claude Code builds the system, while OpenAI models run inside the product.
- Code lives in a new GitHub repository, with GitHub Actions for CI.
- John is the only human at the start; a second person may join later.
- We start with the weaker form of the premise: humans read code only when a gate flags it. The strong form (nobody reads code) is tested in the regeneration experiments.

Open questions:

- [x] Who plays the customer and checks the golden spreads? John.
- [x] Is there a preferred spread template? Find one: see Spread template.
- [x] Which filings seed the golden dataset? Both UK and US.
- [ ] What is the weekly budget for tokens (OpenAI and Claude)? Not decided yet.
