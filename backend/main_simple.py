"""
REWRITTEN Lead Generation Backend - NO SIMULATION, REAL DATA ONLY
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import uuid
import os
import asyncio
import re
import base64
import io
import zipfile
from xml.etree import ElementTree as ET

PDF_EXTRACTION_AVAILABLE = False
try:
    from pdfminer.high_level import extract_text as pdf_extract_text

    PDF_EXTRACTION_AVAILABLE = True
except Exception as pdf_import_error:  # pragma: no cover - logging only
    pdf_extract_text = None
    logging.getLogger(__name__).warning(
        "PDF extraction library not available: %s", pdf_import_error
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import real research functions
REAL_RESEARCH_AVAILABLE = False
try:
    from services.real_research import (
        extract_targeting_criteria,
        search_companies,
        research_company_deep,
        find_company_contacts
    )
    from services.hunter_client import hunter_client
    REAL_RESEARCH_AVAILABLE = True
    logger.info("✅ Real research engine loaded successfully")
except ImportError as e:
    logger.error(f"❌ Real research engine not available: {e}")
    logger.error("❌ System will not work without real research!")
    REAL_RESEARCH_AVAILABLE = False

# Pydantic models
from pydantic import BaseModel

class JobCreate(BaseModel):
    prompt: str
    target_count: int = 10
    quality_threshold: float = 0.8
    knowledge_base_documents: List[Dict[str, Any]] = []
    exclude_existing_leads: bool = False
    existing_leads: List[Any] = []


class KnowledgeBaseExtractRequest(BaseModel):
    name: str
    type: str
    data: str  # Base64 encoded file contents


class KnowledgeBaseExtractResponse(BaseModel):
    text: str
    summary: str
    category: str
    word_count: int

# FastAPI app
app = FastAPI(
    title="AI Lead Generation Platform",
    description="Real lead generation using Google Search + Hunter.io",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Job storage
job_storage = {}
container_start_time = datetime.utcnow().isoformat()


def extract_company_name_from_prompt(prompt: str) -> Optional[str]:
    """Extract company name if user asks for specific company
    
    Examples:
    - "Find leads at Center Square Investment" -> "Center Square Investment"
    - "Get contacts from CenterSquare" -> "CenterSquare"
    - "leads from the investment firm Center Square" -> "Center Square"
    """
    
    # Pattern 1: "at/from/for [Company Name]" (greedy capture until common stop words)
    # Matches: "leads at CenterSquare Investment Management" or "from Center Square"
    pattern1 = r'(?:at|from|for)\s+(?:the\s+)?(?:investment\s+)?(?:firm\s+)?([A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*(?:\s+(?:Investment|Management|Capital|Partners|Group|Corp|Inc|LLC))*)'
    
    # Pattern 2: Capitalized company names (handles "CenterSquare Investment" or "Center Square Investment")
    # Matches both single words like "CenterSquare" and multi-word like "Center Square Investment Management"
    pattern2 = r'\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*(?:\s+(?:Investment|Management|Capital|Partners|Group|Corp|Inc|LLC))+)\b'
    
    # Pattern 3: Single capitalized word followed by business suffix (CenterSquare Investment)
    pattern3 = r'\b([A-Z][a-z]*[A-Z][a-z]*(?:\s+(?:Investment|Management|Capital|Partners|Group))*)\b'
    
    # Try patterns in order
    for pattern in [pattern1, pattern2, pattern3]:
        match = re.search(pattern, prompt)
        if match:
            company_name = match.group(1).strip()
            
            # Clean up trailing common words that aren't part of company name
            company_name = re.sub(r'\s+(?:in|the|from|at|for|and|or)$', '', company_name, flags=re.IGNORECASE)
            
            # Ignore very short matches or common false positives
            ignore_list = ['the', 'investment', 'firm', 'company', 'center', 'square']
            if len(company_name) >= 5 and company_name.lower() not in ignore_list:
                logger.info(f"🎯 Detected specific company request: '{company_name}'")
                return company_name
    
    # Fallback: if prompt is just a capitalized company name with no other words
    # Matches: "CenterSquare" or "Center Square"
    if len(prompt.split()) <= 4:  # Short prompt, might be just company name
        words = prompt.split()
        capitalized_words = [w for w in words if w[0].isupper() and len(w) > 3]
        if len(capitalized_words) >= 1:
            company_name = ' '.join(capitalized_words)
            logger.info(f"🎯 Detected simple company name: '{company_name}'")
            return company_name
    
    return None


def _decode_base64(data: str) -> bytes:
    """Decode base64 data with graceful error handling."""

    try:
        return base64.b64decode(data, validate=True)
    except Exception:
        # Accept non-padded strings by adding padding if needed
        padding_needed = len(data) % 4
        if padding_needed:
            data += "=" * (4 - padding_needed)
        return base64.b64decode(data)


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    if not PDF_EXTRACTION_AVAILABLE or pdf_extract_text is None:
        raise HTTPException(
            status_code=400,
            detail="PDF extraction is not available on this server. Please install pdfminer.six.",
        )

    with io.BytesIO(file_bytes) as buffer:
        return pdf_extract_text(buffer) or ""


def _extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as docx_zip:
            xml_data = docx_zip.read("word/document.xml")
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail="DOCX file is missing document.xml content.",
        )
    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=400,
            detail="Invalid DOCX file provided.",
        )

    tree = ET.fromstring(xml_data)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    text_runs = []

    for node in tree.iter():
        if node.tag == f"{namespace}t" and node.text:
            text_runs.append(node.text)

    return "\n".join(text_runs)


def _extract_text_from_plain(file_bytes: bytes, encoding: str = "utf-8") -> str:
    try:
        return file_bytes.decode(encoding)
    except UnicodeDecodeError:
        # Attempt with latin-1 as fallback to preserve bytes
        return file_bytes.decode("latin-1")


def _infer_category(name: str, text: str) -> str:
    normalized_name = name.lower()
    normalized_text = text.lower()

    research_keywords = [
        "research",
        "icp",
        "ideal customer",
        "target",
        "persona",
        "prospect",
    ]
    outreach_keywords = [
        "outreach",
        "email",
        "script",
        "message",
        "copy",
        "sequence",
    ]

    def contains_keywords(target: str, keywords: List[str]) -> bool:
        return any(keyword in target for keyword in keywords)

    if contains_keywords(normalized_name, research_keywords) or contains_keywords(
        normalized_text, research_keywords
    ):
        return "research_guide"

    if contains_keywords(normalized_name, outreach_keywords) or contains_keywords(
        normalized_text, outreach_keywords
    ):
        return "outreach_playbook"

    if any(word in normalized_name for word in ["persona", "profile", "audience"]):
        return "audience_profile"

    return "other"


def _summarize_text(text: str, max_sentences: int = 3, max_chars: int = 400) -> str:
    cleaned = " ".join(text.split())
    if not cleaned:
        return ""

    sentence_endings = re.compile(r"(?<=[.!?])\s+")
    sentences = sentence_endings.split(cleaned)
    summary_sentences = sentences[:max_sentences]
    summary = " ".join(summary_sentences)

    if len(summary) > max_chars:
        summary = summary[: max_chars - 3].rstrip() + "..."

    return summary


def _extract_text_from_document(name: str, mime_type: str, file_bytes: bytes) -> Tuple[str, str, str]:
    mime_type = (mime_type or "").lower()
    name_lower = name.lower()

    if mime_type in {"text/plain", "text/markdown", "application/json", "application/xml"}:
        text = _extract_text_from_plain(file_bytes)
    elif mime_type == "application/pdf" or name_lower.endswith(".pdf"):
        text = _extract_text_from_pdf(file_bytes)
    elif mime_type in {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    } or name_lower.endswith(".docx"):
        text = _extract_text_from_docx(file_bytes)
    else:
        # Fallback: try UTF-8 decode
        text = _extract_text_from_plain(file_bytes)

    summary = _summarize_text(text)
    category = _infer_category(name, text)
    return text, summary, category


async def find_specific_company(company_name: str, original_prompt: str = "") -> Optional[Dict[str, Any]]:
    """Search for a specific company by name with context from original prompt
    
    Args:
        company_name: The extracted company name (e.g., "CenterSquare")
        original_prompt: The full user prompt with context (e.g., "Find leads at CenterSquare real estate investment")
    """
    logger.info(f"🔍 Searching for specific company: {company_name}")
    
    # Try to search Google for the company with industry/context disambiguation
    try:
        # Extract industry/business context keywords from original prompt to help disambiguate
        context_keywords = []
        exclusion_keywords = []
        
        if original_prompt:
            prompt_lower = original_prompt.lower()
            
            # Investment/finance related keywords (HIGH PRIORITY for disambiguation)
            if any(word in prompt_lower for word in ['investment', 'investor', 'investing', 'capital', 'fund', 'private equity', 'reit', 'portfolio', 'lp', 'limited partner']):
                context_keywords.append('investment management')
                context_keywords.append('institutional investor')
                # Exclude data centers and news sites
                exclusion_keywords.extend(['-data center', '-datacenter', '-news', '-media'])
            
            # Real estate keywords
            if any(word in prompt_lower for word in ['real estate', 'property', 'realty', 'multifamily', 'residential', 'commercial', 'btr', 'build to rent']):
                context_keywords.append('real estate')
                # If combined with investment, be even more specific
                if any(word in prompt_lower for word in ['investment', 'investor', 'fund']):
                    context_keywords.append('REIT')
                    exclusion_keywords.extend(['-construction', '-developer', '-builder'])
            
            # Development keywords (but not if it's clearly an investor request)
            if 'development' in prompt_lower and not any(word in prompt_lower for word in ['investor', 'investing', 'lp', 'limited partner', 'fund']):
                context_keywords.append('development')
            
            # Technology keywords
            if any(word in prompt_lower for word in ['tech', 'technology', 'software', 'saas', 'ai', 'startup']):
                context_keywords.append('technology')
            
            logger.info(f"🎯 Extracted context keywords from prompt: {context_keywords}")
            if exclusion_keywords:
                logger.info(f"🚫 Adding exclusions to avoid wrong companies: {exclusion_keywords}")
        
        # Build search query with context for disambiguation
        if context_keywords:
            # Use context keywords to help Google find the right company
            # Place industry context BEFORE company name for better Google ranking
            context_str = ' '.join(context_keywords)
            exclusion_str = ' '.join(exclusion_keywords) if exclusion_keywords else ''
            search_query = f'{context_str} "{company_name}" official website {exclusion_str}'
            logger.info(f"🔎 Using enhanced contextual search: {search_query}")
        else:
            # Fallback to basic search
            search_query = f'"{company_name}" official website'
            logger.info(f"🔎 Using basic search: {search_query}")
        
        companies = await search_companies({"prompt": search_query}, 1)
        
        if companies and len(companies) > 0:
            company = companies[0]
            logger.info(f"✅ Found company: {company.get('name')} at {company.get('domain')}")
            return company
        else:
            logger.warning(f"⚠️ Could not find company via Google search")
            
            # Fallback: try to guess domain
            domain_guess = company_name.lower().replace(' ', '').replace('&', 'and') + '.com'
            logger.info(f"💡 Trying domain guess: {domain_guess}")
            
            return {
                "name": company_name,
                "domain": domain_guess,
                "website": f"https://{domain_guess}",
                "snippet": f"Company website for {company_name}"
            }
            
    except Exception as e:
        logger.error(f"❌ Error searching for company: {e}")
        return None


async def process_job_real_only(job_id: str, job_data: dict):
    """
    Process job with REAL data only - NO SIMULATION
    
    This completely replaces the old process_job_background() function
    """
    
    if not REAL_RESEARCH_AVAILABLE:
        job_storage[job_id].update({
            "status": "failed",
            "progress": 0,
            "message": "❌ Real research engine not available. System cannot function.",
            "error": "Required modules not loaded. Check server logs."
        })
        logger.error(f"Job {job_id}: Cannot process - real research not available!")
        return
    
    try:
        prompt = job_data.get("prompt", "")
        target_count = job_data.get("target_count", 10)
        
        logger.info(f"="*80)
        logger.info(f"Job {job_id}: START PROCESSING")
        logger.info(f"Job {job_id}: Prompt: {prompt}")
        logger.info(f"Job {job_id}: Target count: {target_count}")
        logger.info(f"="*80)
        
        # ALWAYS extract research guide and targeting criteria FIRST
        # This is important even for specific company requests to know what roles to target
        job_storage[job_id].update({
            "progress": 5,
            "message": "Analyzing research guide..."
        })
        
        # Extract research guide text from knowledge base
        knowledge_base_docs = job_data.get("knowledge_base_documents", [])
        knowledge_sections = {
            "research_guide": [],
            "outreach_playbook": [],
            "audience_profile": [],
            "other": [],
        }

        for doc in knowledge_base_docs:
            raw_text = (doc.get("extractedText") or doc.get("content") or "").strip()
            if not raw_text:
                continue

            category = doc.get("category") or _infer_category(doc.get("name", ""), raw_text)
            if category not in knowledge_sections:
                category = "other"

            knowledge_sections[category].append(raw_text)
            doc["category"] = category  # Persist inferred category for downstream usage

        # Store flattened summary for downstream consumers (outreach generation, QA, exports)
        knowledge_base_summary = {
            key: "\n\n".join(value)
            for key, value in knowledge_sections.items()
            if value
        }
        combined_knowledge_text = "\n\n".join(knowledge_base_summary.values())

        job_data["knowledge_base_summary"] = knowledge_base_summary

        research_guide_text = (
            knowledge_base_summary.get("research_guide")
            or knowledge_base_summary.get("audience_profile")
            or combined_knowledge_text
        )

        # Extract targeting criteria from research guide + prompt
        prompt_with_guide = f"{prompt}\n\nResearch Guide:\n{research_guide_text}" if research_guide_text else prompt
        targeting_criteria = await extract_targeting_criteria(prompt_with_guide)
        
        # Store targeting criteria for later use when finding contacts
        job_data['targeting_criteria'] = targeting_criteria
        
        logger.info(f"Job {job_id}: 📋 Extracted targeting criteria:")
        logger.info(f"  Industry: {targeting_criteria.get('industry', 'N/A')}")
        logger.info(f"  Target Roles: {targeting_criteria.get('target_roles', [])}")
        logger.info(f"  Target Department: {targeting_criteria.get('target_department', 'executive')}")
        
        # Check if user is asking for a specific company
        specific_company_name = extract_company_name_from_prompt(prompt)
        
        if specific_company_name:
            # USER ASKED FOR SPECIFIC COMPANY (but still use research guide for role targeting)
            logger.info(f"Job {job_id}: 🎯 SPECIFIC COMPANY REQUEST: {specific_company_name}")
            logger.info(f"Job {job_id}: 📚 Will use research guide to target correct roles at this company")
            
            job_storage[job_id].update({
                "progress": 20,
                "message": f"Searching for {specific_company_name}..."
            })
            
            # Find the specific company (pass original prompt for context)
            company = await find_specific_company(specific_company_name, prompt)
            
            if not company:
                job_storage[job_id].update({
                    "status": "failed",
                    "message": f"❌ Could not find company: {specific_company_name}",
                    "error": "Company not found"
                })
                logger.error(f"Job {job_id}: Company not found")
                return
            
            companies = [company]
            
        else:
            # GENERAL SEARCH USING RESEARCH GUIDE
            logger.info(f"Job {job_id}: 📋 GENERAL SEARCH using research guide")
            
            job_storage[job_id].update({
                "progress": 20,
                "message": "Searching for companies..."
            })
            
            # Search for companies using targeting criteria
            companies = await search_companies(targeting_criteria, target_count)
            
            if not companies or len(companies) == 0:
                job_storage[job_id].update({
                    "status": "failed",
                    "message": "❌ No companies found matching your criteria",
                    "error": "No search results. Try different keywords or check API keys."
                })
                logger.error(f"Job {job_id}: No companies found")
                return
        
        logger.info(f"Job {job_id}: ✅ Found {len(companies)} companies")
        
        # Find contacts at each company
        job_storage[job_id].update({
            "progress": 50,
            "message": f"Finding contacts at {len(companies)} companies..."
        })
        
        all_leads = []
        
        for i, company in enumerate(companies):
            company_name = company.get('name', 'Unknown')
            domain = company.get('domain', '')
            
            logger.info(f"Job {job_id}: [{i+1}/{len(companies)}] Finding contacts at {company_name} ({domain})")
            
            job_storage[job_id].update({
                "progress": 50 + int((i / len(companies)) * 40),
                "message": f"Finding contacts at {company_name}... ({i+1}/{len(companies)})"
            })
            
            try:
                # Get targeting criteria if available
                targeting_criteria = job_data.get('targeting_criteria', {})
                
                # Find contacts
                contacts = await find_company_contacts(company, targeting_criteria)
                
                if contacts:
                    logger.info(f"Job {job_id}: ✅ Found {len(contacts)} contacts at {company_name}")
                    knowledge_summary = job_data.get("knowledge_base_summary", {})
                    for contact in contacts:
                        if knowledge_summary.get("research_guide"):
                            contact.setdefault(
                                "research_guide", knowledge_summary["research_guide"]
                            )
                        if knowledge_summary.get("outreach_playbook"):
                            contact.setdefault(
                                "outreach_instructions",
                                knowledge_summary["outreach_playbook"],
                            )
                        if knowledge_summary.get("audience_profile"):
                            contact.setdefault(
                                "audience_profile",
                                knowledge_summary["audience_profile"],
                            )
                        if combined_knowledge_text:
                            contact.setdefault(
                                "knowledge_base_context", combined_knowledge_text
                            )

                    all_leads.extend(contacts)
                else:
                    logger.error(f"Job {job_id}: ❌ FAILED to find contacts at {company_name} ({domain})")
                    logger.error(f"  Possible reasons:")
                    logger.error(f"    - Website has no /team or /leadership page")
                    logger.error(f"    - Team page uses non-standard HTML structure")
                    logger.error(f"    - Website blocks web scraping")
                    logger.error(f"    - Website requires JavaScript to load team info")
                    
            except Exception as e:
                logger.error(f"Job {job_id}: ❌ EXCEPTION finding contacts at {company_name}: {type(e).__name__}: {e}")
                import traceback
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                continue
        
        # Final result
        if len(all_leads) == 0:
            # Build detailed error message explaining WHY no contacts found
            error_details = []
            error_details.append(f"Searched {len(companies)} companies but found 0 contacts.")
            error_details.append("\nPossible reasons:")
            error_details.append("1. Companies don't have public team/leadership pages")
            error_details.append("2. Team pages use non-standard HTML (JavaScript-heavy sites)")
            error_details.append("3. Websites block web scraping")
            error_details.append("4. Wrong companies found by Google search (articles/blogs)")
            error_details.append("\nCompanies searched:")
            for i, company in enumerate(companies[:10], 1):  # Show first 10
                error_details.append(f"  {i}. {company.get('name')} ({company.get('domain')})")
            if len(companies) > 10:
                error_details.append(f"  ... and {len(companies) - 10} more")
            
            detailed_message = "\n".join(error_details)
            
            job_storage[job_id].update({
                "status": "failed",
                "progress": 100,
                "message": f"❌ No contacts found at {len(companies)} companies",
                "error": detailed_message,
                "leads": [],
                "companies_searched": len(companies)
            })
            logger.error(f"Job {job_id}: FAILED - No contacts found")
            logger.error(detailed_message)
        else:
            job_storage[job_id].update({
                "status": "completed",
                "progress": 100,
                "message": f"✅ Found {len(all_leads)} real contacts with verified emails!",
                "leads": all_leads,
                "companies_searched": len(companies)
            })
            logger.info(f"Job {job_id}: ✅ COMPLETED with {len(all_leads)} leads")
        
    except Exception as e:
        logger.error(f"Job {job_id}: ❌ CRITICAL ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        job_storage[job_id].update({
            "status": "failed",
            "message": f"❌ Job failed: {str(e)}",
            "error": str(e)
        })


# API Endpoints


@app.post("/knowledge-base/extract", response_model=KnowledgeBaseExtractResponse)
async def extract_knowledge_base_document(payload: KnowledgeBaseExtractRequest):
    """Extract raw text and metadata from an uploaded knowledge base document."""

    if not payload.data:
        raise HTTPException(status_code=400, detail="No document data provided")

    file_bytes = _decode_base64(payload.data)
    text, summary, category = _extract_text_from_document(payload.name, payload.type, file_bytes)

    if not text.strip():
        raise HTTPException(status_code=400, detail="Document contained no extractable text")

    return KnowledgeBaseExtractResponse(
        text=text.strip(),
        summary=summary,
        category=category,
        word_count=len(text.split()),
    )

@app.get("/")
async def root():
    """Serve frontend"""
    return FileResponse("frontend/dist/index.html")

@app.post("/jobs/")
async def create_job(job_data: dict):
    """Create a new job"""
    try:
        job_id = str(uuid.uuid4())
        logger.info(f"Creating job {job_id}")
        
        job_storage[job_id] = {
            "id": job_id,
            "status": "started",
            "progress": 0,
            "message": "Job started - Real research in progress",
            "created_at": datetime.utcnow().isoformat(),
            "prompt": job_data.get("prompt", ""),
            "target_count": job_data.get("target_count", 10)
        }
        
        # Start background processing
        asyncio.create_task(process_job_real_only(job_id, job_data))
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Job started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status"""
    if job_id in job_storage:
        return job_storage[job_id]
    else:
        raise HTTPException(status_code=404, detail="Job not found")

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "real_research_available": REAL_RESEARCH_AVAILABLE,
        "container_start_time": container_start_time,
        "active_jobs": len(job_storage)
    }

@app.get("/health-check")
async def health_check():
    """Health check for Railway"""
    return {
        "status": "healthy",
        "real_research_available": REAL_RESEARCH_AVAILABLE,
        "container_start_time": container_start_time,
        "active_jobs": len(job_storage)
    }

# Serve static files
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
