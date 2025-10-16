"""
Pydantic models for the AI Lead Generation Platform API
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

# Enums
class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ContactSeniority(str, Enum):
    C_LEVEL = "c_level"
    VP = "vp"
    DIRECTOR = "director"
    MANAGER = "manager"
    INDIVIDUAL = "individual"

class OutreachChannel(str, Enum):
    LINKEDIN = "linkedin"
    EMAIL = "email"
    PHONE = "phone"

class QAStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

# Base Models
class BaseResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime

# Job Models
class JobCreate(BaseModel):
    prompt: str = Field(..., description="Targeting prompt for lead generation")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional job parameters")
    vertical: Optional[str] = Field(None, description="Industry vertical")
    target_count: int = Field(25, ge=1, le=100, description="Target number of companies")
    quality_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Minimum quality threshold")

class JobResponse(BaseResponse):
    prompt: str
    parameters: Optional[Dict[str, Any]]
    status: JobStatus
    vertical: Optional[str]
    target_count: int
    quality_threshold: float
    completed_at: Optional[datetime]
    user_id: Optional[str]
    
    # Computed fields
    companies_found: Optional[int] = None
    contacts_found: Optional[int] = None
    outreach_generated: Optional[int] = None
    quality_score: Optional[float] = None

# Company Models
class CompanyAttributes(BaseModel):
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    revenue_range: Optional[str] = None
    funding_stage: Optional[str] = None
    technology_stack: Optional[List[str]] = None
    growth_signals: Optional[List[str]] = None
    pain_points: Optional[List[str]] = None

class CompanyResponse(BaseResponse):
    job_id: str
    name: str
    website: Optional[str]
    domain: Optional[str]
    country: Optional[str]
    city: Optional[str]
    state: Optional[str]
    attributes: Optional[CompanyAttributes]
    discovery_confidence: float
    fit_score: float
    
    # Computed fields
    contact_count: Optional[int] = None
    research_completed: Optional[bool] = None
    outreach_generated: Optional[bool] = None

# Contact Models
class ContactResponse(BaseResponse):
    company_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    title: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    linkedin_url: Optional[str]
    department: Optional[str]
    seniority_level: Optional[ContactSeniority]
    fit_score: float
    email_confidence: float
    email_status: Optional[str]
    verification_date: Optional[datetime]

# Research Models
class ResearchSummary(BaseModel):
    company_overview: str
    key_initiatives: List[str]
    recent_developments: List[str]
    competitive_position: str
    growth_opportunities: List[str]

class PainPoints(BaseModel):
    operational_challenges: List[str]
    technology_gaps: List[str]
    compliance_requirements: List[str]
    cost_pressures: List[str]

class GrowthSignals(BaseModel):
    recent_funding: Optional[Dict[str, Any]]
    hiring_trends: List[str]
    expansion_plans: List[str]
    technology_adoption: List[str]

class TechStack(BaseModel):
    primary_technologies: List[str]
    infrastructure: List[str]
    development_tools: List[str]
    cloud_platforms: List[str]

class BuyingTriggers(BaseModel):
    immediate_needs: List[str]
    budget_cycle: Optional[str]
    decision_makers: List[str]
    evaluation_criteria: List[str]

class CompanyProfileResponse(BaseResponse):
    company_id: str
    research_summary: ResearchSummary
    pain_points: PainPoints
    growth_signals: GrowthSignals
    tech_stack: TechStack
    buying_triggers: BuyingTriggers
    recent_investments: Optional[Dict[str, Any]]
    reasons_to_reach_out: List[str]
    sources: List[Dict[str, Any]]
    research_confidence: float

# Outreach Models
class OutreachContentResponse(BaseResponse):
    company_id: str
    contact_id: Optional[str]
    channel: OutreachChannel
    subject: Optional[str]
    body: str
    tone: str
    word_count: Optional[int]
    qa_feedback: Optional[Dict[str, Any]]
    quality_score: float
    status: str

class OutreachGenerationRequest(BaseModel):
    company_id: str
    contact_ids: Optional[List[str]] = None
    channels: List[OutreachChannel] = [OutreachChannel.LINKEDIN, OutreachChannel.EMAIL]
    tone: str = "professional"
    custom_requirements: Optional[Dict[str, Any]] = None

# QA Models
class QAReviewRequest(BaseModel):
    record_type: str = Field(..., description="Type of record being reviewed")
    record_id: str = Field(..., description="ID of the record")
    status: QAStatus = Field(..., description="Review decision")
    feedback: Optional[str] = Field(None, description="Review feedback")
    score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality score")

class QAReviewResponse(BaseResponse):
    record_type: str
    record_id: str
    reviewer_id: Optional[str]
    status: QAStatus
    feedback: Optional[str]
    score: Optional[float]
    reviewed_at: Optional[datetime]

# Export Models
class ExportRequest(BaseModel):
    job_id: str
    format: str = Field("google_sheets", description="Export format")
    include_contacts: bool = True
    include_research: bool = True
    include_outreach: bool = True
    filters: Optional[Dict[str, Any]] = None

class ExportResponse(BaseResponse):
    job_id: str
    format: str
    status: str
    download_url: Optional[str]
    record_count: Optional[int]

# Analytics Models
class UsageAnalytics(BaseModel):
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_companies: int
    total_contacts: int
    total_outreach: int
    api_calls: Dict[str, int]
    costs: Dict[str, float]
    average_processing_time: float

class QualityMetrics(BaseModel):
    overall_quality_score: float
    contact_accuracy: float
    email_verification_rate: float
    outreach_approval_rate: float
    qa_failure_rate: float
    human_review_rate: float

# Error Models
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Validation helpers
@validator('email', pre=True, always=True)
def validate_email(cls, v):
    if v and '@' not in v:
        raise ValueError('Invalid email format')
    return v

@validator('linkedin_url', pre=True, always=True)
def validate_linkedin_url(cls, v):
    if v and not v.startswith(('http://', 'https://')):
        v = f"https://{v}"
    return v
