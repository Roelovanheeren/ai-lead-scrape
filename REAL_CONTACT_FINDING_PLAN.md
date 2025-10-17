# Real Contact Finding Implementation Plan

## Current Problem

**User Report**: 
- "it also doesnt seem to find linkedin profiles at all"
- "its also way to quick, to find, research, and create message for these leads could easily take up to 5 minutes or more and thats fine"

**Root Cause**: The `find_company_contacts()` function generates MOCK contacts instead of finding real ones.

**Current Behavior**:
```python
# This just makes up contacts!
contact = {
    "contact_name": "CEO CompanyName",  # Fake
    "email": "ceo@company.com",  # Fake
    "linkedin": "linkedin.com/in/ceo-company-name",  # Fake
    "phone": "+1-555-1000"  # Fake
}
```

---

## Why It's Too Fast

### Current Flow (60 seconds)
1. Google Custom Search API: **10 seconds** ✅ (REAL)
2. Company research: **10 seconds** ⚠️ (Mock data)
3. Find contacts: **5 seconds** ❌ (Completely fake)
4. Generate outreach: **10 seconds** ✅ (Real AI, but uses fake contact data)

**Total**: ~30-60 seconds with mostly fake data

### Desired Flow (5+ minutes)
1. Google Custom Search API: **20 seconds** ✅
2. Scrape company websites: **30-60 seconds** (per company)
3. Search LinkedIn for employees: **30-60 seconds** (per company)
4. Find email addresses: **20-40 seconds** (per contact)
5. Verify emails: **10-20 seconds** (per contact)
6. Deep research each contact: **30-60 seconds** (per contact)
7. Generate personalized outreach: **20-30 seconds** (per contact)

**Total**: 5-10 minutes for 10 leads (REAL, thorough research)

---

## Solution Options

### Option 1: Apollo.io API (Recommended)
**Best for**: Finding business contacts with verified emails and LinkedIn profiles

**Features**:
- ✅ 200M+ contact database
- ✅ Real LinkedIn profiles
- ✅ Verified email addresses
- ✅ Phone numbers
- ✅ Job titles and seniority
- ✅ Company information
- ✅ Intent data

**API Endpoints**:
```python
# Search for people at a company
POST /v1/people/search
{
    "organization_ids": ["company_id"],
    "person_titles": ["CEO", "CTO", "VP"],
    "contact_email_status": ["verified"]
}

# Get person details
GET /v1/people/{person_id}
```

**Pricing**:
- Free tier: 50 credits/month
- Paid: $49/month (10,000 contacts)

**Setup**:
1. Sign up at apollo.io
2. Get API key
3. Add to Railway env: `APOLLO_API_KEY`

---

### Option 2: Hunter.io API
**Best for**: Finding and verifying email addresses

**Features**:
- ✅ Domain search (find all emails at company)
- ✅ Email verification
- ✅ Email pattern detection
- ✅ Confidence scores

**API Endpoints**:
```python
# Find emails at domain
GET /v2/domain-search?domain=company.com&department=executive

# Verify email
GET /v2/email-verifier?email=ceo@company.com

# Find email for person
GET /v2/email-finder?domain=company.com&first_name=John&last_name=Doe
```

**Pricing**:
- Free tier: 25 searches/month
- Paid: $49/month (500 searches)

**Setup**:
1. Sign up at hunter.io
2. Get API key
3. Add to Railway env: `HUNTER_API_KEY`

---

### Option 3: RocketReach API
**Best for**: LinkedIn profiles and direct contact info

**Features**:
- ✅ LinkedIn profile URLs
- ✅ Real-time contact data
- ✅ Social media profiles
- ✅ Phone numbers
- ✅ Email verification

**API Endpoints**:
```python
# Search for people
POST /v2/api/search
{
    "query": {
        "current_employer": ["Company Name"],
        "current_title": ["CEO", "CTO"]
    }
}

# Get person details
GET /v2/api/lookupProfile?id={profile_id}
```

**Pricing**:
- Free tier: 5 lookups/month (very limited)
- Paid: $39/month (170 lookups)

---

### Option 4: LinkedIn Sales Navigator API (Enterprise)
**Best for**: Official LinkedIn data

**Features**:
- ✅ Real LinkedIn profiles
- ✅ InMail access
- ✅ Lead recommendations
- ✅ Company insights

**Limitations**:
- ❌ Expensive ($99+/month per seat)
- ❌ Requires Sales Navigator subscription
- ❌ Complex authentication
- ❌ Rate limits

---

### Option 5: Scraping + AI (Budget Option)
**Best for**: Low budget, willing to do more work

**Approach**:
1. Search LinkedIn with Google: `site:linkedin.com/in "Company Name" "CEO"`
2. Scrape LinkedIn profiles (carefully, respect robots.txt)
3. Use AI to extract contact info from company websites
4. Use email pattern guessing + verification
5. Cross-reference multiple sources

