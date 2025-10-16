"""
Conversational AI Service for Target Audience Discovery
Guides users through strategic questions to build comprehensive audience profiles
"""

import openai
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

class ConversationalAI:
    """AI service that conducts strategic conversations to discover target audiences"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Conversation flow stages
        self.stages = {
            'introduction': 0,
            'business_context': 1,
            'target_demographics': 2,
            'pain_points': 3,
            'goals_objectives': 4,
            'buying_behavior': 5,
            'competition': 6,
            'messaging': 7,
            'finalization': 8
        }
        
        # Strategic questions for each stage
        self.question_sets = {
            'introduction': [
                "Hi! I'm here to help you identify your perfect target audience for lead generation. What's your business or product that you're looking to promote?",
                "Great! Can you tell me more about what you do and what makes your offering unique?",
                "What's the main problem your product or service solves for customers?"
            ],
            'business_context': [
                "What industry or market are you primarily targeting?",
                "What's the typical size of companies you work with? (startup, SMB, enterprise)",
                "What's your geographic focus? (local, national, international)",
                "How long have you been in this market?"
            ],
            'target_demographics': [
                "Who are the key decision makers for your product? (CEO, CTO, Marketing Director, etc.)",
                "What's the typical age range of your ideal customers?",
                "What's their professional background or experience level?",
                "What's their typical company role or seniority level?"
            ],
            'pain_points': [
                "What are the biggest challenges your target audience faces in their daily work?",
                "What problems keep them up at night that your solution addresses?",
                "What frustrations do they have with current solutions in the market?",
                "What would happen if they don't solve these problems?"
            ],
            'goals_objectives': [
                "What are the main goals your target audience is trying to achieve?",
                "What does success look like for them?",
                "What metrics or KPIs matter most to them?",
                "What outcomes are they hoping to achieve in the next 6-12 months?"
            ],
            'buying_behavior': [
                "How do your ideal customers typically research and evaluate solutions?",
                "What information do they need before making a purchase decision?",
                "Who else is involved in their buying process?",
                "What's their typical budget range for solutions like yours?"
            ],
            'competition': [
                "Who are your main competitors in this space?",
                "What do customers like and dislike about your competitors?",
                "What makes your solution different or better?",
                "How do customers currently solve this problem without you?"
            ],
            'messaging': [
                "What messaging or value propositions resonate most with your audience?",
                "What language or terminology do they use when discussing these problems?",
                "What proof points or case studies would be most compelling to them?",
                "What objections do they typically raise during sales conversations?"
            ],
            'finalization': [
                "Based on our conversation, let me summarize your ideal target audience...",
                "Is there anything else about your target audience that I should know?",
                "Would you like me to refine any of these characteristics?",
                "Perfect! I'll now create a comprehensive audience profile for your lead generation campaigns."
            ]
        }
    
    async def process_message(self, user_message: str, conversation_history: List[Dict[str, str]], current_stage: str = 'introduction') -> Dict[str, Any]:
        """
        Process user message and generate appropriate AI response
        
        Args:
            user_message: User's input message
            conversation_history: Previous conversation messages
            current_stage: Current conversation stage
            
        Returns:
            Dict containing AI response, next stage, and conversation data
        """
        try:
            # Build conversation context
            context = self._build_conversation_context(conversation_history, current_stage)
            
            # Generate AI response using OpenAI
            ai_response = await self._generate_ai_response(user_message, context, current_stage)
            
            # Determine next stage
            next_stage = self._determine_next_stage(current_stage, user_message, conversation_history)
            
            # Extract insights from conversation
            insights = self._extract_insights(conversation_history + [{"role": "user", "content": user_message}])
            
            return {
                "response": ai_response,
                "next_stage": next_stage,
                "insights": insights,
                "is_complete": next_stage == 'finalization',
                "progress": self._calculate_progress(next_stage)
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I'm having trouble processing your message. Could you please try again?",
                "next_stage": current_stage,
                "insights": {},
                "is_complete": False,
                "progress": 0
            }
    
    def _build_conversation_context(self, history: List[Dict[str, str]], current_stage: str) -> str:
        """Build context for AI response generation"""
        context = f"Current conversation stage: {current_stage}\n\n"
        context += "Conversation history:\n"
        
        for message in history[-10:]:  # Last 10 messages for context
            context += f"{message['role']}: {message['content']}\n"
        
        return context
    
    async def _generate_ai_response(self, user_message: str, context: str, current_stage: str) -> str:
        """Generate AI response using OpenAI"""
        try:
            if not self.openai_api_key:
                # Fallback to rule-based responses
                return self._get_fallback_response(current_stage, user_message)
            
            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": f"""You are an expert target audience discovery specialist. Your goal is to guide users through a strategic conversation to identify their ideal customers for lead generation campaigns.

Current stage: {current_stage}
Available questions for this stage: {self.question_sets.get(current_stage, [])}

