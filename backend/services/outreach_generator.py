"""
Outreach Generator Service
Handles personalized outreach content generation using LLMs and company research
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..database.connection import DatabaseConnection
from ..models.schemas import OutreachContentResponse, OutreachChannel, OutreachGenerationRequest
from ..integrations.openai_client import OpenAIClient
from ..integrations.claude_client import ClaudeClient
from ..utils.outreach_framework import OutreachFramework
from ..utils.content_optimization import ContentOptimizationService
from ..utils.tone_analysis import ToneAnalysisService

logger = logging.getLogger(__name__)

class OutreachGenerator:
    """Service for generating personalized outreach content"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.claude_client = ClaudeClient()
        self.outreach_framework = OutreachFramework()
        self.content_optimization = ContentOptimizationService()
        self.tone_analysis = ToneAnalysisService()
    
    async def generate_company_outreach(self, company_id: str) -> List[OutreachContentResponse]:
        """Generate outreach content for a company"""
        try:
            # Get company and contact information
            company_data = await self._get_company_data(company_id)
            contacts = await self._get_company_contacts(company_id)
            research_profile = await self._get_company_research(company_id)
            
            if not company_data:
                logger.warning(f"Company {company_id} not found")
                return []
            
            outreach_content = []
            
            # Generate LinkedIn outreach
            linkedin_content = await self._generate_linkedin_outreach(company_data, contacts, research_profile)
            outreach_content.extend(linkedin_content)
            
            # Generate email outreach
            email_content = await self._generate_email_outreach(company_data, contacts, research_profile)
            outreach_content.extend(email_content)
            
            # Store outreach content
            stored_content = await self._store_outreach_content(company_id, outreach_content)
            
            logger.info(f"Generated {len(stored_content)} outreach pieces for company {company_id}")
            return stored_content
            
        except Exception as e:
            logger.error(f"Error generating outreach for company {company_id}: {str(e)}")
            raise
    
    async def _generate_linkedin_outreach(self, company_data: Dict[str, Any], 
                                        contacts: List[Dict[str, Any]], 
                                        research_profile: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate LinkedIn connection messages"""
        try:
            linkedin_content = []
            
            for contact in contacts:
                if not contact.get('linkedin_url'):
                    continue
                
                # Generate personalized LinkedIn message
                message_data = await self._create_linkedin_message(company_data, contact, research_profile)
                
                if message_data:
                    linkedin_content.append({
                        'contact_id': contact['id'],
                        'channel': OutreachChannel.LINKEDIN,
                        'subject': None,
                        'body': message_data['body'],
                        'tone': message_data['tone'],
                        'word_count': message_data['word_count'],
                        'quality_score': message_data['quality_score']
                    })
            
            return linkedin_content
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn outreach: {str(e)}")
            return []
    
    async def _generate_email_outreach(self, company_data: Dict[str, Any], 
                                     contacts: List[Dict[str, Any]], 
                                     research_profile: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate email outreach content"""
        try:
            email_content = []
            
            for contact in contacts:
                if not contact.get('email'):
                    continue
                
                # Generate personalized email
                email_data = await self._create_email_content(company_data, contact, research_profile)
                
                if email_data:
                    email_content.append({
                        'contact_id': contact['id'],
                        'channel': OutreachChannel.EMAIL,
                        'subject': email_data['subject'],
                        'body': email_data['body'],
                        'tone': email_data['tone'],
                        'word_count': email_data['word_count'],
                        'quality_score': email_data['quality_score']
                    })
            
            return email_content
            
        except Exception as e:
            logger.error(f"Error generating email outreach: {str(e)}")
            return []
    
    async def _create_linkedin_message(self, company_data: Dict[str, Any], 
                                    contact: Dict[str, Any], 
                                    research_profile: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Create personalized LinkedIn connection message"""
        try:
            # Build context for LinkedIn message
            context = await self._build_outreach_context(company_data, contact, research_profile)
            
            # Use outreach framework to generate message
            message_prompt = await self.outreach_framework.build_linkedin_prompt(context)
            
            # Generate message using LLM
            generated_content = await self.openai_client.generate_content(
                prompt=message_prompt,
                max_tokens=300,
                temperature=0.7
            )
            
            # Optimize content
            optimized_content = await self.content_optimization.optimize_linkedin_message(generated_content)
            
            # Analyze tone
            tone_analysis = await self.tone_analysis.analyze_tone(optimized_content)
            
            # Calculate quality score
            quality_score = await self._calculate_content_quality(optimized_content, tone_analysis)
            
            return {
                'body': optimized_content,
                'tone': tone_analysis.get('primary_tone', 'professional'),
                'word_count': len(optimized_content.split()),
                'quality_score': quality_score
            }
            
        except Exception as e:
            logger.error(f"Error creating LinkedIn message: {str(e)}")
            return None
    
    async def _create_email_content(self, company_data: Dict[str, Any], 
                                  contact: Dict[str, Any], 
                                  research_profile: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Create personalized email content"""
        try:
            # Build context for email
            context = await self._build_outreach_context(company_data, contact, research_profile)
            
            # Use outreach framework to generate email
            email_prompt = await self.outreach_framework.build_email_prompt(context)
            
            # Generate email using LLM
            generated_content = await self.openai_client.generate_content(
                prompt=email_prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            # Parse subject and body
            subject, body = await self._parse_email_content(generated_content)
            
            # Optimize content
            optimized_body = await self.content_optimization.optimize_email_body(body)
            optimized_subject = await self.content_optimization.optimize_email_subject(subject)
            
            # Analyze tone
            tone_analysis = await self.tone_analysis.analyze_tone(optimized_body)
            
            # Calculate quality score
            quality_score = await self._calculate_content_quality(optimized_body, tone_analysis)
            
            return {
                'subject': optimized_subject,
                'body': optimized_body,
                'tone': tone_analysis.get('primary_tone', 'professional'),
                'word_count': len(optimized_body.split()),
                'quality_score': quality_score
            }
            
        except Exception as e:
            logger.error(f"Error creating email content: {str(e)}")
            return None
    
    async def _build_outreach_context(self, company_data: Dict[str, Any], 
                                    contact: Dict[str, Any], 
                                    research_profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build context for outreach generation"""
        try:
            context = {
                'company': {
                    'name': company_data.get('name'),
                    'industry': company_data.get('attributes', {}).get('industry'),
                    'website': company_data.get('website'),
                    'city': company_data.get('city'),
                    'state': company_data.get('state')
                },
                'contact': {
                    'first_name': contact.get('first_name'),
                    'last_name': contact.get('last_name'),
                    'title': contact.get('title'),
                    'department': contact.get('department'),
                    'seniority_level': contact.get('seniority_level')
                },
                'research': research_profile or {},
                'outreach_goals': await self._determine_outreach_goals(company_data, contact, research_profile)
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error building outreach context: {str(e)}")
            return {}
    
    async def _determine_outreach_goals(self, company_data: Dict[str, Any], 
                                      contact: Dict[str, Any], 
                                      research_profile: Optional[Dict[str, Any]]) -> List[str]:
        """Determine outreach goals based on company and contact data"""
        try:
            goals = []
            
            # Add goals based on company stage
            if company_data.get('attributes', {}).get('funding_stage') == 'series_a':
                goals.append('discuss_growth_scaling')
            
            # Add goals based on contact role
            if contact.get('title', '').lower() in ['ceo', 'founder']:
                goals.append('strategic_partnership')
            elif 'marketing' in contact.get('title', '').lower():
                goals.append('marketing_collaboration')
            elif 'engineering' in contact.get('title', '').lower():
                goals.append('technical_discussion')
            
            # Add goals based on research insights
            if research_profile:
                pain_points = research_profile.get('pain_points', {})
                if pain_points.get('operational_challenges'):
                    goals.append('solve_operational_challenges')
                if pain_points.get('technology_gaps'):
                    goals.append('address_technology_gaps')
            
            return goals
            
        except Exception as e:
            logger.error(f"Error determining outreach goals: {str(e)}")
            return []
    
    async def _parse_email_content(self, generated_content: str) -> tuple[str, str]:
        """Parse generated content into subject and body"""
        try:
            lines = generated_content.strip().split('\n')
            
            # Find subject line
            subject = ""
            body_start = 0
            
            for i, line in enumerate(lines):
                if line.lower().startswith('subject:'):
                    subject = line.replace('Subject:', '').strip()
                    body_start = i + 1
                    break
                elif line.lower().startswith('subject '):
                    subject = line.replace('Subject ', '').strip()
                    body_start = i + 1
                    break
            
            # Extract body
            body_lines = lines[body_start:]
            body = '\n'.join(body_lines).strip()
            
            # If no subject found, use first line as subject
            if not subject and body_lines:
                subject = body_lines[0][:50] + "..." if len(body_lines[0]) > 50 else body_lines[0]
                body = '\n'.join(body_lines[1:]).strip()
            
            return subject, body
            
        except Exception as e:
            logger.error(f"Error parsing email content: {str(e)}")
            return "Follow-up", generated_content
    
    async def _calculate_content_quality(self, content: str, tone_analysis: Dict[str, Any]) -> float:
        """Calculate quality score for outreach content"""
        try:
            quality_score = 0.0
            
            # Length appropriateness (LinkedIn: 200-300 chars, Email: 100-300 words)
            word_count = len(content.split())
            if 50 <= word_count <= 500:
                quality_score += 0.2
            
            # Tone appropriateness
            primary_tone = tone_analysis.get('primary_tone', '')
            if primary_tone in ['professional', 'friendly', 'confident']:
                quality_score += 0.3
            
            # Personalization indicators
            personalization_score = await self._calculate_personalization_score(content)
            quality_score += personalization_score * 0.3
            
            # Grammar and readability
            readability_score = await self._calculate_readability_score(content)
            quality_score += readability_score * 0.2
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating content quality: {str(e)}")
            return 0.5
    
    async def _calculate_personalization_score(self, content: str) -> float:
        """Calculate personalization score for content"""
        try:
            personalization_indicators = [
                'your company', 'your team', 'your business',
                'I noticed', 'I saw', 'I read',
                'specifically', 'particularly', 'especially'
            ]
            
            score = 0.0
            for indicator in personalization_indicators:
                if indicator.lower() in content.lower():
                    score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating personalization score: {str(e)}")
            return 0.0
    
    async def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score for content"""
        try:
            # Simple readability check
            sentences = content.split('.')
            words = content.split()
            
            if not sentences or not words:
                return 0.0
            
            avg_sentence_length = len(words) / len(sentences)
            
            # Optimal sentence length is 15-20 words
            if 10 <= avg_sentence_length <= 25:
                return 1.0
            elif 5 <= avg_sentence_length <= 30:
                return 0.7
            else:
                return 0.3
                
        except Exception as e:
            logger.error(f"Error calculating readability score: {str(e)}")
            return 0.5
    
    async def get_outreach_content(self, db: DatabaseConnection, company_id: str, 
                                 channel: Optional[str] = None) -> List[OutreachContentResponse]:
        """Get outreach content for a company"""
        try:
            query = "SELECT * FROM outreach_content WHERE company_id = %s"
            params = [company_id]
            
            if channel:
                query += " AND channel = %s"
                params.append(channel)
            
            query += " ORDER BY created_at DESC"
            
            results = await db.fetch_all(query, params)
            return [OutreachContentResponse(**row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting outreach content for company {company_id}: {str(e)}")
            raise
    
    async def approve_outreach(self, db: DatabaseConnection, outreach_id: str) -> bool:
        """Approve outreach content for sending"""
        try:
            result = await db.execute(
                "UPDATE outreach_content SET status = 'approved', updated_at = %s WHERE id = %s",
                (datetime.utcnow(), outreach_id)
            )
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error approving outreach {outreach_id}: {str(e)}")
            raise
    
    async def _store_outreach_content(self, company_id: str, content_list: List[Dict[str, Any]]) -> List[OutreachContentResponse]:
        """Store outreach content in database"""
        try:
            stored_content = []
            
            for content_data in content_list:
                content_id = str(uuid.uuid4())
                
                # Prepare content record
                content_record = {
                    "id": content_id,
                    "company_id": company_id,
                    "contact_id": content_data.get('contact_id'),
                    "channel": content_data.get('channel'),
                    "subject": content_data.get('subject'),
                    "body": content_data.get('body'),
                    "tone": content_data.get('tone', 'professional'),
                    "word_count": content_data.get('word_count'),
                    "quality_score": content_data.get('quality_score', 0.0),
                    "status": 'draft',
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Store in database
                await self._insert_outreach_content(content_record)
                
                # Convert to response model
                stored_content.append(OutreachContentResponse(**content_record))
            
            return stored_content
            
        except Exception as e:
            logger.error(f"Error storing outreach content: {str(e)}")
            raise
    
    # Helper methods
    async def _get_company_data(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get company data from database"""
        # Implementation would fetch from database
        return None
    
    async def _get_company_contacts(self, company_id: str) -> List[Dict[str, Any]]:
        """Get contacts for a company"""
        # Implementation would fetch from database
        return []
    
    async def _get_company_research(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get research profile for a company"""
        # Implementation would fetch from database
        return None
    
    async def _insert_outreach_content(self, content_record: Dict[str, Any]):
        """Insert outreach content into database"""
        # Implementation would insert into database
        pass
