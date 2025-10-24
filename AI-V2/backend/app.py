from __future__ import annotations

import asyncio
import uuid
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.core.logging import setup_logging, logger
from backend.core.settings import get_settings
from backend.schemas.lead import CompanyProfile, Contact, LeadResponse
from backend.services.ai_research import AIResearchService
from backend.services.persistence import JobRecord, PersistenceService
from backend.utils.validators import is_senior_title

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"]
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

ai_service = AIResearchService()
persistence = PersistenceService()

FRONTEND_INDEX = "frontend/index.html"


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(FRONTEND_INDEX)


@app.post("/leads/generate", response_model=LeadResponse)
async def generate_leads(payload: Dict[str, str | int | None]) -> LeadResponse:
    target_count = int(payload.get("target_count", 10))
    target_count = max(1, min(target_count, 50))
    prompt = str(payload.get("prompt") or "Discover institutional investors for Hazen Road")

    job_id = str(uuid.uuid4())
    logger.info("Job %s started (target_count=%s)", job_id, target_count)

    persistence.append_log(job_id, "INFO", "Job started")

    collected_contacts: List[Contact] = []
    company_profiles: List[CompanyProfile] = []
    seen_contacts: set[tuple[str, str]] = set()

    attempts = 0
    while len(collected_contacts) < target_count and attempts < settings.max_lead_attempts:
        remaining = target_count - len(collected_contacts)
        persistence.append_log(
            job_id,
            "INFO",
            f"Requesting {remaining} more leads from AI (attempt {attempts + 1})",
        )
        batch = await ai_service.generate_leads(prompt, remaining)
        if not batch:
            persistence.append_log(job_id, "WARNING", "AI returned no companies")
            break

        for record in batch:
            company_profiles.append(CompanyProfile(**record))
            for contact in record.get("contacts", []):
                if not is_senior_title(contact.get("title")):
                    continue
                key = (
                    (contact.get("name") or "").lower(),
                    (record.get("company") or "").lower(),
                )
                if key in seen_contacts:
                    continue
                seen_contacts.add(key)
                collected_contacts.append(Contact(**contact, company=record.get("company")))
                if len(collected_contacts) >= target_count:
                    break
            if len(collected_contacts) >= target_count:
                break

        attempts += 1

    status = "completed" if len(collected_contacts) >= target_count else "partial"
    persistence.append_log(job_id, "INFO", f"Job finished with {len(collected_contacts)} leads ({status})")

    record = JobRecord(
        job_id=job_id,
        status=status,
        prompt=prompt,
        target_count=target_count,
        leads=[c.dict(by_alias=True) for c in collected_contacts],
        raw_response={"company_profiles": [cp.dict() for cp in company_profiles]},
    )
    persistence.save_job(record)

    return LeadResponse(
        job_id=job_id,
        status=status,
        target_count=target_count,
        leads=collected_contacts,
        company_profiles=company_profiles,
    )


@app.get("/leads/{job_id}", response_model=LeadResponse)
async def get_leads(job_id: str) -> LeadResponse:
    job = persistence.load_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    leads = [Contact(**lead) for lead in job["leads"]]
    profiles = [CompanyProfile(**profile) for profile in job["raw_response"].get("company_profiles", [])]

    return LeadResponse(
        job_id=job_id,
        status=job["status"],
        target_count=job["target_count"],
        leads=leads,
        company_profiles=profiles,
    )


@app.get("/logs/{job_id}")
async def get_logs(job_id: str) -> List[Dict[str, str]]:
    return persistence.fetch_logs(job_id)
