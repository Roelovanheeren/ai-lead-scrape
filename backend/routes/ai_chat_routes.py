"""
AI Chat API Routes
Handles conversational AI for target audience discovery
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging

from ..services.conversational_ai import conversational_ai

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-chat", tags=["ai-chat"])

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage]
    current_stage: Optional[str] = 'introduction'

class ChatResponse(BaseModel):
    response: str
    next_stage: str
    insights: Dict[str, Any]
    is_complete: bool
    progress: int

class AudienceProfileRequest(BaseModel):
    conversation_history: List[ChatMessage]

@router.post("/message", response_model=ChatResponse)
async def process_chat_message(request: ChatRequest):
    """Process a chat message and return AI response"""
    try:
        # Convert Pydantic models to dict format
        history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]
        
        result = await conversational_ai.process_message(
            request.message,
            history,
            request.current_stage
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-profile")
async def generate_audience_profile(request: AudienceProfileRequest):
    """Generate comprehensive audience profile from conversation"""
    try:
        # Convert Pydantic models to dict format
        history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]
        
        profile = await conversational_ai.generate_audience_profile(history)
        
        return {
            "status": "success",
            "profile": profile,
            "message": "Audience profile generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating audience profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stages")
async def get_conversation_stages():
    """Get available conversation stages"""
    return {
        "stages": list(conversational_ai.stages.keys()),
        "stage_descriptions": {
            "introduction": "Initial greeting and business context",
            "business_context": "Understanding the business and market",
            "target_demographics": "Identifying key decision makers",
            "pain_points": "Discovering customer challenges",
            "goals_objectives": "Understanding customer goals",
            "buying_behavior": "Learning about the buying process",
            "competition": "Understanding competitive landscape",
            "messaging": "Developing messaging strategy",
            "finalization": "Completing the audience profile"
        }
    }

@router.get("/questions/{stage}")
async def get_stage_questions(stage: str):
    """Get questions for a specific conversation stage"""
    questions = conversational_ai.question_sets.get(stage, [])
    return {
        "stage": stage,
        "questions": questions,
        "total_questions": len(questions)
    }

@router.post("/reset-conversation")
async def reset_conversation():
    """Reset conversation to beginning"""
    return {
        "status": "success",
        "message": "Conversation reset to beginning",
        "current_stage": "introduction",
        "progress": 0
    }

@router.get("/health")
async def check_ai_health():
    """Check if AI service is working"""
    try:
        # Test with a simple message
        test_result = await conversational_ai.process_message(
            "Hello, I want to find my target audience",
            [],
            "introduction"
        )
        
        return {
            "status": "healthy",
            "ai_working": True,
            "openai_configured": conversational_ai.openai_api_key is not None
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "ai_working": False,
            "error": str(e)
        }
