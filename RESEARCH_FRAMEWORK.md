# AI-Driven Lead Generation Platform - Project Blueprint

## 1. Vision & Success Criteria
- **Objective**: Build an automated lead generation and outreach platform that ingests high-level targeting prompts and delivers enriched contact lists, deep company dossiers, and personalized outreach copy.
- **Primary Outputs**:
  1. Structured lead dataset (min. three decision makers per company).
  2. Company research reports aligned to your research framework.
  3. Custom LinkedIn and email outreach copy per company.
  4. Exported Google Sheet with quality-reviewed data.
- **Success Metrics**:
  - ≥90% accuracy for core contact attributes (name, role, email, LinkedIn).
  - ≥80% of companies passing QA without manual edits.
  - Outreach templates scored ≥4/5 in internal quality rubric.
  - Turnaround time ≤4 hours for batches of 25 companies.

## 2. Core Capabilities & Tools
| Capability | Tools / Services | Notes |
| --- | --- | --- |
| Prompt capture & job orchestration | Web UI (Next.js) or CLI; Backend (FastAPI) | Stores targeting prompts, triggers pipeline runs. |
| Web search & scraping | Google Custom Search API, SerpAPI, Firecrawl, Crawl4AI, Playwright/Puppeteer | Handle discovery & structured extraction; include CAPTCHA fallback. |
| Enrichment & firmographic data | Apollo.io API, Clearbit, Crunchbase, Owler, LinkedIn Sales Navigator (if available) | Use provider SDKs or REST APIs with retry logic. |
| Contact discovery & verification | Apollo.io People API, Hunter.io, Dropcontact, NeverBounce | Sequence: gather candidates → verify email validity. |
| Research augmentation | OpenAI GPT-4o, Claude 3.5 Sonnet, Perplexity API | Summarize findings, follow research framework prompts. |
| Outreach generation & delivery | LLMs (same as above) with structured prompts; Prompt templates stored in DB; Aimfox (via Make) | Generate LinkedIn & email copy, enforce word count & tone; pass approved copy to Aimfox sequences. |
| Data storage | PostgreSQL (primary), Redis (queues/cache), S3-compatible storage (research artifacts) | Use Prisma/SQLAlchemy for ORM. |
| Workflow orchestration | Temporal.io, Airflow, or Prefect | Coordinate multi-stage pipeline with retries & human-in-loop gating. |
| QA & validation | Custom rule engine, schema validation (Pydantic/Marshmallow), email verification APIs | Automated QA plus manual review UI. |
| Delivery & reporting | Google Sheets API, Aimfox (via Make), GoHighLevel (GHL) API, Looker Studio dashboards, Slack/Email notifications | Push final data, sync outreach tasks/messages, maintain analytics. |

## 3. High-Level Architecture
1. **Front Door** (prompt intake): User submits targeting brief via UI or CLI → stored in `jobs` table.
2. **Orchestrator**: Workflow engine dequeues job, creates task graph for discovery, enrichment, research, outreach.
3. **Scraping Cluster**: Serverless functions or containerized workers perform web search, crawl company domains, capture raw text.
4. **Data Enrichment Layer**: Aggregates third-party API data (Apollo, Clearbit) and normalizes into canonical company & contact schemas.
5. **Research Engine**: LLM agents run research framework prompts against compiled artifacts; outputs structured JSON summaries.
6. **Outreach Generator**: LLM agent uses company profile + outreach framework to produce LinkedIn invites & emails, then packages payloads for Aimfox (via Make) and GHL sequences; includes tone/style checks.
7. **Quality Assurance Gate**: Validates schema, dedupes contacts, verifies emails, and optionally routes to human reviewer UI.
8. **Export & Sync Service**: Writes final records to Google Sheets workbook, pushes outreach payloads through Make to Aimfox, syncs contacts/opportunities to GHL via API, stores JSON/CSV in S3, and sends completion notification.
9. **Monitoring Layer**: Logs, metrics, and alerting (OpenTelemetry + Grafana + PagerDuty/Slack). Tracks API usage and QA failure rates.

## 4. Detailed Workflow (per job)
1. **Prompt Intake & Parsing**
   - Capture targeting prompt + optional filters (industry, geography, funding stage, employee count).
   - Use lightweight LLM prompt to extract structured filters → persist as `job_parameters`.
   - Run validation (ensure scope, banned industries, etc.).
