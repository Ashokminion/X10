"""
FastAPI router for HR chatbot endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from database import get_db, ChatHistory
from sqlalchemy.orm import Session
from engines.chatbot_engine import chatbot_engine
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    message: str

class ChatResponse(BaseModel):
    intent: str
    response: str
    data: dict = None
    timestamp: datetime

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Process user query through HR chatbot engine
    """
    try:
        start_time = datetime.now()
        
        # Process query
        result = chatbot_engine.process_query(request.message, db)
        
        end_time = datetime.now()
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Save chat history
        # User message
        user_chat = ChatHistory(
            user_id=request.user_id,
            message_type='USER',
            message_text=request.message,
            created_at=start_time
        )
        db.add(user_chat)
        
        # Bot response
        bot_chat = ChatHistory(
            user_id=request.user_id,
            message_type='BOT',
            message_text=result['response'],
            intent_detected=result['intent'],
            response_time_ms=response_time_ms,
            created_at=end_time
        )
        db.add(bot_chat)
        db.commit()
        
        return ChatResponse(
            intent=result['intent'],
            response=result['response'],
            data=result.get('data'),
            timestamp=end_time
        )
        
    except Exception as e:
        logger.error(f"Chatbot error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_chat_history(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve chat history for a user
    """
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).order_by(ChatHistory.created_at.desc()).limit(limit).all()
    
    result = []
    for chat in reversed(history):  # Reverse to get chronological order
        result.append({
            'message_type': chat.message_type,
            'message': chat.message_text,
            'timestamp': str(chat.created_at),
            'intent': chat.intent_detected
        })
    
    return {'user_id': user_id, 'history': result, 'count': len(result)}

@router.get("/intents")
async def get_supported_intents():
    """
    Get list of supported chatbot intents
    """
    intents_info = []
    for intent_name, intent_config in chatbot_engine.intents.items():
        intents_info.append({
            'intent': intent_name,
            'keywords': intent_config['keywords'],
            'example': f"Try asking about {intent_name.replace('_', ' ')}"
        })
    
    return {'supported_intents': intents_info}
