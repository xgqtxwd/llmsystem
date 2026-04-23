import numpy as np
from sqlalchemy import create_engine, text
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class VectorDatabase:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self._init_tables()
    
    def _init_tables(self):
        """初始化向量数据库表"""
        with self.engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS knowledge_vectors CASCADE"))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS knowledge_vectors (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    content_type VARCHAR(50),
                    metadata TEXT,
                    embedding TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_content_type 
                ON knowledge_vectors(content_type)
            """))
            
            conn.commit()
            logger.info("向量数据库表初始化完成")
    
    def insert_vector(self, content: str, embedding: List[float], 
                     content_type: str = "general", metadata: Optional[Dict] = None) -> int:
        """插入向量数据"""
        embedding_str = json.dumps(embedding)
        metadata_str = json.dumps(metadata) if metadata else None
        
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO knowledge_vectors (content, content_type, metadata, embedding)
                    VALUES (:content, :content_type, :metadata, :embedding)
                    RETURNING id
                """),
                {
                    "content": content,
                    "content_type": content_type,
                    "metadata": metadata_str,
                    "embedding": embedding_str
                }
            )
            conn.commit()
            return result.fetchone()[0]
    
    def search_similar(self, query_embedding: List[float], 
                      content_type: Optional[str] = None,
                      top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似向量"""
        query_embedding_str = json.dumps(query_embedding)
        
        with self.engine.connect() as conn:
            if content_type:
                sql = text("""
                    SELECT id, content, content_type, metadata, embedding,
                           1 - ((embedding::jsonb) <=> (:embedding::jsonb)) as similarity
                    FROM knowledge_vectors
                    WHERE content_type = :content_type
                    ORDER BY (embedding::jsonb) <=> (:embedding::jsonb)
                    LIMIT :top_k
                """)
                params = {
                    "embedding": query_embedding_str,
                    "content_type": content_type,
                    "top_k": top_k
                }
            else:
                sql = text("""
                    SELECT id, content, content_type, metadata, embedding,
                           1 - ((embedding::jsonb) <=> (:embedding::jsonb)) as similarity
                    FROM knowledge_vectors
                    ORDER BY (embedding::jsonb) <=> (:embedding::jsonb)
                    LIMIT :top_k
                """)
                params = {
                    "embedding": query_embedding_str,
                    "top_k": top_k
                }
            
            result = conn.execute(sql, params)
            rows = result.fetchall()
            
            return [
                {
                    "id": row[0],
                    "content": row[1],
                    "content_type": row[2],
                    "metadata": json.loads(row[3]) if row[3] else None,
                    "similarity": float(row[4])
                }
                for row in rows
            ]
    
    def get_all_by_type(self, content_type: str) -> List[Dict[str, Any]]:
        """获取指定类型的所有内容"""
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, content, content_type, metadata, created_at
                    FROM knowledge_vectors
                    WHERE content_type = :content_type
                    ORDER BY created_at DESC
                """),
                {"content_type": content_type}
            )
            rows = result.fetchall()

            return [
                {
                    "id": row[0],
                    "content": row[1],
                    "content_type": row[2],
                    "metadata": json.loads(row[3]) if row[3] else None,
                    "created_at": row[4]
                }
                for row in rows
            ]

    def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取所有向量知识（分页）"""
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, content, content_type, metadata, created_at
                    FROM knowledge_vectors
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                """),
                {"limit": limit, "offset": offset}
            )
            rows = result.fetchall()

            return [
                {
                    "id": row[0],
                    "content": row[1],
                    "content_type": row[2],
                    "metadata": json.loads(row[3]) if row[3] else None,
                    "created_at": row[4]
                }
                for row in rows
            ]
    
    def delete_vector(self, vector_id: int) -> bool:
        """删除向量"""
        with self.engine.connect() as conn:
            conn.execute(
                text("DELETE FROM knowledge_vectors WHERE id = :id"),
                {"id": vector_id}
            )
            conn.commit()
            return True
    
    def count_vectors(self, content_type: Optional[str] = None) -> int:
        """统计向量数量"""
        with self.engine.connect() as conn:
            if content_type:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM knowledge_vectors WHERE content_type = :content_type"),
                    {"content_type": content_type}
                )
            else:
                result = conn.execute(text("SELECT COUNT(*) FROM knowledge_vectors"))
            return result.fetchone()[0]


class EmbeddingService:
    def __init__(self, api_key: str, model: str = "text-embedding-v4"):
        import dashscope
        dashscope.api_key = api_key
        self.model = model
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的嵌入向量"""
        from dashscope import TextEmbedding
        
        response = TextEmbedding.call(
            model=self.model,
            input=text,
            dimension=1024
        )
        
        if response.status_code == 200:
            return response.output['embeddings'][0]['embedding']
        else:
            raise Exception(f"Embedding调用失败: {response.code} - {response.message}")
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量获取嵌入向量"""
        from dashscope import TextEmbedding
        
        response = TextEmbedding.call(
            model=self.model,
            input=texts,
            dimension=1024
        )
        
        if response.status_code == 200:
            return [item['embedding'] for item in response.output['embeddings']]
        else:
            raise Exception(f"Embedding调用失败: {response.code} - {response.message}")


class VisionService:
    def __init__(self, api_key: str, model: str = "qwen-vl-plus"):
        import dashscope
        dashscope.api_key = api_key
        self.model = model
    
    def analyze_image(self, image_url: str, prompt: str = None) -> Dict[str, Any]:
        """分析图片内容"""
        from dashscope import MultiModalConversation
        from dashscope.api_entities import File
        
        if not prompt:
            prompt = "请识别图片中的食材，列出所有可见的食物原材料名称和数量"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"image": File.from_url(image_url)},
                    {"text": prompt}
                ]
            }
        ]
        
        response = MultiModalConversation.call(
            model=self.model,
            messages=messages
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "content": response.output.choices[0].message.content[0]["text"]
            }
        else:
            return {
                "success": False,
                "error": f"图像识别失败: {response.code} - {response.message}"
            }
    
    def analyze_image_base64(self, image_base64: str, prompt: str = None) -> Dict[str, Any]:
        """分析Base64编码的图片"""
        from dashscope import MultiModalConversation
        
        if not prompt:
            prompt = "请识别图片中的食材，列出所有可见的食物原材料名称和数量"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"image": f"data:image/jpeg;base64,{image_base64}"},
                    {"text": prompt}
                ]
            }
        ]
        
        response = MultiModalConversation.call(
            model=self.model,
            messages=messages
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "content": response.output.choices[0].message.content[0]["text"]
            }
        else:
            return {
                "success": False,
                "error": f"图像识别失败: {response.code} - {response.message}"
            }
