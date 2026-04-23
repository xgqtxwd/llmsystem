from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import asyncio
from app.database import get_db
from app.models import User, ChatRecord, UserHealthProfile, UserDietPreference, UserHealthGoal
from app.schemas import ChatMessageCreate, ChatMessageResponse
from app.services.llm_service import llm_service
from app.utils import get_current_user

router = APIRouter(prefix="/chat", tags=["智能对话"])


def get_user_context(user: User, db: Session) -> dict:
    context = {}
    
    profile = db.query(UserHealthProfile).filter(
        UserHealthProfile.user_id == user.id
    ).first()
    if profile:
        context["age"] = profile.age
        context["gender"] = profile.gender
        context["height"] = profile.height
        context["weight"] = profile.weight
        context["bmi"] = profile.bmi
        context["activity_level"] = profile.activity_level
        context["health_conditions"] = profile.health_conditions
    
    preference = db.query(UserDietPreference).filter(
        UserDietPreference.user_id == user.id
    ).first()
    if preference:
        context["taste_preference"] = preference.taste_preference
        context["diet_type"] = preference.diet_type
        context["allergies"] = preference.allergies
        context["forbidden_foods"] = preference.forbidden_foods
    
    goal = db.query(UserHealthGoal).filter(
        UserHealthGoal.user_id == user.id
    ).first()
    if goal:
        context["goal_type"] = goal.goal_type
        context["target_weight"] = goal.target_weight
        context["daily_calorie_target"] = goal.daily_calorie_target
    
    return context


@router.post("/message", response_model=ChatMessageResponse, summary="发送聊天消息")
async def send_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_context = get_user_context(current_user, db)
    
    answer = None
    try:
        answer = await llm_service.generate_nutrition_advice(user_context, message.message)
    except Exception as e:
        answer = f"抱歉，处理您的请求时发生错误。请稍后重试。{str(e)}"
    
    chat_record = ChatRecord(
        user_id=current_user.id,
        question=message.message,
        answer=answer,
        created_at=datetime.now()
    )
    
    db.add(chat_record)
    db.commit()
    db.refresh(chat_record)
    
    return ChatMessageResponse.model_validate(chat_record)


@router.get("/history", response_model=List[ChatMessageResponse], summary="获取对话历史")
def get_chat_history(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * page_size
    
    records = db.query(ChatRecord).filter(
        ChatRecord.user_id == current_user.id
    ).order_by(ChatRecord.created_at.desc()).offset(offset).limit(page_size).all()
    
    total = db.query(ChatRecord).filter(
        ChatRecord.user_id == current_user.id
    ).count()
    
    return [ChatMessageResponse.model_validate(record) for record in records]


@router.get("/history/{message_id}", response_model=ChatMessageResponse, summary="获取单条对话记录")
def get_chat_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(ChatRecord).filter(
        ChatRecord.id == message_id,
        ChatRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到对话记录"
        )
    
    return ChatMessageResponse.model_validate(record)


@router.delete("/history", summary="清空对话历史")
def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.query(ChatRecord).filter(
        ChatRecord.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return {"message": "对话历史已清空"}


@router.get("/stats", summary="获取对话统计")
def get_chat_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_messages = db.query(ChatRecord).filter(
        ChatRecord.user_id == current_user.id
    ).count()
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_messages = db.query(ChatRecord).filter(
        ChatRecord.user_id == current_user.id,
        ChatRecord.created_at >= today
    ).count()
    
    return {
        "total_messages": total_messages,
        "today_messages": today_messages
    }
