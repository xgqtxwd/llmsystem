from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
import base64
import json
import threading
import logging
from app.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.utils import get_current_user
from app.config import settings
from app.services.vector_service import EmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["管理员"])

upload_tasks: Dict[str, dict] = {}
task_lock = threading.Lock()


def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


@router.get("/users", summary="获取所有用户列表")
async def get_all_users(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    query = db.query(User)
    total = query.count()
    offset = (page - 1) * page_size
    users = query.offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "users": [UserResponse.model_validate(u) for u in users]
    }


@router.get("/users/{user_id}", summary="获取用户详情")
async def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}/role", summary="修改用户角色")
async def update_user_role(
    user_id: int,
    is_admin: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    user.is_admin = is_admin
    db.commit()
    db.refresh(user)

    return {"message": "用户角色已更新", "user": UserResponse.model_validate(user)}


@router.delete("/users/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    db.delete(user)
    db.commit()

    return {"message": "用户已删除"}


@router.get("/stats/overview", summary="系统概览统计")
async def get_system_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    total_users = db.query(User).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()

    return {
        "total_users": total_users,
        "admin_users": admin_users,
        "regular_users": total_users - admin_users
    }


@router.get("/stats/activity", summary="用户活跃度统计")
async def get_user_activity_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    mock_data = {
        "daily_active_users": 128,
        "weekly_active_users": 456,
        "monthly_active_users": 1234,
        "retention_rate": 68.5,
        "avg_session_duration": "15.5分钟",
        "total_conversations": 5678,
        "today_new_users": 23
    }
    return mock_data


@router.get("/stats/behavior", summary="用户行为分析")
async def get_user_behavior_analysis(
    current_user: User = Depends(require_admin)
):
    mock_data = {
        "feature_usage": [
            {"feature": "营养咨询", "usage_count": 3456, "percentage": 35},
            {"feature": "食谱推荐", "usage_count": 2345, "percentage": 24},
            {"feature": "食材识别", "usage_count": 1890, "percentage": 19},
            {"feature": "季节推荐", "usage_count": 1234, "percentage": 12},
            {"feature": "知识库", "usage_count": 890, "percentage": 9}
        ],
        "avg_interactions_per_user": 8.5,
        "preferred_meal_times": [
            {"time": "早餐 7-9点", "percentage": 30},
            {"time": "午餐 11-13点", "percentage": 35},
            {"time": "晚餐 17-19点", "percentage": 25},
            {"time": "其他时间", "percentage": 10}
        ]
    }
    return mock_data


@router.get("/feedbacks", summary="获取用户反馈列表")
async def get_user_feedbacks(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_admin)
):
    mock_feedbacks = [
        {"id": 1, "user_id": 101, "username": "用户A", "content": "希望增加更多的减肥食谱", "created_at": "2024-03-15 10:30", "status": "待处理"},
        {"id": 2, "user_id": 102, "username": "用户B", "content": "食材识别功能很好用！", "created_at": "2024-03-14 15:20", "status": "已处理"},
        {"id": 3, "user_id": 103, "username": "用户C", "content": "建议增加离线使用功能", "created_at": "2024-03-13 09:45", "status": "处理中"},
        {"id": 4, "user_id": 104, "username": "用户D", "content": "界面可以更简洁一些", "created_at": "2024-03-12 14:30", "status": "待处理"},
        {"id": 5, "user_id": 105, "username": "用户E", "content": "希望增加运动建议功能", "created_at": "2024-03-11 11:15", "status": "已处理"},
    ]
    return {
        "total": len(mock_feedbacks),
        "page": page,
        "feedbacks": mock_feedbacks[(page-1)*page_size: page*page_size]
    }


@router.post("/feedbacks/{feedback_id}/process", summary="处理用户反馈")
async def process_feedback(
    feedback_id: int,
    status: str,
    response: str,
    current_user: User = Depends(require_admin)
):
    return {"message": "反馈已处理", "feedback_id": feedback_id, "status": status}


@router.get("/settings/llm", summary="获取LLM设置")
async def get_llm_settings(current_user: User = Depends(require_admin)):
    return {
        "model_name": settings.LLM_MODEL_NAME,
        "temperature": 0.7,
        "max_tokens": 500,
        "embedding_model": settings.EMBEDDING_MODEL
    }


@router.put("/settings/llm", summary="更新LLM设置")
async def update_llm_settings(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    current_user: User = Depends(require_admin)
):
    return {
        "message": "LLM设置已更新",
        "settings": {
            "model_name": model_name or settings.LLM_MODEL_NAME,
            "temperature": temperature or 0.7,
            "max_tokens": max_tokens or 500
        }
    }


@router.get("/settings/embedding", summary="获取Embedding设置")
async def get_embedding_settings(current_user: User = Depends(require_admin)):
    return {
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_dimension": settings.EMBEDDING_DIMENSION,
        "chunk_methods": ["固定大小分块", "句子分块", "段落分块", "递归分块"],
        "current_chunk_method": "固定大小分块"
    }


@router.put("/settings/embedding", summary="更新Embedding设置")
async def update_embedding_settings(
    embedding_model: Optional[str] = None,
    chunk_method: Optional[str] = None,
    current_user: User = Depends(require_admin)
):
    return {
        "message": "Embedding设置已更新",
        "settings": {
            "embedding_model": embedding_model or settings.EMBEDDING_MODEL,
            "chunk_method": chunk_method or "固定大小分块"
        }
    }


@router.get("/logs", summary="获取系统日志")
async def get_system_logs(
    page: int = 1,
    page_size: int = 50,
    level: Optional[str] = None,
    current_user: User = Depends(require_admin)
):
    mock_logs = [
        {"id": 1, "timestamp": "2024-03-15 14:30:25", "level": "INFO", "module": "auth", "message": "用户登录成功: user_001"},
        {"id": 2, "timestamp": "2024-03-15 14:28:10", "level": "ERROR", "module": "llm_service", "message": "LLM API请求超时"},
        {"id": 3, "timestamp": "2024-03-15 14:25:00", "level": "WARNING", "module": "vector_service", "message": "向量数据库连接延迟较高"},
        {"id": 4, "timestamp": "2024-03-15 14:20:15", "level": "INFO", "module": "recipes", "message": "季节推荐请求成功"},
        {"id": 5, "timestamp": "2024-03-15 14:15:30", "level": "INFO", "module": "knowledge", "message": "知识库检索成功"},
    ]

    filtered_logs = mock_logs
    if level:
        filtered_logs = [log for log in mock_logs if log["level"] == level.upper()]

    return {
        "total": len(filtered_logs),
        "page": page,
        "logs": filtered_logs[(page-1)*page_size: page*page_size]
    }


MAX_FILE_SIZE = 30 * 1024 * 1024

EMBEDDING_MODELS = {
    "text-embedding-v4": {
        "name": "DashScope Text Embedding V4",
        "dimension": 1536,
        "api_type": "dashscope"
    },
    "text-embedding-3-large": {
        "name": "OpenAI Embedding 3 Large",
        "dimension": 3072,
        "api_type": "openai"
    }
}

CHUNK_METHODS_CONFIG = {
    "fixed": {"name": "固定大小分块", "chunk_size": 500, "overlap": 50},
    "sentence": {"name": "句子分块", "delimiter": "。！？"},
    "paragraph": {"name": "段落分块", "delimiter": "\n\n"},
    "recursive": {"name": "递归分块", "separators": ["\n\n", "\n", "。", "！", "？"]}
}


@router.get("/document/parse-options", summary="获取文档解析选项")
async def get_document_parse_options(current_user: User = Depends(require_admin)):
    return {
        "chunk_methods": [
            {"value": "fixed", "label": "固定大小分块", "description": "按固定字符数分割文本"},
            {"value": "sentence", "label": "句子分块", "description": "按句子分隔符分割"},
            {"value": "paragraph", "label": "段落分块", "description": "按段落分割"},
            {"value": "recursive", "label": "递归分块", "description": "递归使用多种分隔符"}
        ],
        "embedding_models": [
            {"value": "text-embedding-v4", "label": "DashScope Text Embedding V4"},
            {"value": "text-embedding-3-large", "label": "OpenAI Embedding 3 Large"}
        ]
    }


@router.post("/document/upload", summary="上传并解析文档")
async def upload_document(
    file: UploadFile = File(...),
    chunk_method: str = Query("fixed", description="分块方式"),
    embedding_model: str = Query("text-embedding-v4", description="嵌入模型"),
    content_type: str = Query("nutrition", description="知识类型"),
    category: str = Query("general", description="分类"),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(require_admin)
):
    if not file.filename.endswith(('.pdf', '.docx', '.doc', '.txt', '.md')):
        return {"success": False, "error": "只支持 PDF、Word、TXT、Markdown 文档"}

    file_content = await file.read()
    file_size = len(file_content)

    if file_size > MAX_FILE_SIZE:
        return {"success": False, "error": f"文件大小不能超过 {MAX_FILE_SIZE // (1024 * 1024)}MB"}

    if file_size == 0:
        return {"success": False, "error": "文件内容为空"}

    try:
        if file.filename.endswith('.pdf'):
            text = await extract_pdf_text(file_content)
        elif file.filename.endswith(('.docx', '.doc')):
            text = await extract_word_text(file_content)
        elif file.filename.endswith(('.txt', '.md')):
            text = file_content.decode('utf-8', errors='ignore')
        else:
            text = ""

        if not text.strip():
            return {"success": False, "error": "文档内容为空或无法解析"}

        chunks = chunk_text(text, chunk_method)

        if not chunks:
            return {"success": False, "error": "文档分块失败"}

        import uuid
        task_id = str(uuid.uuid4())[:8]

        with task_lock:
            upload_tasks[task_id] = {
                "status": "processing",
                "filename": file.filename,
                "file_size": file_size,
                "total_chunks": len(chunks),
                "processed_chunks": 0,
                "stored_count": 0,
                "errors": [],
                "message": "正在处理中...",
                "chunk_preview": [
                    {
                        "index": i,
                        "content": chunk[:300] + ("..." if len(chunk) > 300 else ""),
                        "length": len(chunk)
                    }
                    for i, chunk in enumerate(chunks[:15])
                ],
                "full_text_length": len(text),
                "chunk_method": chunk_method
            }

        background_tasks.add_task(
            process_document_task,
            task_id,
            chunks,
            embedding_model,
            content_type,
            category,
            file.filename
        )

        return {
            "success": True,
            "task_id": task_id,
            "filename": file.filename,
            "file_size": file_size,
            "total_chunks": len(chunks),
            "message": "文档已提交处理，请使用任务ID查询进度"
        }
    except Exception as e:
        logger.error(f"文档解析失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": f"文档解析失败: {str(e)}"}


def process_document_task(task_id: str, chunks: List[str], embedding_model: str, content_type: str, category: str, filename: str):
    from app.services.rag_service import rag_service as rag_svc

    embedding_service = EmbeddingService(
        api_key=settings.DASHSCOPE_API_KEY,
        model=embedding_model
    )

    batch_size = 5
    total_chunks = len(chunks)
    processed = 0
    stored = 0
    errors = []

    try:
        for batch_start in range(0, len(chunks), batch_size):
            batch_end = min(batch_start + batch_size, len(chunks))
            batch_chunks = chunks[batch_start:batch_end]

            try:
                texts_for_embedding = [c for c in batch_chunks if c.strip()]
                if not texts_for_embedding:
                    continue

                results = embedding_service.get_embeddings(texts_for_embedding)

                for i, (chunk, embedding) in enumerate(zip(texts_for_embedding, results)):
                    if embedding and isinstance(embedding, list):
                        chunk_index = batch_start + i
                        metadata = {
                            "filename": filename,
                            "chunk_index": chunk_index,
                            "total_chunks": total_chunks,
                            "category": category,
                            "source": "document_upload"
                        }
                        rag_svc.add_knowledge(
                            content=chunk,
                            content_type=content_type,
                            metadata=metadata,
                            embedding=embedding
                        )
                        stored += 1
                    processed += 1

                with task_lock:
                    if task_id in upload_tasks:
                        upload_tasks[task_id]["processed_chunks"] = processed
                        upload_tasks[task_id]["stored_count"] = stored

            except Exception as e:
                logger.error(f"Batch embedding failed: {e}")
                errors.append(f"Batch {batch_start}: {str(e)}")
                processed += len(batch_chunks)

        with task_lock:
            if task_id in upload_tasks:
                upload_tasks[task_id]["status"] = "completed"
                upload_tasks[task_id]["processed_chunks"] = processed
                upload_tasks[task_id]["stored_count"] = stored
                upload_tasks[task_id]["errors"] = errors
                upload_tasks[task_id]["message"] = f"处理完成，已存储 {stored}/{total_chunks} 个文本块"

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        with task_lock:
            if task_id in upload_tasks:
                upload_tasks[task_id]["status"] = "failed"
                upload_tasks[task_id]["message"] = f"处理失败: {str(e)}"


@router.get("/document/task/{task_id}", summary="查询文档处理任务状态")
async def get_task_status(task_id: str, current_user: User = Depends(require_admin)):
    with task_lock:
        task = upload_tasks.get(task_id)

    if not task:
        return {"success": False, "error": "任务不存在"}

    result = {
        "success": True,
        "task_id": task_id,
        "status": task["status"],
        "filename": task["filename"],
        "file_size": task["file_size"],
        "total_chunks": task["total_chunks"],
        "processed_chunks": task["processed_chunks"],
        "stored_count": task["stored_count"],
        "progress": round(task["processed_chunks"] / task["total_chunks"] * 100, 1) if task["total_chunks"] > 0 else 0,
        "errors": task["errors"] if task["status"] in ["completed", "failed"] else None,
        "message": task["message"]
    }

    if task["status"] == "completed":
        result["chunk_preview"] = task.get("chunk_preview", [])
        result["full_text_length"] = task.get("full_text_length", 0)
        result["chunk_method"] = task.get("chunk_method", "")

    return result


@router.get("/document/tasks", summary="获取所有文档处理任务")
async def get_all_tasks(current_user: User = Depends(require_admin)):
    with task_lock:
        tasks = [
            {
                "task_id": tid,
                "status": t["status"],
                "filename": t["filename"],
                "total_chunks": t["total_chunks"],
                "stored_count": t["stored_count"],
                "message": t["message"]
            }
            for tid, t in upload_tasks.items()
        ]
    return {"success": True, "tasks": tasks}


@router.get("/document/chunks", summary="预览文档分块结果")
async def preview_document_chunks(
    file: UploadFile = File(...),
    chunk_method: str = Query("fixed", description="分块方式"),
    current_user: User = Depends(require_admin)
):
    if not file.filename.endswith(('.pdf', '.docx', '.doc', '.txt', '.md')):
        return {"success": False, "error": "只支持 PDF、Word、TXT、Markdown 文档"}

    file_content = await file.read()
    file_size = len(file_content)

    if file_size > MAX_FILE_SIZE:
        return {"success": False, "error": f"文件大小不能超过 {MAX_FILE_SIZE // (1024 * 1024)}MB"}

    try:
        if file.filename.endswith('.pdf'):
            text = await extract_pdf_text(file_content)
        elif file.filename.endswith(('.docx', '.doc')):
            text = await extract_word_text(file_content)
        elif file.filename.endswith(('.txt', '.md')):
            text = file_content.decode('utf-8', errors='ignore')
        else:
            text = ""

        chunks = chunk_text(text, chunk_method)

        preview_chunks = []
        for i, chunk in enumerate(chunks[:10]):
            preview_chunks.append({
                "index": i,
                "content": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                "length": len(chunk)
            })

        return {
            "success": True,
            "filename": file.filename,
            "total_chunks": len(chunks),
            "preview": preview_chunks
        }
    except Exception as e:
        logger.error(f"文档预览失败: {e}")
        return {"success": False, "error": f"文档预览失败: {str(e)}"}


async def extract_pdf_text(content: bytes) -> str:
    try:
        from PyPDF2 import PdfReader
        from io import BytesIO
        reader = PdfReader(BytesIO(content))
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"[第{page_num + 1}页]\n{page_text}\n"
        return text
    except ImportError:
        logger.error("PyPDF2 not installed")
        raise ImportError("请安装 PyPDF2: pip install PyPDF2")
    except Exception as e:
        logger.error(f"PDF解析失败: {e}")
        raise Exception(f"PDF解析失败: {str(e)}")


async def extract_word_text(content: bytes) -> str:
    try:
        from docx import Document
        from io import BytesIO
        doc = Document(BytesIO(content))
        text = ""
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
        return text
    except ImportError:
        logger.error("python-docx not installed")
        raise ImportError("请安装 python-docx: pip install python-docx")
    except Exception as e:
        logger.error(f"Word解析失败: {e}")
        raise Exception(f"Word解析失败: {str(e)}")


def chunk_text(text: str, method: str) -> List[str]:
    config = CHUNK_METHODS_CONFIG.get(method, CHUNK_METHODS_CONFIG["fixed"])

    if method == "fixed":
        return chunk_fixed(text, config.get("chunk_size", 500), config.get("overlap", 50))
    elif method == "sentence":
        return chunk_by_delimiter(text, config.get("delimiter", "。！？"))
    elif method == "paragraph":
        return chunk_by_delimiter(text, config.get("delimiter", "\n\n"))
    elif method == "recursive":
        return chunk_recursive(text, config.get("separators", ["\n\n", "\n", "。", "！", "？"]))
    else:
        return chunk_fixed(text, 500, 50)


def chunk_fixed(text: str, chunk_size: int, overlap: int) -> List[str]:
    if not text.strip():
        return []
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = start + chunk_size
        if end >= text_length:
            chunk = text[start:]
        else:
            chunk = text[start:end]
        cleaned = chunk.strip()
        if cleaned:
            chunks.append(cleaned)
        if end >= text_length:
            break
        start = end - overlap
    return chunks


def chunk_by_delimiter(text: str, delimiter: str) -> List[str]:
    if not text.strip():
        return []
    parts = text.split(delimiter)
    chunks = []
    current = ""
    current_length = 0
    max_chunk_size = 500

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(current) + len(part) + len(delimiter) <= max_chunk_size:
            current += part + delimiter
            current_length += len(part)
        else:
            if current:
                chunks.append(current.strip())
            if len(part) <= max_chunk_size:
                current = part + delimiter
            else:
                sub_chunks = chunk_fixed(part, max_chunk_size, 50)
                chunks.extend(sub_chunks[:-1] if len(sub_chunks) > 1 else [])
                current = sub_chunks[-1] + delimiter if sub_chunks else ""

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if c.strip()]


def chunk_recursive(text: str, separators: List[str]) -> List[str]:
    if not text.strip():
        return []

    def split_text(text: str, sep: str) -> tuple:
        parts = text.split(sep)
        return parts

    def recursive_chunk(text: str, index: int) -> List[str]:
        if index >= len(separators):
            if len(text) > 500:
                return chunk_fixed(text, 500, 50)
            elif text.strip():
                return [text.strip()]
            return []

        separator = separators[index]
        parts = split_text(text, separator)

        chunks = []
        current = ""
        max_size = 500

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if len(current) + len(separator) + len(part) <= max_size:
                current += part + separator
            else:
                if current.strip():
                    chunks.append(current.strip())
                if len(part) <= max_size:
                    current = part + separator
                else:
                    sub_chunks = recursive_chunk(part, index + 1)
                    chunks.extend(sub_chunks[:-1] if len(sub_chunks) > 1 else sub_chunks)
                    current = ""

        if current.strip():
            chunks.append(current.strip())

        return chunks

    return recursive_chunk(text, 0)
