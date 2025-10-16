"""
Research Engine Service
Handles deep company research using LLMs and multiple data sources
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..database.connection import DatabaseConnection
from ..models.schemas import CompanyProfileResponse, ResearchSummary, PainPoints, GrowthSignals, TechStack, BuyingTriggers
from ..integrations.openai_client import OpenAIClient
from ..integrations.claude_client import ClaudeClient
from ..integrations.news_api import NewsAPIClient
from ..integrations.crunchbase_client import CrunchbaseClient
from ..integrations.web_scraper import WebScraperService
from ..utils.research_framework import ResearchFramework
from ..utils.knowledge_extraction import KnowledgeExtractionService

logger = logging.getLogger(__name__)

class ResearchEngine:
    """Service for conducting deep company research"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.claude_client = ClaudeClient()
        self.news_api = NewsAPIClient()
        self.crunchbase_client = CrunchbaseClient()
        self.web_scraper = WebScraperService()
        self.research_framework = ResearchFramework()
        self.knowledge_extraction = KnowledgeExtractionService()
    
    async def research_company(self, company_id: str) -> CompanyProfileResponse:
        """Conduct comprehensive research on a company"""
        try:
            # Get company information
            company = await self._get_company_info(company_id)
            if not company:
                logger.warning(f"Company {company_id} not found")
                return None
            
            # Gather research data from multiple sources
            research_data = await self._gather_research_data(company)
            
            # Analyze data using research framework
            analysis_results = await self._analyze_research_data(research_data, company)
            
            # Generate structured research profile
            profile = await self._generate_research_profile(analysis_results, company)
            
            # Store research profile in database
            stored_profile = await self._store_research_profile(company_id, profile)
            
            logger.info(f"Completed research for company {company_id}")
            return stored_profile
            
        except Exception as e:
            logger.error(f"Error researching company {company_id}: {str(e)}")
            raise
    
    async def _gather_research_data(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Gather research data from multiple sources"""
        try:
            research_data = {
                "company_info": company,
                "news_articles": [],
                "funding_data": {},
                "website_content": {},
                "social_media": {},
                "competitor_analysis": {},
                "market_intelligence": {}
            }
            
            # 1. News and Media Coverage
            news_data = await self._gather_news_data(company)
            research_data["news_articles"] = news_data
            
            # 2. Funding and Investment Data
            funding_data = await self._gather_funding_data(company)
            research_data["funding_data"] = funding_data
            
            # 3. Website Content Analysis
            website_data = await self._gather_website_data(company)
            research_data["website_content"] = website_data
            
            # 4. Social Media Intelligence
            social_data = await self._gather_social_media_data(company)
            research_data["social_media"] = social_data
            
            # 5. Competitor Analysis
            competitor_data = await self._gather_competitor_data(company)
            research_data["competitor_analysis"] = competitor_data
            
            # 6. Market Intelligence
            market_data = await self._gather_market_intelligence(company)
            research_data["market_intelligence"] = market_data
            
            return research_data
            
        except Exception as e:
            logger.error(f"Error gathering research data: {str(e)}")
            return {}
    
    async def _gather_news_data(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gather news articles about the company"""
        try:
            news_articles = []
            
            # Search for news using company name and domain
            search_queries = [
                f'"{company["name"]}"',
                f'"{company.get("domain", "")}"',
                f'"{company["name"]}" funding',
                f'"{company["name"]}" hiring',
                f'"{company["name"]}" expansion'
            ]
            
            for query in search_queries:
                articles = await self.news_api.search_articles(query, days=90)
                news_articles.extend(articles)
            
            # Remove duplicates
            unique_articles = await self._deduplicate_articles(news_articles)
            
            logger.info(f"Gathered {len(unique_articles)} news articles")
            return unique_articles
            
        except Exception as e:
            logger.error(f"Error gathering news data: {str(e)}")
            return []
    
    async def _gather_funding_data(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Gather funding and investment data"""
        try:
            funding_data = {}
            
            # Get funding data from Crunchbase
            if company.get('name'):
                cb_funding = await self.crunchbase_client.get_company_funding(company['name'])
                if cb_funding:
                    funding_data.update(cb_funding)
            
            # Get recent funding rounds
            recent_rounds = await self.crunchbase_client.get_recent_funding(company['name'])
            funding_data['recent_rounds'] = recent_rounds
            
            logger.info(f"Gathered funding data for {company['name']}")
            return funding_data
            
        except Exception as e:
            logger.error(f"Error gathering funding data: {str(e)}")
            return {}
    
    async def _gather_website_data(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Gather and analyze website content"""
        try:
            website_data = {}
            website_url = company.get('website')
            
            if not website_url:
                return website_data
            
            # Scrape key pages
            key_pages = await self._get_key_website_pages(website_url)
            
            for page_type, page_url in key_pages.items():
                content = await self.web_scraper.scrape_website(page_url)
                website_data[page_type] = content
            
            # Extract key information
            extracted_info = await self.knowledge_extraction.extract_company_info(website_data)
            website_data['extracted_info'] = extracted_info
            
            logger.info(f"Gathered website data for {company['name']}")
            return website_data
            
        except Exception as e:
            logger.error(f"Error gathering website data: {str(e)}")
            return {}
    
    async def _gather_social_media_data(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Gather social media intelligence"""
        try:
            social_data = {}
            
            # LinkedIn company page analysis
            linkedin_data = await self._analyze_linkedin_company(company)
            social_data['linkedin'] = linkedin_data
            
            # Twitter/X mentions
            twitter_data = await self._analyze_twitter_mentions(company)
            social_data['twitter'] = twitter_data
            
            logger.info(f"Gathered social media data for {company['name']}")
            return social_data
            
        except Exception as e:
            logger.error(f"Error gathering social media data: {str(e)}")
            return {}
    
    async def _gather_competitor_data(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Gather competitor analysis data"""
        try:
            competitor_data = {}
            
            # Identify competitors
            competitors = await self._identify_competitors(company)
            competitor_data['competitors'] = competitors
            
            # Analyze competitive positioning
            positioning = await self._analyze_competitive_positioning(company, competitors)
            competitor_data['positioning'] = positioning
            
            logger.info(f"Gathered competitor data for {company['name']}")
            return competitor_data
            
        except Exception as e:
            logger.error(f"Error gathering competitor data: {str(e)}")
            return {}
    
    async def _gather_market_intelligence(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Gather market intelligence and trends"""
        try:
            market_data = {}
            
            # Industry trends
            industry_trends = await self._analyze_industry_trends(company)
            market_data['industry_trends'] = industry_trends
            
            # Market size and growth
            market_size = await self._analyze_market_size(company)
            market_data['market_size'] = market_size
            
            # Regulatory environment
            regulatory = await self._analyze_regulatory_environment(company)
            market_data['regulatory'] = regulatory
            
            logger.info(f"Gathered market intelligence for {company['name']}")
            return market_data
            
        except Exception as e:
            logger.error(f"Error gathering market intelligence: {str(e)}")
            return {}
    
    async def _analyze_research_data(self, research_data: Dict[str, Any], company: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze research data using LLM-powered framework"""
        try:
            analysis_results = {}
            
            # Use research framework to analyze data
            framework_analysis = await self.research_framework.analyze_company(research_data, company)
            analysis_results.update(framework_analysis)
            
            # Extract pain points
            pain_points = await self._extract_pain_points(research_data)
            analysis_results['pain_points'] = pain_points
            
            # Identify growth signals
            growth_signals = await self._identify_growth_signals(research_data)
            analysis_results['growth_signals'] = growth_signals
            
            # Analyze technology stack
            tech_stack = await self._analyze_technology_stack(research_data)
            analysis_results['tech_stack'] = tech_stack
            
            # Identify buying triggers
            buying_triggers = await self._identify_buying_triggers(research_data)
            analysis_results['buying_triggers'] = buying_triggers
            
            # Generate reasons to reach out
            reasons_to_reach_out = await self._generate_reasons_to_reach_out(analysis_results)
            analysis_results['reasons_to_reach_out'] = reasons_to_reach_out
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing research data: {str(e)}")
            return {}
    
    async def _generate_research_profile(self, analysis_results: Dict[str, Any], company: Dict[str, Any]) -> CompanyProfileResponse:
        """Generate structured research profile"""
        try:
            profile_id = str(uuid.uuid4())
            
            # Create research summary
            research_summary = ResearchSummary(
                company_overview=analysis_results.get('company_overview', ''),
                key_initiatives=analysis_results.get('key_initiatives', []),
                recent_developments=analysis_results.get('recent_developments', []),
                competitive_position=analysis_results.get('competitive_position', ''),
                growth_opportunities=analysis_results.get('growth_opportunities', [])
            )
            
            # Create pain points
            pain_points = PainPoints(
                operational_challenges=analysis_results.get('pain_points', {}).get('operational', []),
                technology_gaps=analysis_results.get('pain_points', {}).get('technology', []),
                compliance_requirements=analysis_results.get('pain_points', {}).get('compliance', []),
                cost_pressures=analysis_results.get('pain_points', {}).get('cost', [])
            )
            
            # Create growth signals
            growth_signals = GrowthSignals(
                recent_funding=analysis_results.get('funding_data', {}),
                hiring_trends=analysis_results.get('growth_signals', {}).get('hiring', []),
                expansion_plans=analysis_results.get('growth_signals', {}).get('expansion', []),
                technology_adoption=analysis_results.get('growth_signals', {}).get('technology', [])
            )
            
            # Create tech stack
            tech_stack = TechStack(
                primary_technologies=analysis_results.get('tech_stack', {}).get('primary', []),
                infrastructure=analysis_results.get('tech_stack', {}).get('infrastructure', []),
                development_tools=analysis_results.get('tech_stack', {}).get('development', []),
                cloud_platforms=analysis_results.get('tech_stack', {}).get('cloud', [])
            )
            
            # Create buying triggers
            buying_triggers = BuyingTriggers(
                immediate_needs=analysis_results.get('buying_triggers', {}).get('immediate', []),
                budget_cycle=analysis_results.get('buying_triggers', {}).get('budget_cycle'),
                decision_makers=analysis_results.get('buying_triggers', {}).get('decision_makers', []),
                evaluation_criteria=analysis_results.get('buying_triggers', {}).get('criteria', [])
            )
            
            # Calculate research confidence
            research_confidence = await self._calculate_research_confidence(analysis_results)
            
            # Create sources list
            sources = await self._compile_sources(analysis_results)
            
            profile = CompanyProfileResponse(
                id=profile_id,
                company_id=company['id'],
                research_summary=research_summary,
                pain_points=pain_points,
                growth_signals=growth_signals,
                tech_stack=tech_stack,
                buying_triggers=buying_triggers,
                recent_investments=analysis_results.get('funding_data', {}),
                reasons_to_reach_out=analysis_results.get('reasons_to_reach_out', []),
                sources=sources,
                research_confidence=research_confidence,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error generating research profile: {str(e)}")
            raise
    
    async def get_company_profile(self, db: DatabaseConnection, company_id: str) -> Optional[CompanyProfileResponse]:
        """Get research profile for a company"""
        try:
            result = await db.fetch_one(
                "SELECT * FROM company_profiles WHERE company_id = %s ORDER BY created_at DESC LIMIT 1",
                (company_id,)
            )
            
            if not result:
                return None
                
            return CompanyProfileResponse(**result)
            
        except Exception as e:
            logger.error(f"Error getting company profile for {company_id}: {str(e)}")
            raise
    
    async def _store_research_profile(self, company_id: str, profile: CompanyProfileResponse) -> CompanyProfileResponse:
        """Store research profile in database"""
        try:
            # Store in database
            await self._insert_research_profile(profile)
            
            logger.info(f"Stored research profile for company {company_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error storing research profile: {str(e)}")
            raise
    
    # Helper methods
    async def _get_company_info(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get company information from database"""
        # Implementation would fetch from database
        return None
    
    async def _get_key_website_pages(self, website_url: str) -> Dict[str, str]:
        """Get key pages to scrape from a website"""
        pages = {
            'home': website_url,
            'about': f"{website_url}/about",
            'team': f"{website_url}/team",
            'careers': f"{website_url}/careers",
            'news': f"{website_url}/news",
            'blog': f"{website_url}/blog"
        }
        return pages
    
    async def _deduplicate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles"""
        unique_articles = []
        seen_urls = set()
        
        for article in articles:
            url = article.get('url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        return unique_articles
    
    async def _analyze_linkedin_company(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze LinkedIn company page"""
        # Add LinkedIn analysis logic here
        return {}
    
    async def _analyze_twitter_mentions(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Twitter mentions"""
        # Add Twitter analysis logic here
        return {}
    
    async def _identify_competitors(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify competitors"""
        # Add competitor identification logic here
        return []
    
    async def _analyze_competitive_positioning(self, company: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitive positioning"""
        # Add competitive analysis logic here
        return {}
    
    async def _analyze_industry_trends(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze industry trends"""
        # Add industry trend analysis logic here
        return {}
    
    async def _analyze_market_size(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market size and growth"""
        # Add market size analysis logic here
        return {}
    
    async def _analyze_regulatory_environment(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze regulatory environment"""
        # Add regulatory analysis logic here
        return {}
    
    async def _extract_pain_points(self, research_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract pain points from research data"""
        # Add pain point extraction logic here
        return {}
    
    async def _identify_growth_signals(self, research_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Identify growth signals"""
        # Add growth signal identification logic here
        return {}
    
    async def _analyze_technology_stack(self, research_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Analyze technology stack"""
        # Add tech stack analysis logic here
        return {}
    
    async def _identify_buying_triggers(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify buying triggers"""
        # Add buying trigger identification logic here
        return {}
    
    async def _generate_reasons_to_reach_out(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate reasons to reach out"""
        # Add reason generation logic here
        return []
    
    async def _calculate_research_confidence(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate confidence in research quality"""
        # Add confidence calculation logic here
        return 0.8
    
    async def _compile_sources(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compile list of sources used in research"""
        sources = []
        # Add source compilation logic here
        return sources
    
    async def _insert_research_profile(self, profile: CompanyProfileResponse):
        """Insert research profile into database"""
        # Implementation would insert into database
        pass