**Limitations**:
- ⚠️ Slower (2-3x longer)
- ⚠️ Less accurate (60-70% vs 90%+)
- ⚠️ Risk of rate limiting / IP blocking
- ⚠️ May violate LinkedIn ToS

---

## Recommended Implementation

### Phase 1: Apollo.io Integration (Primary)
**Why**: Best balance of quality, price, and ease of use

**Implementation**:
```python
# backend/services/apollo_client.py

import aiohttp
import os
import logging

logger = logging.getLogger(__name__)

class ApolloClient:
    def __init__(self):
        self.api_key = os.getenv("APOLLO_API_KEY")
        self.base_url = "https://api.apollo.io/v1"
    
    async def find_contacts_by_company(
        self, 
        company_name: str, 
        titles: List[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find contacts at a specific company"""
        
        if not self.api_key:
            logger.error("❌ APOLLO_API_KEY not set")
            return []
        
        # First, find the organization
        org_id = await self._find_organization(company_name)
        if not org_id:
            return []
        
        # Search for people at this organization
        url = f"{self.base_url}/people/search"
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": self.api_key
        }
        
        payload = {
            "organization_ids": [org_id],
            "person_titles": titles or ["CEO", "CTO", "VP", "Head", "Director"],
            "contact_email_status": ["verified", "guessed"],
            "page": 1,
            "per_page": limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_apollo_contacts(data)
                else:
                    logger.error(f"Apollo API error: {response.status}")
                    return []
    
    async def _find_organization(self, company_name: str) -> Optional[str]:
        """Find organization ID by name"""
        url = f"{self.base_url}/organizations/search"
        headers = {"X-Api-Key": self.api_key}
        
        payload = {
            "q_organization_name": company_name,
            "per_page": 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    orgs = data.get("organizations", [])
                    if orgs:
                        return orgs[0].get("id")
        return None
    
    def _parse_apollo_contacts(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse Apollo API response into our contact format"""
        contacts = []
        
        for person in data.get("people", []):
            contact = {
                "id": person.get("id"),
                "contact_name": person.get("name"),
                "email": person.get("email"),
                "linkedin": person.get("linkedin_url"),
                "phone": person.get("phone_numbers", [{}])[0].get("sanitized_number"),
                "company": person.get("organization", {}).get("name"),
                "role": person.get("title"),
                "seniority": person.get("seniority"),
                "location": person.get("city"),
                "confidence": 0.95,  # Apollo verified
                "source": "Apollo.io",
                "created_at": datetime.utcnow().isoformat()
            }
            contacts.append(contact)
        
        return contacts
```

### Phase 2: Hunter.io Fallback (Email Verification)
**Use case**: When Apollo doesn't have contact, or to verify emails

```python
# backend/services/hunter_client.py

class HunterClient:
    async def find_emails_at_domain(self, domain: str) -> List[str]:
        """Find all emails at a domain"""
        url = "https://api.hunter.io/v2/domain-search"
        params = {
            "domain": domain,
            "api_key": os.getenv("HUNTER_API_KEY"),
            "department": "executive"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {}).get("emails", [])
        return []
    
    async def verify_email(self, email: str) -> Dict[str, Any]:
        """Verify if an email is valid"""
        url = "https://api.hunter.io/v2/email-verifier"
        params = {
            "email": email,
            "api_key": os.getenv("HUNTER_API_KEY")
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "valid": data.get("data", {}).get("result") == "deliverable",
                        "score": data.get("data", {}).get("score"),
                        "status": data.get("data", {}).get("result")
                    }
        return {"valid": False}
```

### Phase 3: Update real_research.py

