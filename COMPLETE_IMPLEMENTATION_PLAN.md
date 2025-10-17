# Complete Implementation Plan - Knowledge Base Integration

## Current Status ✅

**What works:**
- Frontend uploads PDFs (research guide, outreach guide) to localStorage
- Frontend connects to Google Sheets and maps columns to localStorage  
- Frontend reads existing leads from sheet
- Frontend sends to backend:
  - `connected_sheet_id` ✅
  - `header_mapping` ✅
  - `existing_leads` ✅

**What's MISSING:**
- Backend cannot access localStorage (browser-only)
- Uploaded PDFs not sent to backend ❌
- Backend doesn't read connected sheet data ❌
- Backend doesn't use header mapping ❌
- Backend doesn't exclude existing leads properly ❌

---

## What User Wants

### The Flow:
1. User uploads "Research Guide.pdf" and "Outreach Guide.pdf" to knowledge base
2. User connects Google Sheet with existing leads
3. User maps sheet columns (Company Name, Email, Phone, etc.)
4. User creates job with prompt: "Generate leads as explained in the research guide"
5. Backend should:
   - **Read uploaded PDFs** (research + outreach guides)
   - **Read existing leads** from connected sheet
   - **Exclude those companies** from search
   - **Follow research guide** to know what to search for
   - **Search Google** based on guide instructions
   - **Research each company** deeply
   - **Follow outreach guide** to write messages
   - **Continue until X qualified leads** found
   - **Write new leads** back to sheet in correct format (using header mapping)

---

## Implementation Required

### Phase 1: Send Knowledge Base to Backend

**Frontend Changes** (`JobWizard.tsx`):

```typescript
// When creating job, include uploaded documents
const uploadedDocs = await storageService.getUploadedDocuments()

const jobData: JobCreate = {
  prompt: formData.prompt,
  target_count: formData.targetCount,
  quality_threshold: formData.qualityThreshold,
  
  // Already sent ✅
  connected_sheet_id: activeConnectedSheet?.id,
  header_mapping: headerMapping?.mapping,
  existing_leads: existingLeads,
  exclude_existing_leads: existingLeads.length > 0,
  
  // NEW: Send uploaded documents
  knowledge_base: {
    research_guide: uploadedDocs.find(d => d.name.toLowerCase().includes('research'))?.content || null,
    outreach_guide: uploadedDocs.find(d => d.name.toLowerCase().includes('outreach'))?.content || null,
    all_documents: uploadedDocs.map(d => ({
      name: d.name,
      type: d.type,
      content: d.content,
      extracted_text: d.extractedText,
      summary: d.summary
    }))
  }
}
```

---

### Phase 2: Backend Reads Everything

**Backend Changes** (`main_simple.py`):

