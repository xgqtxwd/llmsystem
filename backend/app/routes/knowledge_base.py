from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
from app.database import get_db
from app.models import User
from app.utils import get_current_user
from app.services.rag_service import rag_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge-base", tags=["知识库管理"])


class KnowledgeAddRequest(BaseModel):
    content: str
    content_type: str
    category: Optional[str] = None


class KnowledgeUpdateRequest(BaseModel):
    content: str
    category: Optional[str] = None


class KnowledgeSearchRequest(BaseModel):
    query: str
    content_type: Optional[str] = None
    top_k: int = 5


@router.get("/stats", summary="获取知识库统计")
async def get_knowledge_stats(
    current_user: User = Depends(get_current_user)
):
    """获取知识库统计信息"""
    try:
        stats = rag_service.get_knowledge_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"获取知识库统计失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/", summary="获取知识列表")
async def get_knowledge_list(
    content_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user)
):
    """获取知识库中的知识列表"""
    try:
        all_knowledge = rag_service.get_all_knowledge(content_type, page=page, page_size=page_size)
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        paginated_knowledge = all_knowledge[start:end]
        
        return {
            "success": True,
            "data": paginated_knowledge,
            "total": len(all_knowledge),
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.error(f"获取知识列表失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/", summary="添加知识")
async def add_knowledge(
    request: KnowledgeAddRequest,
    current_user: User = Depends(get_current_user)
):
    """向知识库添加新知识"""
    try:
        success = await rag_service.add_knowledge(
            content=request.content,
            content_type=request.content_type,
            metadata={"category": request.category} if request.category else None
        )
        
        if success:
            return {
                "success": True,
                "message": "知识添加成功"
            }
        else:
            return {
                "success": False,
                "error": "知识添加失败"
            }
    except Exception as e:
        logger.error(f"添加知识失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.delete("/{knowledge_id}", summary="删除知识")
async def delete_knowledge(
    knowledge_id: int,
    current_user: User = Depends(get_current_user)
):
    """删除指定知识"""
    try:
        success = rag_service.delete_knowledge(knowledge_id)
        
        if success:
            return {
                "success": True,
                "message": "知识删除成功"
            }
        else:
            return {
                "success": False,
                "error": "知识删除失败"
            }
    except Exception as e:
        logger.error(f"删除知识失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/search", summary="搜索知识")
async def search_knowledge(
    request: KnowledgeSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """在知识库中搜索相关内容"""
    try:
        results = rag_service.retrieve_knowledge(
            query=request.query,
            content_type=request.content_type,
            top_k=request.top_k
        )
        
        return {
            "success": True,
            "query": request.query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"搜索知识失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/types", summary="获取知识类型列表")
async def get_knowledge_types(
    current_user: User = Depends(get_current_user)
):
    """获取知识库中的知识类型"""
    types = [
        {"value": "nutrition", "label": "营养知识", "description": "关于营养成分、食物搭配等知识"},
        {"value": "recipe", "label": "食谱", "description": "各类食谱信息"},
        {"value": "ingredient", "label": "食材", "description": "食材营养信息和特点"},
        {"value": "advice", "label": "饮食建议", "description": "健康饮食建议"},
        {"value": "seasonal", "label": "季节性知识", "description": "季节性饮食知识"}
    ]
    
    return {
        "success": True,
        "types": types
    }


@router.post("/batch-add", summary="批量添加知识")
async def batch_add_knowledge(
    knowledge_list: List[KnowledgeAddRequest],
    current_user: User = Depends(get_current_user)
):
    """批量向知识库添加知识"""
    success_count = 0
    fail_count = 0
    
    for item in knowledge_list:
        try:
            success = await rag_service.add_knowledge(
                content=item.content,
                content_type=item.content_type,
                metadata={"category": item.category} if item.category else None
            )
            if success:
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            logger.error(f"批量添加知识失败: {e}")
            fail_count += 1
    
    return {
        "success": True,
        "message": f"批量添加完成：成功 {success_count} 条，失败 {fail_count} 条",
        "success_count": success_count,
        "fail_count": fail_count
    }