2. **Company Discovery**
   - Fire off search queries via Google Custom Search / SerpAPI using extracted keywords.
   - Supplement with Apollo "Companies" API and Crunchbase search.
   - Store candidate companies with metadata (URL, description, source confidence).
   - De-duplicate via domain + company name fuzzy match (FuzzyWuzzy/RapidFuzz).
3. **Website Crawling & Signal Extraction**
   - Crawl home/about/product pages with Crawl4AI/Playwright.
   - Extract structured signals: industry terms, technology stack, funding mentions, locations.
   - Persist cleaned markdown + embeddings (OpenAI text-embedding-3-large) for retrieval.
4. **Contact Identification**
   - Query Apollo People API filtered by company domain and role keywords (e.g., "Head of Growth", "CEO").
   - If <3 contacts, fallback to LinkedIn scraping (PhantomBuster or custom Playwright) and enrichment via Dropcontact.
   - Run email verification (NeverBounce/Hunter) and mark confidence scores.
5. **Deep Research (per company)**
   - Aggregate sources: website crawl, news (NewsAPI, GDELT), funding databases (PitchBook if available), LinkedIn posts.
   - Feed documents into LLM research chain using your framework (e.g., Pain points, Growth signals, Tech stack, Buying triggers).
   - Output structured JSON (company profile, key initiatives, recent investments, reasons to reach out).
6. **Outreach Content Generation & Handoff**
   - Apply outreach framework prompts to create:
     - LinkedIn connection message (≤300 characters) tailored for Aimfox cadences.
     - Email subject & body (personalized opening, value proposition, CTA) structured for GHL campaigns.
   - Run style QA: enforce tone, banned phrases, grammar (LanguageTool API or GPT critique pass).
   - Package final copy + metadata into automation payloads (JSON) consumed by Make scenarios for Aimfox and the GHL API.
7. **Quality Assurance & Scoring**
   - Validate required fields using Pydantic schema.
   - Confirm ≥3 valid contacts; flag records needing manual review.
   - Scoring engine ranks leads (fit score, urgency score, data confidence).
   - Provide reviewer dashboard (React + FastAPI) to approve/reject flagged items.
8. **Export & Delivery**
   - Assemble final dataset: company info, contact info, research summary, outreach copy, channel-specific metadata (Aimfox campaign IDs, GHL pipeline stage).
   - Use Google Sheets API to create/update workbook tabs (Companies, Contacts, Outreach).
   - Trigger Make scenarios that push LinkedIn outreach assets and scheduling data into Aimfox.
   - Invoke GHL API to upsert companies/contacts, attach research notes, and enqueue personalized emails.
   - Email/Slack summary with run statistics, QA outcomes, and download links for JSON/CSV exports.
9. **Post-Run Analytics & Feedback Loop**
   - Log run metrics, API usage, contact success rates.
   - Sync outreach engagement metrics back from Aimfox and GHL (opens, replies, connection accepts).
   - Store human reviewer feedback to retrain scoring models and prompt templates.

## 5. Integrations & APIs
- **Search & Scraping**: Google Custom Search, SerpAPI, Bing Web Search, Crawl4AI, Firecrawl, Playwright/Puppeteer.
- **Company & Contact Data**: Apollo.io, Clearbit, Crunchbase, LinkedIn (official APIs or Sales Navigator), Owler, ZoomInfo (if licensed).
- **Email Verification**: NeverBounce, ZeroBounce, Hunter.io.
- **News & Investment Data**: NewsAPI, GDELT, PitchBook (enterprise), Crunchbase funding rounds.
- **LLM Providers**: OpenAI (GPT-4o, GPT-4.1), Anthropic (Claude 3.5), Azure OpenAI for enterprise controls.
- **Storage & Infra**: AWS S3, RDS PostgreSQL, Redis (ElastiCache), AWS Lambda/ECS for workers.
- **Productivity & Outreach**: Google Sheets API, Aimfox (via Make), GoHighLevel (GHL) API, Slack API, Notion API (optional knowledge base), Linear/Jira for task tracking.

## 6. Data Models (simplified)
```mermaid
erDiagram
    JOB ||--o{ COMPANY : includes
    COMPANY ||--o{ CONTACT : has
    COMPANY ||--o{ COMPANY_PROFILE : has
    COMPANY ||--o{ OUTREACH : generates
    CONTACT ||--o{ OUTREACH : personalized

    JOB {
      uuid id
      text prompt
      jsonb parameters
      text status
      timestamptz created_at
    }
    COMPANY {
      uuid id
      text name
      text website
      text domain
      text country
      text city
      jsonb attributes
      float discovery_confidence
    }
    CONTACT {
      uuid id
      uuid company_id
      text first_name
      text last_name
      text title
      text email
      text phone
      text linkedin_url
      float fit_score
      float email_confidence
    }
    COMPANY_PROFILE {
      uuid id
      uuid company_id
      jsonb research_summary
      jsonb investments
      jsonb reasons_to_reach_out
      jsonb sources
    }
    OUTREACH {
      uuid id
      uuid company_id
      uuid contact_id (nullable)
      text channel -- linkedin/email
      text subject
      text body
      jsonb qa_feedback
    }
```