```python
async def process_job_background(job_id: str, job_data: dict):
    # Step 1: Extract all the data frontend sent
    prompt = job_data.get("prompt", "")
    target_count = job_data.get("target_count", 10)
    connected_sheet_id = job_data.get("connected_sheet_id")
    header_mapping = job_data.get("header_mapping", {})
    existing_leads = job_data.get("existing_leads", [])
    exclude_existing = job_data.get("exclude_existing_leads", False)
    knowledge_base = job_data.get("knowledge_base", {})
    
    # Step 2: Get guides from knowledge base
    research_guide = knowledge_base.get("research_guide")
    outreach_guide = knowledge_base.get("outreach_guide")
    
    logger.info(f"📚 Research guide available: {bool(research_guide)}")
    logger.info(f"📝 Outreach guide available: {bool(outreach_guide)}")
    logger.info(f"📊 Connected sheet: {connected_sheet_id}")
    logger.info(f"🗺️ Header mapping: {header_mapping}")
    logger.info(f"🚫 Existing leads to exclude: {len(existing_leads)}")
    
    # Step 3: Read existing leads from connected sheet (if not already sent)
    if connected_sheet_id and not existing_leads:
        logger.info(f"📖 Reading existing leads from sheet...")
        from services.google_sheets_service import google_sheets_service
        sheet_data = await google_sheets_service.read_sheet_data(
            connected_sheet_id,
            range_name="A:Z"
        )
        if sheet_data.get("success"):
            existing_leads = sheet_data.get("data", [])
            logger.info(f"✅ Loaded {len(existing_leads)} existing leads from sheet")
    
    # Step 4: Extract companies/emails to exclude
    existing_companies = set()
    existing_emails = set()
    
    if exclude_existing and existing_leads:
        # Use header mapping to find company/email columns
        company_col = None
        email_col = None
        
        if header_mapping:
            # Find which column maps to 'company' and 'email'
            for col_name, field_name in header_mapping.items():
                if 'company' in field_name.lower():
                    company_col = col_name
                if 'email' in field_name.lower():
                    email_col = col_name
        
        # Extract from existing leads
        headers = existing_leads[0] if existing_leads else []
        for row in existing_leads[1:]:  # Skip header row
            if company_col and company_col in headers:
                idx = headers.index(company_col)
                if idx < len(row):
                    existing_companies.add(row[idx].lower())
            
            if email_col and email_col in headers:
                idx = headers.index(email_col)
                if idx < len(row) and '@' in row[idx]:
                    existing_emails.add(row[idx].lower())
        
        logger.info(f"🚫 Will exclude {len(existing_companies)} companies and {len(existing_emails)} emails")
    
    # Step 5: Use AI to understand research guide
    if research_guide:
        # Use OpenAI/Claude to extract search strategy from guide
        search_instructions = await analyze_research_guide_with_ai(
            prompt=prompt,
            research_guide=research_guide
        )
        logger.info(f"🎯 AI extracted search strategy: {search_instructions}")
    else:
        # Fallback to prompt-based extraction
        search_instructions = await extract_targeting_criteria(prompt)
    
    # Step 6: Search for companies
    logger.info(f"🔍 Starting company search...")
    companies = await search_companies(search_instructions, target_count * 3)  # Get 3x for filtering
    
    # Step 7: Filter out existing companies
    new_companies = []
    for company in companies:
        company_name = company.get("name", "").lower()
        company_domain = company.get("domain", "").lower()
        
        # Check if already exists
        if company_name in existing_companies or company_domain in existing_companies:
            logger.info(f"⏭️ Skipping existing company: {company.get('name')}")
            continue
        
        new_companies.append(company)
        
        # Stop when we have enough NEW companies
        if len(new_companies) >= target_count:
            break
    
    logger.info(f"✅ Found {len(new_companies)} NEW companies (excluded {len(companies) - len(new_companies)} existing)")
    
    # Step 8: Research each company deeply
    researched_companies = []
    for i, company in enumerate(new_companies):
        logger.info(f"🔬 Researching company {i+1}/{len(new_companies)}: {company.get('name')}")
        
        # Use research guide to know WHAT to research
        if research_guide:
            research_data = await research_company_with_guide(company, research_guide)
        else:
            research_data = await research_company_deep(company)
        
        researched_companies.append(research_data)
    
    # Step 9: Find contacts for each company
    leads = []
    for company in researched_companies:
        contacts = await find_company_contacts(company)
        
        # Filter out existing emails
        for contact in contacts:
            email = contact.get("email", "").lower()
            if email not in existing_emails:
                leads.append(contact)
    
    logger.info(f"✅ Found {len(leads)} NEW contacts (excluded existing emails)")
    
    # Step 10: Generate outreach using outreach guide
    final_leads = []
    for lead in leads:
        logger.info(f"✍️ Generating outreach for {lead.get('contact_name')}")
        
        # Use outreach guide for message generation
        if outreach_guide:
            outreach = await generate_outreach_with_guide(lead, outreach_guide)
        else:
            outreach = await generate_personalized_outreach(lead)
        
        lead.update(outreach)
        final_leads.append(lead)
    
    # Step 11: Write to Google Sheet using header mapping
    if connected_sheet_id and header_mapping:
        logger.info(f"📝 Writing {len(final_leads)} leads to Google Sheet...")
        
        # Format leads according to header mapping
        formatted_rows = []
        for lead in final_leads:
            row = format_lead_for_sheet(lead, header_mapping)
            formatted_rows.append(row)
        
        # Append to sheet
        from services.google_sheets_service import google_sheets_service
        for row in formatted_rows:
            await google_sheets_service.write_lead_data(
                connected_sheet_id,
                row,
                sheet_name="Sheet1"  # Or get from sheet info
            )
        
        logger.info(f"✅ Written {len(formatted_rows)} leads to sheet")
    
    # Step 12: Mark job complete
    job_storage[job_id] = {
        "id": job_id,
        "status": "completed",
        "progress": 100,
        "message": f"Completed! Found {len(final_leads)} qualified leads",
        "leads": final_leads,
        "completed_at": datetime.utcnow().isoformat()
    }
```

