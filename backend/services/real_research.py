"""
Real Research and Web Scraping Implementation
Replaces simulation with actual Google Custom Search, company research, and outreach generation
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import re
from urllib.parse import urlparse, urljoin

# Import HTTP client
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logging.warning("aiohttp not available, using requests fallback")

# Import AI clients
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available")

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    logging.warning("Anthropic Claude not available")

logger = logging.getLogger(__name__)

class RealResearchEngine:
    """Real research engine that performs actual web scraping and company research"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        # Support both GOOGLE_CSE_ID and GOOGLE_SEARCH_ENGINE_ID for backwards compatibility
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID") or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.claude_key = os.getenv("CLAUDE_API_KEY")
        
        # Initialize AI clients
        if OPENAI_AVAILABLE and self.openai_key:
            self.openai_client = AsyncOpenAI(api_key=self.openai_key)
        else:
            self.openai_client = None
            
        if CLAUDE_AVAILABLE and self.claude_key:
            self.claude_client = anthropic.AsyncAnthropic(api_key=self.claude_key)
        else:
            self.claude_client = None
    
    async def extract_targeting_criteria(self, prompt: str) -> Dict[str, Any]:
        """Extract structured targeting criteria from user prompt using AI
        
        The prompt may include research guide documents that explain:
        - What types of companies to target
        - What industries to focus on
        - What criteria make a good lead
        - How to exclude certain companies
        """
        if not self.openai_client and not self.claude_client:
            logger.error("❌ NO AI CLIENT AVAILABLE (OpenAI/Claude API key not set)")
            logger.error("Using rule-based extraction fallback")
            logger.error("⚠️ Results will be lower quality without AI")
            logger.error("💡 Set OPENAI_API_KEY or CLAUDE_API_KEY environment variable for better results")
            
            # Smart fallback: detect investment vs development from keywords
            prompt_lower = prompt.lower()
            
            # Check if this is about INVESTORS (LP, fund, capital partners)
            is_investor_query = any(word in prompt_lower for word in [
                'investor', 'invest', 'lp', 'limited partner', 'fund', 'capital',
                'reit', 'private equity', 'institutional', 'portfolio'
            ])
            
            # Check if this is about DEVELOPERS (build, develop, construction)
            is_developer_query = any(word in prompt_lower for word in [
                'developer', 'development', 'builder', 'construction', 'contractor'
            ]) and not is_investor_query  # Don't match if also investor query
            
            if is_investor_query:
                logger.info("🎯 Detected INVESTOR query (fallback mode)")
                return {
                    "keywords": ["investor", "investment", "fund", "capital", "LP", "institutional"],
                    "industry": "Real Estate Investment Management",
                    "search_queries": [
                        "top real estate investment firms",
                        "institutional real estate investors",
                        "real estate private equity funds",
                        "REIT companies",
                        "multifamily investment firms USA"
                    ],
                    "target_roles": ["Investment Director", "Portfolio Manager", "Fund Manager"],
                    "target_department": "finance"
                }
            elif is_developer_query:
                logger.info("🎯 Detected DEVELOPER query (fallback mode)")
                return {
                    "keywords": ["developer", "development", "builder", "construction"],
                    "industry": "Real Estate Development",
                    "search_queries": [
                        "top real estate development firms",
                        "leading commercial real estate developers",
                        "multifamily developers USA",
                        "residential property developers"
                    ],
                    "target_roles": ["VP Development", "Development Director", "CEO"],
                    "target_department": "executive"
                }
            else:
                logger.warning("⚠️ Could not detect query type, using generic fallback")
                return {
                    "keywords": prompt.split()[:10],
                    "industry": "Technology",
                    "search_queries": [f"{' '.join(prompt.split()[:5])} companies"]
                }
        
        extraction_prompt = f"""
        You are analyzing a lead generation request. The user has provided a prompt that may include:
        1. A short instruction like "Generate leads as explained in the knowledge base"
        2. Attached research guide documents that explain targeting criteria
        
        Your task: Extract SPECIFIC, ACTIONABLE search criteria that can be used for Google searches.
        
        User Input:
        {prompt}
        
        Return a JSON object with these fields:
        {{
          "keywords": ["list", "of", "specific", "search", "terms"],
          "industry": "specific industry if mentioned",
          "location": "geographic focus if mentioned",
          "company_size": "size preference if mentioned",
          "funding_stage": "funding stage if mentioned",
          "technology": "tech stack if mentioned",
          "pain_points": ["specific", "pain", "points"],
          "search_queries": ["ready-to-use Google search query 1", "query 2", "query 3"],
          "target_roles": ["specific job titles/roles to target, e.g. CEO, VP of Development, etc."],
          "target_department": "department to focus on (executive, engineering, sales, marketing, etc.)"
        }}
        
        IMPORTANT:
        - Read the ENTIRE research guide document if provided
        - Pay CLOSE ATTENTION to whether the guide wants:
          * DEVELOPERS (companies that build their own projects) OR
          * INVESTORS/LPs (companies that invest in other people's projects)
        - Extract keywords that would work well in Google searches
        - If the guide mentions specific company types, industries, or criteria, include those
        - Generate 5-10 ready-to-use Google search queries based on the criteria
        - Be specific and actionable - these will be used directly for web searches
        - CRITICAL: Search queries should target COMPANY WEBSITES, not job boards or articles
        - Include company names, "top companies", "leading firms", "portfolio", "about us" to find real companies
        
        Examples:
        
        If guide says "target institutional investors that invest as LPs in real estate", include:
        - keywords: ["institutional investor", "limited partner", "LP investor", "real estate fund", "REIT", "private equity"]
        - industry: "Real Estate Investment Management"
        - search_queries: [
            "institutional real estate investors LP",
            "real estate private equity funds",
            "multifamily investment firms",
            "build-to-rent LP investors",
            "opportunity zone fund managers"
          ]
        
        If guide says "target SaaS companies with 50-200 employees", include:
        - keywords: ["SaaS", "software", "cloud", "subscription"]
        - search_queries: [
            "top SaaS companies 50-200 employees",
            "leading cloud software companies",
            "SaaS startup company websites",
            "enterprise SaaS vendors portfolio"
          ]
        
        If guide says "contact executives at real estate DEVELOPMENT companies" (not investors), include:
        - target_roles: ["CEO", "President", "Managing Director"]
        - target_department: "executive"
        - industry: "Real Estate Development"
        - search_queries: [
            "top real estate development firms",
            "leading commercial real estate developers",
            "residential property developers"
          ]
        
        BAD QUERIES (these find job boards/articles):
        - "real estate development companies 50-500 employees" (job listings)
        - "VP of Development jobs" (job boards)
        
        GOOD QUERIES (these find company websites):
        - "top real estate development firms USA"
        - "leading commercial developers portfolio"
        - "major real estate investment companies"
        
        CRITICAL DISTINCTION - Investors vs Developers:
        If the guide mentions "LP investors", "institutional investors", "fund managers", "capital partners":
        - Industry should be: "Real Estate Investment Management" or "Institutional Real Estate Investment"
        - Keywords should include: "LP", "limited partner", "investor", "fund", "REIT", "private equity"
        - Search for: investment firms, fund managers, REITs, private equity firms
        - Target roles: "Investment Director", "Portfolio Manager", "Fund Manager", "Investment Committee"
        
        If the guide mentions "developers", "development companies", "builders":
        - Industry should be: "Real Estate Development"
        - Keywords should include: "developer", "development", "builder", "construction"
        - Search for: development companies, construction firms, home builders
        - Target roles: "VP of Development", "Project Manager", "Development Director"
        """
        
        try:
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
            elif self.claude_client:
                response = await self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": extraction_prompt}]
                )
                result = json.loads(response.content[0].text)
            
            logger.info(f"✅ Extracted targeting criteria from research guide:")
            logger.info(f"   Keywords: {result.get('keywords', [])}")
            logger.info(f"   Industry: {result.get('industry', 'N/A')}")
            logger.info(f"   Generated search queries: {len(result.get('search_queries', []))}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting targeting criteria: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {"keywords": prompt.split()[:10], "industry": "Technology", "search_queries": []}
    
    async def search_companies(self, criteria: Dict[str, Any], target_count: int) -> List[Dict[str, Any]]:
        """Search for companies using Google Custom Search API with rich targeting"""
        logger.info(f"="*80)
        logger.info(f"🔍 SEARCH_COMPANIES CALLED WITH RICH CRITERIA")
        logger.info(f"Target count: {target_count}")
        logger.info(f"Google API key available: {bool(self.google_api_key)}")
        logger.info(f"Google CSE ID available: {bool(self.google_cse_id)}")
        logger.info(f"AIOHTTP available: {AIOHTTP_AVAILABLE}")
        
        if not self.google_api_key or not self.google_cse_id:
            logger.error(f"❌ Google API credentials not configured")
            logger.error(f"GOOGLE_API_KEY: {'SET (len={})'.format(len(self.google_api_key)) if self.google_api_key else 'NOT SET'}")
            logger.error(f"GOOGLE_CSE_ID: {'SET (len={})'.format(len(self.google_cse_id)) if self.google_cse_id else 'NOT SET'}")
            logger.error(f"Please set these environment variables in Railway:")
            logger.error(f"  - GOOGLE_API_KEY: Your Google API key")
            logger.error(f"  - GOOGLE_CSE_ID (or GOOGLE_SEARCH_ENGINE_ID): Your Custom Search Engine ID")
            logger.info(f"="*80)
            return []
        
        companies = []
        
        # Extract structured data from criteria
        keywords = criteria.get("keywords", [])
        industry = criteria.get("industry", "")
        location = criteria.get("location", "")
        company_size = criteria.get("company_size", "")
        exclude_keywords = criteria.get("exclude_keywords", [])
        original_prompt = criteria.get("prompt", "")  # NEW: Get original prompt
        
        logger.info(f"🎯 STRUCTURED SEARCH PARAMETERS:")
        logger.info(f"  Industry: {industry}")
        logger.info(f"  Location: {location}")
        logger.info(f"  Company Size: {company_size}")
        logger.info(f"  Keywords: {keywords}")
        logger.info(f"  Exclude: {exclude_keywords}")
        logger.info(f"  Original Prompt: {original_prompt[:100]}...")  # NEW: Log prompt
        
        # Build SMART search queries using ALL parameters
        search_queries = []
        
        # PRIORITY 1: Use AI-generated search queries from research guide analysis (MOST SPECIFIC)
        ai_queries = criteria.get("search_queries", [])
        if ai_queries:
            logger.info(f"✅ PRIORITY 1: Using {len(ai_queries)} AI-generated search queries from research guide")
            search_queries.extend(ai_queries)
        
        # PRIORITY 2: Build complementary queries from structured fields (AS FALLBACK/SUPPLEMENT)
        # Only add these if we don't have enough AI queries
        if len(search_queries) < 10:
            # 1. Highly targeted queries combining all parameters
            if industry and location and keywords:
                # "Technology companies in San Francisco AI SaaS"
                search_queries.append(f"{industry} companies in {location} {' '.join(keywords[:2])}")
                # "San Francisco Technology startups AI machine learning"
                search_queries.append(f"{location} {industry} startups {' '.join(keywords[:3])}")
            
            # 2. Industry + location specific
            if industry and location:
                search_queries.append(f"{industry} companies {location}")
                search_queries.append(f"top {industry} businesses {location}")
                search_queries.append(f"{industry} startups {location}")
            
            # 3. Keyword-focused with location
            if keywords and location:
                for keyword in keywords[:3]:
                    search_queries.append(f"{keyword} companies {location}")
                    search_queries.append(f"{keyword} startups {location}")
            
            # 4. Industry + keyword combinations
            if industry and keywords:
                for keyword in keywords[:3]:
                    search_queries.append(f"{industry} {keyword} companies")
            
            # 5. Company size specific searches
            if company_size and industry and location:
                size_term = "startups" if "Startup" in company_size else "companies"
                search_queries.append(f"{company_size.split('(')[0].strip()} {industry} {size_term} {location}")
            
            # 6. Pure keyword searches (broader)
            for keyword in keywords[:2]:
                search_queries.append(f"{keyword} company directory")
                search_queries.append(f"best {keyword} companies")
        
        # PRIORITY 3: Fallback to keywords if still no queries
        if len(search_queries) == 0 and keywords:
            logger.warning(f"⚠️ No AI queries or structured fields, using extracted keywords")
            for keyword in keywords[:5]:
                search_queries.append(f"{keyword} companies")
                search_queries.append(f"{keyword} startups")
        
        # PRIORITY 4: Last resort - use original prompt
        if len(search_queries) == 0 and original_prompt:
            logger.warning(f"⚠️ No queries generated, falling back to original prompt")
            search_queries.append(original_prompt)
            # Extract words from prompt as additional queries
            prompt_words = [w for w in original_prompt.split() if len(w) > 4][:5]
            for word in prompt_words:
                search_queries.append(f"{word} companies")
        
        logger.info(f"🔎 Generated {len(search_queries)} targeted search queries:")
        for i, query in enumerate(search_queries[:5], 1):
            logger.info(f"  {i}. \"{query}\"")
        if len(search_queries) > 5:
            logger.info(f"  ... and {len(search_queries) - 5} more queries")
        
        if not AIOHTTP_AVAILABLE:
            logger.error(f"❌ aiohttp not available, cannot make HTTP requests")
            logger.error(f"Install aiohttp: pip install aiohttp")
            logger.info(f"="*80)
            return []
            
        # Execute searches - do MORE searches for better coverage
        max_queries = min(len(search_queries), 10)  # Use up to 10 queries (was 3!)
        logger.info(f"📡 Will execute {max_queries} Google searches for comprehensive results")
        
        async with aiohttp.ClientSession() as session:
            for i, query in enumerate(search_queries[:max_queries], 1):
                try:
                    logger.info(f"🌐 Search {i}/{max_queries}: \"{query}\"")
                    companies_found = await self._search_google(session, query, target_count)
                    companies.extend(companies_found)
                    logger.info(f"  ✅ Found {len(companies_found)} companies from this search")
                    logger.info(f"  📊 Total so far: {len(companies)} companies")
                    
                    # Small delay between searches to be respectful to Google API
                    if i < max_queries:
                        await asyncio.sleep(1)  # 1 second delay between searches
                    
                    # Keep searching until we have enough UNIQUE companies
                    if len(set(c.get('domain', '') for c in companies)) >= target_count:
                        logger.info(f"✅ Reached target count of unique companies")
                        break
                        
                except Exception as e:
                    logger.error(f"❌ Error searching for '{query}': {e}")
                    continue
        
        # Remove duplicates and limit results
        unique_companies = []
        seen_domains = set()
        
        for company in companies:
            domain = company.get("domain", "")
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                unique_companies.append(company)
                
                if len(unique_companies) >= target_count:
                    break
        
        logger.info(f"✅ Found {len(unique_companies)} unique companies (target: {target_count})")
        logger.info(f"Returning {min(len(unique_companies), target_count)} companies")
        logger.info(f"="*80)
        return unique_companies[:target_count]
    
    async def _search_google(self, session, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search Google Custom Search API"""
        logger.info(f"🌐 Making Google API request for query: '{query}'")
        
        if not AIOHTTP_AVAILABLE:
            logger.error(f"❌ aiohttp not available, skipping Google search")
            return []
            
        # Exclude job boards and recruitment sites from results
        excluded_sites = [
            "linkedin.com/jobs",
            "indeed.com",
            "glassdoor.com",
            "ziprecruiter.com",
            "monster.com",
            "careerbuilder.com",
            "flexjobs.com",
            "simplyhired.com",
            "dice.com",
            "crunchbase.com/jobs"
        ]
        
        # Add site exclusions to query
        query_with_exclusions = query
        for site in excluded_sites[:3]:  # Only use top 3 to keep query reasonable
            query_with_exclusions += f" -site:{site}"
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "q": query_with_exclusions,
            "num": min(max_results, 10)  # Google API limit
        }
        
        try:
            logger.info(f"📡 Sending request to: {url}")
            logger.info(f"Parameters: key=*****, cx={self.google_cse_id[:10]}..., q={query[:50]}...")
            
            async with session.get(url, params=params) as response:
                logger.info(f"Response status: {response.status}")
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"❌ Google API error {response.status}: {error_text[:500]}")
                    return []
                
                data = await response.json()
                items_count = len(data.get("items", []))
                logger.info(f"✅ Received {items_count} search results from Google")
                
                companies = []
                
                for item in data.get("items", []):
                    try:
                        title = item.get("title", "")
                        link = item.get("link", "")
                        domain = self._extract_domain(link)
                        
                        # Filter out non-company results
                        filter_result = self._is_likely_article_or_blog(title, link, domain)
                        if filter_result:
                            logger.warning(f"  🚫 FILTERED OUT (reason: {filter_result}): {title[:80]}")
                            logger.warning(f"     Domain: {domain}, URL: {link[:80]}")
                            continue
                        
                        extracted_name = self._extract_company_name(title)
                        if not self._looks_like_company_name(extracted_name):
                            logger.warning(f"  🚫 FILTERED OUT (reason: suspicious company name): {extracted_name[:80]}")
                            continue

                        company = {
                            "name": extracted_name,
                            "website": link,
                            "description": item.get("snippet", ""),
                            "domain": domain,
                            "source": "Google Search",
                            "search_query": query
                        }
                        companies.append(company)
                        logger.info(f"  ✅ Added company: {company['name']} ({domain})")
                    except Exception as e:
                        logger.error(f"Error processing search result: {e}")
                        continue
                
                return companies
        except Exception as e:
            logger.error(f"Error searching Google: {e}")
            return []
    
    def _is_known_non_company_domain(self, domain: str) -> Optional[str]:
        if not domain:
            return "Missing domain"

        domain_lower = domain.lower()

        blocked_domains = {
            "business.com",
            "forbes.com",
            "finance.yahoo.com",
            "news.yahoo.com",
            "cnn.com",
            "nytimes.com",
            "theguardian.com",
            "bloomberg.com",
            "wsj.com",
            "cnbc.com",
            "marketwatch.com",
            "techcrunch.com",
            "venturebeat.com",
            "wired.com",
            "medium.com",
            "substack.com",
            "harvard.edu",
            "mit.edu",
            "wikipedia.org",
            "britannica.com",
            "microsoft.com",
            "learn.microsoft.com",
            "support.microsoft.com",
            "support.google.com",
            "developers.google.com",
            "docs.google.com",
            "cloud.google.com",
            "aws.amazon.com",
            "support.apple.com",
            "help.linkedin.com",
            "news.microsoft.com",
            "about.facebook.com",
            "help.twitter.com",
        }

        if domain_lower in blocked_domains:
            return "Publisher/directory domain"

        keyword_blocks = [
            "news.",
            ".news",
            "blog.",
            ".blog",
            "press",
            "insights",
            "resources",
            "support",
            "docs",
            "knowledge",
            "learn",
            "academy",
            "library",
            "events",
            "portal",
        ]

        for keyword in keyword_blocks:
            if keyword in domain_lower:
                return f"Domain contains '{keyword}' indicator"

        return None

    def _is_likely_article_or_blog(self, title: str, url: str, domain: str) -> Optional[str]:
        """Filter out articles, blogs, and other non-company results."""
        title_lower = title.lower()
        url_lower = url.lower()

        domain_reason = self._is_known_non_company_domain(domain)
        if domain_reason:
            return domain_reason

        article_patterns = [
            (r'\?', "Contains question mark (article)"),
            (r'\bhow\s+to\b', "How-to guide"),
            (r'\btop\s+\d+', "Top N list article"),
            (r'\bbest\s+\d+', "Best of list article"),
            (r'\bguide\b', "Guide article"),
            (r'\btips\b', "Tips article"),
            (r'\bwhy\s+', "Why question article"),
            (r'\bwhat\s+', "What question article"),
            (r'\bfind\s+', "Find X article"),
            (r'\bultimate\b', "Ultimate guide"),
            (r'\bcomplete\b', "Complete guide"),
            (r'\bbeginner', "Beginner guide"),
            (r'\bcourse\b', "Course/tutorial"),
            (r'\blesson\b', "Lesson/tutorial"),
            (r'\btutorial\b', "Tutorial"),
            (r'\bopportunit', "Opportunity article"),
            (r'\bpotential\b', "Opportunity article"),
            (r'\beconomic\b', "Economic analysis article"),
            (r'technology\s+leads', "Technology leads article"),
        ]

        for pattern, reason in article_patterns:
            if re.search(pattern, title_lower):
                return reason

        article_url_patterns = [
            ('/blog/', "Blog post URL"),
            ('/article/', "Article URL"),
            ('/post/', "Post URL"),
            ('/news/', "News article URL"),
            ('/resources/', "Resource page URL"),
            ('/learn/', "Learning resource URL"),
            ('/guide/', "Guide URL"),
            ('/insights/', "Insights article URL"),
            ('/knowledge-base/', "Knowledge base article URL"),
            ('/content/', "Content page URL"),
            ('/stories/', "Story article URL"),
            ('/wiki/', "Wiki page URL"),
            ('/docs/', "Documentation URL"),
            ('/help/', "Help article URL"),
        ]

        for pattern, reason in article_url_patterns:
            if pattern in url_lower:
                return reason

        if re.search(r'/20\d{2}/\d{2}/\d{2}/', url_lower):
            return "Dated article URL"

        article_domains = [
            ('medium.com', "Medium blog"),
            ('forbes.com', "Forbes article"),
            ('techcrunch.com', "TechCrunch article"),
            ('venturebeat.com', "VentureBeat article"),
            ('businessinsider.com', "Business Insider article"),
            ('entrepreneur.com', "Entrepreneur article"),
            ('inc.com', "Inc. article"),
            ('fastcompany.com', "Fast Company article"),
            ('wired.com', "Wired article"),
            ('mashable.com', "Mashable article"),
            ('reddit.com', "Reddit post"),
            ('quora.com', "Quora question"),
            ('stackoverflow.com', "Stack Overflow"),
            ('wikipedia.org', "Wikipedia page"),
            ('youtube.com', "YouTube video"),
            ('linkedin.com/pulse', "LinkedIn Pulse article"),
            ('hubspot.com/blog', "HubSpot blog"),
            ('knowledge.hubspot.com', "HubSpot knowledge base"),
            ('community.hubspot.com', "HubSpot community"),
            ('.gov', "Government site"),
            ('sba.gov', "SBA government site"),
            ('epa.gov', "EPA government site"),
            ('amazon.com', "Amazon product/book"),
            ('namelix.com', "Namelix tool"),
        ]

        for article_domain, reason in article_domains:
            if article_domain in domain:
                return reason

        if len(title) > 100:
            return "Title too long (likely article)"

        return None

    def _looks_like_company_name(self, name: str) -> bool:
        if not name:
            return False

        lowered = name.lower()
        disqualifiers = [
            "how ",
            "why ",
            "what ",
            "economic",
            "opportunit",
            "potential",
            "technology",
            "directory",
            "guide",
            "report",
            "case study",
            "whitepaper",
        ]

        if any(lowered.startswith(prefix.strip()) for prefix in disqualifiers):
            return False

        if any(keyword in lowered for keyword in ["opportunit", "potential", "technology leads", "economic"]):
            return False

        parts = [p for p in re.split(r"\s+", name) if p]
        if len(parts) > 6 or len(parts) < 1:
            return False

        return True
    
    def _extract_company_name(self, title: str) -> str:
        """Extract company name from search result title"""
        # Remove common suffixes and clean up
        title = re.sub(r'\s*-\s*.*$', '', title)  # Remove everything after dash
        title = re.sub(r'\s*\|\s*.*$', '', title)  # Remove everything after pipe
        title = re.sub(r'\s*:.*$', '', title)  # Remove everything after colon
        return title.strip()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""
    
    async def research_company_deep(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct deep research on a company using AI and web scraping"""
        logger.info(f"Researching company: {company.get('name')}")
        
        # Gather research data
        research_data = {
            "company": company,
            "website_content": await self._scrape_website(company.get("website", "")),
            "news_mentions": await self._search_company_news(company.get("name", "")),
            "social_signals": await self._get_social_signals(company.get("name", "")),
            "technology_stack": await self._analyze_tech_stack(company.get("website", "")),
            "funding_info": await self._get_funding_info(company.get("name", ""))
        }
        
        # Analyze with AI
        analysis = await self._analyze_company_with_ai(research_data)
        
        # Combine original company data with research
        company.update(analysis)
        company["research_completed_at"] = datetime.utcnow().isoformat()
        
        return company
    
    async def _scrape_website(self, url: str) -> str:
        """Scrape company website content"""
        if not url or not AIOHTTP_AVAILABLE:
            return ""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Basic text extraction (in production, use proper HTML parsing)
                        return content[:5000]  # Limit content size
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        
        return ""
    
    async def _search_company_news(self, company_name: str) -> List[Dict[str, Any]]:
        """Search for recent news about the company"""
        # This would integrate with NewsAPI or similar
        # For now, return mock data
        return [
            {
                "title": f"Recent news about {company_name}",
                "source": "Tech News",
                "date": datetime.utcnow().isoformat(),
                "summary": f"Latest developments at {company_name}"
            }
        ]
    
    async def _get_social_signals(self, company_name: str) -> Dict[str, Any]:
        """Get social media signals and engagement"""
        # This would integrate with social media APIs
        return {
            "linkedin_followers": 0,
            "twitter_followers": 0,
            "engagement_score": 0.5
        }
    
    async def _analyze_tech_stack(self, website: str) -> List[str]:
        """Analyze technology stack from website"""
        if not website or not AIOHTTP_AVAILABLE:
            return []
        
        # Basic tech stack detection (in production, use proper analysis)
        tech_indicators = ["React", "Angular", "Vue", "Node.js", "Python", "Java", "AWS", "Azure", "Google Cloud"]
        detected_tech = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(website, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        for tech in tech_indicators:
                            if tech.lower() in content.lower():
                                detected_tech.append(tech)
        except Exception as e:
            logger.error(f"Error analyzing tech stack for {website}: {e}")
        
        return detected_tech
    
    async def _get_funding_info(self, company_name: str) -> Dict[str, Any]:
        """Get funding information for the company"""
        # This would integrate with Crunchbase API or similar
        return {
            "total_funding": 0,
            "last_funding_round": None,
            "investors": [],
            "valuation": None
        }
    
    async def _analyze_company_with_ai(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company research data using AI"""
        if not self.openai_client and not self.claude_client:
            return {"analysis": "AI analysis not available"}
        
        company = research_data["company"]
        website_content = research_data["website_content"]
        
        analysis_prompt = f"""
        Analyze this company and provide insights:
        
        Company: {company.get('name', 'Unknown')}
        Website: {company.get('website', 'N/A')}
        Description: {company.get('description', 'N/A')}
        Website Content: {website_content[:2000]}
        
        Provide analysis in JSON format:
        {{
            "pain_points": ["List of likely pain points"],
            "growth_signals": ["Signs of growth or expansion"],
            "technology_needs": ["Technology needs or gaps"],
            "buying_triggers": ["What might trigger a purchase"],
            "key_decision_makers": ["Types of decision makers to target"],
            "reasons_to_reach_out": ["Why this company is a good prospect"],
            "industry_insights": ["Industry-specific insights"],
            "competitive_landscape": ["Competitive positioning"]
        }}
        """
        
        try:
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": analysis_prompt}],
                    temperature=0.3
                )
                analysis = json.loads(response.choices[0].message.content)
            elif self.claude_client:
                response = await self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": analysis_prompt}]
                )
                analysis = json.loads(response.content[0].text)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing company with AI: {e}")
            return {"analysis": "AI analysis failed"}
    
    async def find_company_contacts(self, company: Dict[str, Any], targeting_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find REAL contacts and decision makers for a company using WEB SCRAPING
        
        Args:
            company: Company information (name, domain, etc.)
            targeting_criteria: Optional targeting criteria from research guide
                - Can specify target_roles, target_titles, target_departments
        """
        company_name = company.get("name", "Unknown Company")
        domain = company.get("domain", "company.com")
        website = company.get("website", f"https://{domain}")
        
        logger.info(f"🔍 Finding REAL contacts for {company_name} at {website}")
        
        # Import web scraper
        try:
            from services.web_scraper import scrape_company_contacts
        except ImportError:
            logger.error("❌ Web scraper not available")
            return []
        
        # Extract targeting preferences from criteria
        target_roles = []
        
        if targeting_criteria:
            # Check for specific role targeting in research guide
            target_roles = targeting_criteria.get("target_roles", [])
            
            if target_roles:
                logger.info(f"🎯 Targeting specific roles from research guide: {target_roles}")
        
        # Use WEB SCRAPING to find real contacts
        try:
            logger.info(f"🌐 Scraping website for contacts: {website}")
            scraped_contacts = await scrape_company_contacts(
                company_name=company_name,
                website=website,
                target_roles=target_roles
            )
            
            if not scraped_contacts:
                logger.warning(f"⚠️ No contacts found via web scraping for {website}")
                return []
            
            logger.info(f"✅ Found {len(scraped_contacts)} REAL contacts via web scraping")
            
            # Web scraper already filters by target_roles if provided
            # Convert scraped contacts to standardized format
            contacts = []
            for i, scraped_contact in enumerate(scraped_contacts[:10], 1):  # Limit to 10 contacts
                # Scraper returns: contact_name, role, linkedin, email, confidence
                full_name = scraped_contact.get("contact_name", "Unknown")
                
                # Split name into first/last (basic)
                name_parts = full_name.split()
                first_name = name_parts[0] if len(name_parts) > 0 else ""
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                
                contact = {
                    "id": f"contact_{domain.replace('.', '_')}_{i}",
                    "company": company_name,
                    "contact_name": full_name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": scraped_contact.get("email", ""),
                    "phone": "",
                    "linkedin": scraped_contact.get("linkedin", ""),
                    "twitter": "",
                    "website": website,
                    "industry": company.get("industry", ""),
                    "location": company.get("location", ""),
                    "role": scraped_contact.get("role", "Team Member"),
                    "department": "",
                    "seniority": "Senior" if any(word in scraped_contact.get("role", "").lower() for word in ["director", "vp", "chief", "head", "manager"]) else "Mid",
                    "confidence": scraped_contact.get("confidence", 0.7),
                    "verification_status": "scraped",
                    "source": "Web Scraping",
                    "created_at": datetime.utcnow().isoformat(),
                    "research_data": company.get("research_data", {}),
                    "targeting_match": bool(target_roles)  # Flag if we used role targeting
                }
                contacts.append(contact)
                
                logger.info(f"   [{i}] {full_name} - {contact['role']}")
                if contact['linkedin']:
                    logger.info(f"       🔗 LinkedIn: {contact['linkedin'][:50]}...")
                if contact['email']:
                    logger.info(f"       📧 Email: {contact['email']}")
            
            logger.info(f"✅ Returning {len(contacts)} REAL contacts for {company_name}")
            return contacts
            
        except Exception as e:
            logger.error(f"❌ Exception finding contacts: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def generate_personalized_outreach(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized outreach messages for a lead"""
        if not self.openai_client and not self.claude_client:
            return {
                "linkedin_message": "Hi! I'd love to connect and discuss how we can help your business grow.",
                "email_subject": "Partnership Opportunity",
                "email_body": "Hi there, I'd love to discuss a potential partnership opportunity."
            }
        
        company = lead.get("company", "Unknown Company")
        contact_name = lead.get("contact_name", "there")
        role = lead.get("role", "decision maker")
        research_data = lead.get("research_data", {})
        
        outreach_prompt = f"""
        Generate personalized outreach messages for:
        
        Contact: {contact_name} ({role}) at {company}
        Company Research: {json.dumps(research_data, indent=2)}
        
        Create:
        1. LinkedIn connection message (max 300 characters)
        2. Email subject line (max 50 characters)
        3. Email body (max 200 words)
        
        Make it personal, relevant, and valuable. Reference specific insights from the research.
        Format as JSON:
        {{
            "linkedin_message": "...",
            "email_subject": "...",
            "email_body": "..."
        }}
        """
        
        try:
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": outreach_prompt}],
                    temperature=0.7
                )
                outreach = json.loads(response.choices[0].message.content)
            elif self.claude_client:
                response = await self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": outreach_prompt}]
                )
                outreach = json.loads(response.content[0].text)
            
            return outreach
            
        except Exception as e:
            logger.error(f"Error generating outreach: {e}")
            return {
                "linkedin_message": f"Hi {contact_name}, I'd love to connect and discuss how we can help {company} grow.",
                "email_subject": f"Partnership Opportunity for {company}",
                "email_body": f"Hi {contact_name}, I'd love to discuss a potential partnership opportunity for {company}."
            }

# Global instance
real_research_engine = RealResearchEngine()

# Export functions for use in main_simple.py
async def extract_targeting_criteria(prompt: str) -> Dict[str, Any]:
    return await real_research_engine.extract_targeting_criteria(prompt)

async def search_companies(criteria: Dict[str, Any], target_count: int) -> List[Dict[str, Any]]:
    return await real_research_engine.search_companies(criteria, target_count)

async def research_company_deep(company: Dict[str, Any]) -> Dict[str, Any]:
    return await real_research_engine.research_company_deep(company)

async def find_company_contacts(company: Dict[str, Any], targeting_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    return await real_research_engine.find_company_contacts(company, targeting_criteria)

async def generate_personalized_outreach(lead: Dict[str, Any]) -> Dict[str, Any]:
    return await real_research_engine.generate_personalized_outreach(lead)
