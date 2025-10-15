# Epoxy Leads - B2B Lead Generation System

A systematic lead sourcing and qualification system for B2B industries, built with web scraping, structured data extraction, and automated scoring.

## Overview

This project automates the discovery and qualification of business leads across multiple industry verticals by:
- Scraping public procurement portals, RFPs, and bid sites
- Extracting structured information using AI-powered parsing
- Scoring and prioritizing leads based on configurable criteria
- Generating CRM-ready CSV exports

## Features

- **Multi-Vertical Support**: Separate workflows for aviation, manufacturing, healthcare, pharma, culinary, and distribution verticals
- **Structured Data Pipeline**: Raw scraping → Parsed JSONL → Scored CSV
- **Evidence Tracking**: All leads linked to source URLs and extracted documents
- **Confidence Scoring**: AI-powered confidence ratings for data quality
- **Priority Ranking**: Configurable scoring rules for lead prioritization
- **Git Worktrees**: Isolated branches for each vertical using git worktrees

## Project Structure

```
epoxy-leads/
├── verticals/           # Industry-specific lead sources
│   ├── aviation/
│   ├── manufacturing/
│   └── [vertical]/
│       ├── sources/     # YAML config for scraping targets
│       ├── raw/         # Raw scraped content (gitignored)
│       ├── parsed/      # Structured JSONL (gitignored)
│       └── evidence/    # PDFs, HTML, screenshots (gitignored)
├── common/
│   ├── schemas/         # JSON schemas for lead data
│   └── rules/           # YAML scoring rules
├── outputs/             # Final CSV exports (gitignored)
├── shared/              # Shared utilities and documentation
└── WorkTree/            # Git worktrees for each vertical branch
```

## Setup

### Prerequisites

- Node.js (for any Node-based scraping tools)
- Python 3.8+ (for data processing)
- Git
- MCP (Model Context Protocol) server for Firecrawl (optional but recommended)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd epoxy-leads
```

2. Configure your scraping targets in `verticals/<vertical>/sources/`

3. Review and adjust scoring rules in `common/rules/score.yaml`

## Usage

### Workflow Commands

The project uses slash commands (see `claude.md` for full list):

```bash
# Seed a new vertical with initial targets
/seed-vertical aviation

# Scrape configured sources
/scrape-sources aviation

# Parse raw data into structured JSONL
/parse-drops aviation

# Score and prioritize leads
/score-leads aviation

# Export to CSV
/export-csv

# Package evidence files
/package-evidence aviation
```

### Git Workflow

Each vertical uses a separate branch via git worktrees:

```bash
# Create worktree for a new vertical
git worktree add WorkTree/healthcare -b feature/healthcare

# Work in the worktree
cd WorkTree/healthcare
# ... make changes ...
git add . && git commit -m "feat(healthcare): add initial sources"
git push origin feature/healthcare

# Create PR to merge into main
```

## Data Schema

Leads are normalized to a standard schema defined in `common/schemas/lead_schema.json`:

```json
{
  "company": "Company Name",
  "facility_name": "Facility or Project Name",
  "city": "City",
  "state": "ST",
  "confidence": 85,
  "score": 95,
  "priority": "A",
  "source_urls": ["https://..."],
  "notes": "Description of opportunity"
}
```

## Scoring System

Leads are scored based on configurable rules in `common/rules/score.yaml`:

- **Confidence**: 0-100, AI-assessed data quality
- **Score**: 0-100, business value assessment
- **Priority**: A/B/C tiers (A ≥ 80 confidence)

## Privacy & Security

All scraped data, parsed leads, and output files are excluded from version control via `.gitignore`:

- `/verticals/*/raw/` - Raw scraped content
- `/verticals/*/parsed/` - Parsed JSONL files
- `/verticals/*/evidence/` - Downloaded documents
- `/outputs/*.csv` - Generated lead lists
- Client-specific deliverable files

## Contributing

1. Create a new worktree for your vertical: `git worktree add WorkTree/<vertical> -b feature/<vertical>`
2. Add source configurations in `verticals/<vertical>/sources/`
3. Follow the standard workflow: scrape → parse → score → export
4. Keep commits atomic and use conventional commit format: `feat(<vertical>): description`
5. Create PR for review before merging to main

## Tech Stack

- **Web Scraping**: Firecrawl MCP, Playwright (fallback)
- **Data Processing**: Python, JSONL
- **AI Parsing**: LLM-based structured extraction
- **Version Control**: Git with worktrees
- **Documentation**: Markdown, YAML

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.

**What this means:**
- You can use, study, and modify this code freely
- If you distribute modified versions, you MUST share the source code
- If you run this as a web service, you MUST provide the source to users
- Commercial use requires explicit written permission
- You must give credit to the original author

This license ensures the code remains open source and prevents proprietary theft.

## Notes

This is a lead generation tool designed for B2B sales. All data is sourced from publicly available information (RFPs, procurement portals, public notices). Ensure compliance with website terms of service and applicable regulations.
