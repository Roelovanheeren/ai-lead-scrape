# Project: Epoxy Flooring Lead Sourcing (CT & Westchester)

## Guardrails (MUST follow)
- Throttle requests; no aggressive concurrency.
- Every lead must include source_urls[] and at least one evidence artifact (PDF/HTML/screenshot path).

## Tech & Tools
- Scraping: Firecrawl MCP (primary), Playwright only if needed.
- Parsing: normalize to JSONL per lead_schema (common/schemas/lead_schema.json).
- Outputs: CSV in outputs/leads.csv; per-vertical CSVs; evidence in verticals/*/evidence.

## Structure
verticals/<vertical>/{sources,raw,parsed,evidence}
common/{schemas,rules}
outputs/{leads.csv,leads_priority_A.csv}

## Git Rules
- One branch per vertical (worktrees). Never push directly to main.
- Small atomic commits; PR titles: feat(<vertical>): <summary>

## Success Criteria
- Fields filled per schema; confidence ≥80 for Priority A.
- Evidence files resolve; links valid.

## Handy Commands
- /seed-vertical {vertical}
- /scrape-sources {vertical}
- /parse-drops {vertical}
- /score-leads {vertical}
- /export-csv
- /package-evidence {vertical}
