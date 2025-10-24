from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Contact(BaseModel):
    name: str
    title: str
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = Field(None, alias="linkedin_url")
    confidence: float = Field(0.6, ge=0, le=1)

    class Config:
        allow_population_by_field_name = True


class CompanyProfile(BaseModel):
    company: str
    website: Optional[str] = None
    hq: Optional[str] = None
    aum: Optional[str] = None
    strategy_summary: Optional[str] = None
    alignment_score: Optional[int] = Field(None, ge=0, le=100)
    reasons: List[str] = []
    sources: List[str] = []
    contacts: List[Contact] = []


class LeadResponse(BaseModel):
    job_id: str
    status: str
    target_count: int
    leads: List[Contact]
    company_profiles: List[CompanyProfile]
    created_at: datetime = datetime.utcnow()