## 7. Quality Assurance Strategy
- **Schema Validation**: Pydantic models enforce required fields and data types.
- **Automated Checks**:
  - Email deliverability status must be "valid" or "accept all" with confidence ≥0.7.
  - LinkedIn URLs verified via regex + HTTP status check.
  - Company profiles require ≥3 cited sources.
  - Outreach copy passes toxicity/tone check (Perspective API or LLM review).
  - Aimfox/Make scenario and GHL API responses log success status codes; retries on failure.
- **Human-in-the-loop**:
  - Reviewer UI for flagged records; track decisions for analytics.
  - Random sampling of 10% of leads for manual audit each run.
- **Feedback Loop**:
  - Capture bounce reports and reply outcomes from CRM to refine scoring.
  - Store QA annotations to improve prompts and heuristics.

## 8. Security, Compliance & Ethics
- Respect robots.txt and site terms; implement rate limiting and rotating proxies (Bright Data, ScraperAPI).
- Store API keys securely (AWS Secrets Manager, Hashicorp Vault).
- Ensure GDPR/CCPA compliance: only process publicly available business data; provide data removal workflow.
- Log all data access for auditing; encrypt PII at rest and in transit.
- Implement consent-based outreach policies; maintain suppression lists.

## 9. Infrastructure & Deployment
- **Environment**: AWS (ECS Fargate for services, Lambda for lightweight tasks) or GCP (Cloud Run + Workflows).
- **CI/CD**: GitHub Actions for testing & deployment; IaC via Terraform.
- **Monitoring**: CloudWatch/Stackdriver + Grafana dashboards; alert on API quota usage, error spikes, QA failure rate.
- **Scalability**: Horizontal autoscaling based on queue depth; separate compute pools for scraping vs. LLM workloads.
- **Cost Control**: Track API spend per job; implement throttling and caching; choose model variants based on task complexity.

## 10. Implementation Roadmap
1. **Phase 0 – Foundations (Week 1-2)**
   - Set up repo, CI/CD, infrastructure scaffolding.
   - Integrate user authentication and prompt intake UI.
   - Configure database schema and migrations.
2. **Phase 1 – Discovery & Contacts (Week 3-6)**
   - Implement search + scraping workers with retries.
   - Integrate Apollo API and contact verification flow.
   - Build QA schemas and basic reviewer dashboard.
3. **Phase 2 – Research & Outreach (Week 7-10)**
   - Implement research framework prompts and knowledge store.
    - Build outreach generation with QA and style enforcement; map payloads for Aimfox (via Make) and GHL email templates.
   - Add scoring model and analytics dashboards.
4. **Phase 3 – Automation & Delivery (Week 11-12)**
    - Automate Google Sheets export, Slack notifications, Aimfox sequence handoff (via Make), and GHL contact sync.
   - Harden monitoring, alerting, and cost tracking.
   - Conduct end-to-end tests and dry runs.
5. **Phase 4 – Optimization (Week 13+)**
   - Add human feedback loops, active learning for prompts.
   - Expand data providers, add CRM integration (HubSpot/Salesforce).
   - Implement A/B testing for outreach variants.

## 11. Team Roles & Skills
- **Product/Project Lead**: Manages requirements, QA rubric, prioritization.
- **Full-Stack Engineer**: Builds UI, backend, integrations, DevOps.
- **Data Engineer**: Manages scraping, data pipelines, storage, orchestration.
- **Prompt/Research Specialist**: Crafts research/outreach prompts, audits LLM output.
- **QA Analyst**: Designs quality checks, reviews flagged leads.

## 12. Documentation & Playbooks
- Maintain living Runbooks for each pipeline stage (scraping, enrichment, research).
- Provide API key management handbook and incident response plan.
- Document prompt templates, research framework, outreach frameworks in version-controlled knowledge base (Notion/Git).

---
**Next Steps**: Prioritize provider contracts (Apollo, Clearbit, email verification), finalize research/outreach frameworks, and set up sandbox environments to start implementing Phase 0.