Guidelines:
1. Ask ONE strategic question at a time
2. Be conversational and engaging
3. Listen to their answers and ask follow-up questions
4. Build on previous responses
5. Guide them toward specific, actionable audience characteristics
6. If they give vague answers, ask for more specifics
7. If they seem to be going off-topic, gently redirect to audience discovery
8. Show genuine interest in their business
9. Use their language and terminology
10. Build toward creating a detailed audience profile

Context: {context}"""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._get_fallback_response(current_stage, user_message)
    
    def _get_fallback_response(self, current_stage: str, user_message: str) -> str:
        """Fallback responses when OpenAI is not available"""
        questions = self.question_sets.get(current_stage, [])
        if questions:
            return questions[0]
        return "That's interesting! Can you tell me more about your target audience?"
    
    def _determine_next_stage(self, current_stage: str, user_message: str, history: List[Dict[str, str]]) -> str:
        """Determine the next conversation stage based on current progress"""
        current_index = self.stages.get(current_stage, 0)
        
        # Check if we have enough information for current stage
        if self._has_sufficient_info_for_stage(current_stage, history):
            # Move to next stage
            next_index = min(current_index + 1, len(self.stages) - 1)
            return list(self.stages.keys())[next_index]
        
        # Stay in current stage
        return current_stage
    
    def _has_sufficient_info_for_stage(self, stage: str, history: List[Dict[str, str]]) -> bool:
        """Check if we have sufficient information for the current stage"""
        # Simple heuristic: if we have 2+ exchanges in current stage, move on
        recent_messages = [msg for msg in history[-6:] if msg.get('role') == 'user']
        return len(recent_messages) >= 2
    
    def _extract_insights(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract key insights from the conversation"""
        insights = {
            'business_type': '',
            'industry': '',
            'target_demographics': {},
            'pain_points': [],
            'goals': [],
            'buying_behavior': {},
            'messaging_keywords': []
        }
        
        # Simple keyword extraction (in a real implementation, this would be more sophisticated)
        for message in conversation:
            if message.get('role') == 'user':
                content = message.get('content', '').lower()
                
                # Extract business type
                if any(word in content for word in ['saas', 'software', 'platform']):
                    insights['business_type'] = 'SaaS/Software'
                elif any(word in content for word in ['service', 'consulting', 'agency']):
                    insights['business_type'] = 'Service'
                elif any(word in content for word in ['product', 'physical', 'manufacturing']):
                    insights['business_type'] = 'Product'
                
                # Extract industry
                industries = ['technology', 'healthcare', 'finance', 'education', 'retail', 'manufacturing']
                for industry in industries:
                    if industry in content:
                        insights['industry'] = industry
                        break
        
        return insights
    
    def _calculate_progress(self, current_stage: str) -> int:
        """Calculate conversation progress percentage"""
        current_index = self.stages.get(current_stage, 0)
        total_stages = len(self.stages)
        return int((current_index / total_stages) * 100)
    
    async def generate_audience_profile(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate comprehensive audience profile from conversation"""
        try:
            if not self.openai_api_key:
                return self._generate_fallback_profile(conversation_history)
            
            # Prepare conversation summary
            conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
            
            prompt = f"""Based on this conversation about target audience discovery, create a comprehensive audience profile for lead generation campaigns.

Conversation:
{conversation_text}

Please provide a structured audience profile with:
1. Demographics (age, role, seniority, company size)
2. Psychographics (interests, pain points, goals, values)
3. Firmographics (industry, company size, technology stack)
4. Behavior (channels, content preferences, buying process)
5. Messaging recommendations
6. Search keywords and phrases

Format as JSON with clear categories and specific, actionable insights."""

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Try to parse JSON response
            try:
                profile = json.loads(response.choices[0].message.content)
                return profile
            except json.JSONDecodeError:
                # If not valid JSON, return structured format
                return {
                    "demographics": {"summary": response.choices[0].message.content},
                    "psychographics": {},
                    "firmographics": {},
                    "behavior": {},
                    "messaging": {},
                    "keywords": []
                }
                
        except Exception as e:
            logger.error(f"Error generating audience profile: {e}")
            return self._generate_fallback_profile(conversation_history)
    
    def _generate_fallback_profile(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate fallback profile when AI is not available"""
        return {
            "demographics": {
                "age_range": "25-45",
                "role": "Decision Makers",
                "seniority": "Mid to Senior Level"
            },
            "psychographics": {
                "interests": ["Technology", "Efficiency", "Growth"],
                "pain_points": ["Manual processes", "Time constraints"],
                "goals": ["Increase productivity", "Reduce costs"]
            },
            "firmographics": {
                "industry": "Technology",
                "company_size": "50-500 employees",
                "technology": ["Cloud platforms", "Modern frameworks"]
            },
            "behavior": {
                "channels": ["LinkedIn", "Industry forums"],
                "content": ["Technical blogs", "Case studies"],
                "timing": "Q4 planning, Q1 implementation"
            },
            "messaging": {
                "value_props": ["Efficiency", "ROI", "Scalability"],
                "tone": "Professional, results-focused"
            },
            "keywords": ["automation", "efficiency", "productivity", "scalability"]
        }

# Global instance
conversational_ai = ConversationalAI()