```python
# backend/services/real_research.py

# Add at top
from services.apollo_client import ApolloClient
from services.hunter_client import HunterClient

class RealResearchEngine:
    def __init__(self):
        # ... existing code ...
        self.apollo_client = ApolloClient()
        self.hunter_client = HunterClient()
    
    async def find_company_contacts(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find REAL contacts using Apollo.io"""
        company_name = company.get("name", "")
        domain = company.get("domain", "")
        
        logger.info(f"🔍 Finding REAL contacts for {company_name} using Apollo.io...")
        
        # Try Apollo first (best quality)
        contacts = await self.apollo_client.find_contacts_by_company(
            company_name=company_name,
            titles=["CEO", "CTO", "VP", "Head of", "Director"],
            limit=5
        )
        
        if contacts:
            logger.info(f"✅ Found {len(contacts)} contacts via Apollo.io")
            
            # Verify emails with Hunter if available
            for contact in contacts:
                if contact.get("email") and os.getenv("HUNTER_API_KEY"):
                    verification = await self.hunter_client.verify_email(contact["email"])
                    contact["email_verified"] = verification.get("valid", False)
                    contact["email_score"] = verification.get("score", 0)
            
            return contacts
        
        # Fallback: Try Hunter.io domain search
        if domain and os.getenv("HUNTER_API_KEY"):
            logger.info(f"⚠️ Apollo returned no results, trying Hunter.io for {domain}...")
            emails = await self.hunter_client.find_emails_at_domain(domain)
            
            # Convert Hunter results to contacts
            contacts = []
            for email_data in emails[:5]:
                contact = {
                    "contact_name": f"{email_data.get('first_name', '')} {email_data.get('last_name', '')}".strip(),
                    "email": email_data.get("value"),
                    "linkedin": email_data.get("linkedin"),
                    "company": company_name,
                    "role": email_data.get("position"),
                    "confidence": email_data.get("confidence", 0) / 100,
                    "source": "Hunter.io"
                }
                contacts.append(contact)
            
            if contacts:
                logger.info(f"✅ Found {len(contacts)} contacts via Hunter.io")
                return contacts
        
        # Last resort: AI-powered web scraping
        logger.warning(f"⚠️ No API contacts found, using AI web scraping...")
        return await self._find_contacts_via_scraping(company)
```

---

## Environment Variables Needed

Add these to Railway:

```bash
# Apollo.io (Primary contact finding)
APOLLO_API_KEY=your_apollo_api_key_here

# Hunter.io (Email verification, fallback)
HUNTER_API_KEY=your_hunter_api_key_here

# Optional: RocketReach (Additional source)
ROCKETREACH_API_KEY=your_rocketreach_key_here
```

---

## Timeline & Costs

### Free Tier (Limited)
- Apollo: 50 contacts/month
- Hunter: 25 searches/month
- **Total cost**: $0
- **Limitation**: ~75 contacts/month max

### Paid Tier (Recommended)
- Apollo: $49/month (10,000 contacts)
- Hunter: $49/month (500 searches)
- **Total cost**: $98/month
- **Capability**: ~500-1000 quality leads/month

### Implementation Time
- Apollo integration: **2 hours**
- Hunter integration: **1 hour**
- Testing: **1 hour**
- **Total**: ~4 hours

---

## Next Steps

### Immediate (To Fix Current Issue)

1. **Sign up for Apollo.io**
   - Go to https://www.apollo.io
   - Create free account
   - Get API key from Settings → API

2. **Sign up for Hunter.io** (Optional but recommended)
   - Go to https://hunter.io
   - Create free account
   - Get API key from Settings → API

3. **Add API keys to Railway**
   - Railway Dashboard → Variables
   - Add `APOLLO_API_KEY`
   - Add `HUNTER_API_KEY`

4. **I'll implement the integration** (~2 hours coding)

---

## Alternative: LinkedIn Scraping (Free but Risky)

If you don't want to pay for APIs, we can implement LinkedIn scraping:

**Pros**:
- ✅ Free
- ✅ Direct access to LinkedIn data

**Cons**:
- ❌ Violates LinkedIn Terms of Service
- ❌ High risk of IP banning
- ❌ Requires proxies ($)
- ❌ Slower and less reliable
- ❌ May get account banned

**Not recommended** unless budget is absolutely $0.

---

## Decision Time

**What do you want to do?**

### Option A: Apollo.io + Hunter.io (Recommended)
- **Cost**: $0-98/month depending on volume
- **Quality**: 90%+ accuracy
- **Speed**: 5-10 minutes per job (proper research)
- **Risk**: None (official APIs)
- **I need**: Your API keys

### Option B: Free LinkedIn Scraping (Risky)
- **Cost**: $0
- **Quality**: 60-70% accuracy
- **Speed**: 10-15 minutes per job (slower)
- **Risk**: High (may get banned)
- **I need**: Your permission to implement gray-area scraping

### Option C: Hybrid (Best Value)
- Use free tiers of Apollo + Hunter
- Implement smart scraping as fallback
- **Cost**: $0 initially, scale to paid later
- **Quality**: 70-80% initially, 90%+ with paid
- **I need**: 2 hours to implement

---

## My Recommendation

**Start with Option C (Hybrid)**:

1. Sign up for free Apollo.io account (50 contacts/month)
2. Sign up for free Hunter.io account (25 searches/month)
3. I'll implement both APIs + smart fallback
4. Test with free tier (75 quality contacts/month)
5. Upgrade to paid ($98/month) when you need scale

This gives you:
- ✅ Immediate improvement (real contacts!)
- ✅ No upfront cost
- ✅ Easy to scale later
- ✅ 5-10 minute deep research per job
- ✅ Real LinkedIn profiles
- ✅ Verified emails

**Ready to proceed?** Just give me the API keys and I'll implement it!