---

### Phase 3: AI Functions for Guides

**New Functions Needed**:

```python
# backend/services/real_research.py

async def analyze_research_guide_with_ai(prompt: str, research_guide: str) -> Dict[str, Any]:
    """Use AI to extract search strategy from research guide"""
    
    if not openai_client:
        return await extract_targeting_criteria(prompt)
    
    analysis_prompt = f"""
    User wants: {prompt}
    
    Research Guide Content:
    {research_guide[:5000]}  # First 5000 chars
    
    Based on the research guide, extract:
    1. What types of companies to search for
    2. What keywords to use in searches
    3. What locations/industries to focus on
    4. What to research about each company
    5. What data points are most important
    
    Return as JSON:
    {{
        "search_queries": ["query 1", "query 2", ...],
        "keywords": ["keyword1", "keyword2", ...],
        "industries": ["industry1", ...],
        "locations": ["location1", ...],
        "research_focus": ["data point 1", "data point 2", ...],
        "exclusions": ["thing to avoid 1", ...]
    }}
    """
    
    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": analysis_prompt}],
        temperature=0.3
    )
    
    return json.loads(response.choices[0].message.content)


async def research_company_with_guide(company: Dict, research_guide: str) -> Dict:
    """Research company following specific guide instructions"""
    
    # Extract what to research from guide
    research_instructions = await extract_research_instructions(research_guide)
    
    # Do targeted research based on instructions
    research_data = {}
    
    for instruction in research_instructions:
        if "funding" in instruction.lower():
            research_data["funding"] = await get_funding_info(company)
        if "technology" in instruction.lower():
            research_data["tech_stack"] = await analyze_tech_stack(company)
        if "social" in instruction.lower():
            research_data["social"] = await get_social_signals(company)
        # ... etc
    
    company["research_data"] = research_data
    return company


async def generate_outreach_with_guide(lead: Dict, outreach_guide: str) -> Dict:
    """Generate outreach messages following specific guide"""
    
    if not openai_client:
        return await generate_personalized_outreach(lead)
    
    outreach_prompt = f"""
    Create personalized outreach for:
    
    Contact: {lead.get('contact_name')} ({lead.get('role')})
    Company: {lead.get('company')}
    Research Data: {json.dumps(lead.get('research_data', {}), indent=2)}
    
    Outreach Guide:
    {outreach_guide[:3000]}
    
    Follow the guide's style, tone, and structure exactly.
    Generate:
    1. LinkedIn message (300 chars max)
    2. Email subject (50 chars max)
    3. Email body (200 words max)
    
    Return as JSON.
    """
    
    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": outreach_prompt}],
        temperature=0.7
    )
    
    return json.loads(response.choices[0].message.content)


def format_lead_for_sheet(lead: Dict, header_mapping: Dict) -> Dict:
    """Format lead data according to sheet header mapping"""
    
    formatted = {}
    
    # Map each field to the correct column
    for column_name, field_name in header_mapping.items():
        # Try to find the field in lead data
        value = lead.get(field_name, "")
        
        # Handle nested fields (e.g., "research_data.funding")
        if "." in field_name:
            parts = field_name.split(".")
            value = lead
            for part in parts:
                value = value.get(part, "") if isinstance(value, dict) else ""
        
        formatted[column_name] = value
    
    return formatted
```

---

## Summary

**What needs to be done:**

1. ✅ Frontend already sends: `connected_sheet_id`, `header_mapping`, `existing_leads`
2. ❌ Frontend needs to send: `knowledge_base` with uploaded PDFs
3. ❌ Backend needs to:
   - Read uploaded documents from job data
   - Use AI to analyze research guide → generate smart searches
   - Read existing leads from sheet
   - Filter out existing companies/emails
   - Research following guide instructions
   - Generate outreach following guide
   - Write back to sheet using header mapping

**Time estimate:** 4-6 hours implementation

**Should I implement this now?**

Let me know and I'll start coding!
