from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import User, NutritionKnowledge
from app.schemas import NutritionKnowledgeResponse
from app.utils import get_current_user

router = APIRouter(prefix="/knowledge", tags=["营养知识"])


@router.get("/", response_model=List[NutritionKnowledgeResponse], summary="获取营养知识列表")
def get_knowledge_list(
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(NutritionKnowledge)
    
    if category:
        query = query.filter(NutritionKnowledge.category == category)
    
    offset = (page - 1) * page_size
    knowledge_list = query.offset(offset).limit(page_size).all()
    
    return [NutritionKnowledgeResponse.model_validate(k) for k in knowledge_list]


@router.get("/{knowledge_id}", response_model=NutritionKnowledgeResponse, summary="获取营养知识详情")
def get_knowledge_detail(
    knowledge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    knowledge = db.query(NutritionKnowledge).filter(
        NutritionKnowledge.id == knowledge_id
    ).first()
    
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到营养知识"
        )
    
    return NutritionKnowledgeResponse.model_validate(knowledge)


@router.get("/categories", summary="获取知识分类列表")
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    categories = db.query(NutritionKnowledge.category).distinct().all()
    return [c[0] for c in categories if c[0]]


@router.get("/search", response_model=List[NutritionKnowledgeResponse], summary="搜索营养知识")
def search_knowledge(
    keyword: str,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    offset = (page - 1) * page_size
    
    knowledge_list = db.query(NutritionKnowledge).filter(
        (NutritionKnowledge.title.contains(keyword)) |
        (NutritionKnowledge.content.contains(keyword))
    ).offset(offset).limit(page_size).all()
    
    return [NutritionKnowledgeResponse.model_validate(k) for k in knowledge_list]
