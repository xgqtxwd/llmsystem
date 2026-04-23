import json
import httpx
from typing import Optional, Dict, Any, List
from app.config import settings
from app.services.vector_service import VectorDatabase, EmbeddingService, VisionService
import logging

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.vector_db = VectorDatabase(settings.VECTOR_DATABASE_URL)
        self.embedding_service = EmbeddingService(
            api_key=settings.DASHSCOPE_API_KEY,
            model=settings.EMBEDDING_MODEL
        )
        self.llm_api_key = settings.LLM_API_KEY
        self.llm_api_url = settings.LLM_API_URL
        self.llm_model = settings.LLM_MODEL_NAME
        self._init_default_knowledge()
    
    def _init_default_knowledge(self):
        """初始化默认知识库"""
        try:
            count = self.vector_db.count_vectors()
            if count == 0:
                self._seed_initial_knowledge()
        except Exception as e:
            logger.warning(f"知识库初始化检查失败: {e}")
    
    def _seed_initial_knowledge(self):
        """填充初始营养知识"""
        initial_knowledge = [
            # 营养知识
            {"content": "蛋白质是构成人体组织的基本物质，每克蛋白质提供4千卡热量。优质蛋白质来源包括肉类、鱼类、蛋类、奶制品和豆制品。", "type": "nutrition", "category": "蛋白质"},
            {"content": "碳水化合物是人体主要能量来源，每克碳水化合物提供4千卡热量。建议占总能量的45%-65%。", "type": "nutrition", "category": "碳水化合物"},
            {"content": "脂肪是重要的能量储备，每克脂肪提供9千卡热量。适量摄入健康脂肪有助于维持细胞功能和激素平衡。", "type": "nutrition", "category": "脂肪"},
            {"content": "膳食纤维有助于肠道健康，推荐每日摄入25-30克。富含纤维的食物包括全谷物、蔬菜和水果。", "type": "nutrition", "category": "膳食纤维"},
            {"content": "维生素和矿物质是维持身体正常功能所必需的微量营养素，需要通过均衡饮食来获取。", "type": "nutrition", "category": "维生素和矿物质"},
            
            # 食谱
            {"content": "早餐推荐：全麦面包+鸡蛋+牛奶+水果。营养均衡，适合控制体重人群。", "type": "recipe", "category": "早餐", "meal_type": "breakfast", "calories": 450, "protein": 20, "difficulty": "简单"},
            {"content": "午餐推荐：糙米饭+清蒸鱼+西兰花+番茄蛋花汤。富含优质蛋白和膳食纤维。", "type": "recipe", "category": "午餐", "meal_type": "lunch", "calories": 650, "protein": 35, "difficulty": "中等"},
            {"content": "晚餐推荐：荞麦面+鸡胸肉+凉拌蔬菜。低脂低热量，适合减肥人群。", "type": "recipe", "category": "晚餐", "meal_type": "dinner", "calories": 500, "protein": 30, "difficulty": "简单"},
            {"content": "加餐推荐：坚果+酸奶。提供健康脂肪和蛋白质，适合运动前后食用。", "type": "recipe", "category": "加餐", "meal_type": "snack", "calories": 200, "protein": 8, "difficulty": "简单"},
            
            # 食材
            {"content": "鸡胸肉是高蛋白低脂肪的健康食材，每100克含31克蛋白质，适合增肌和减脂人群。", "type": "ingredient", "category": "肉类", "season": "全年"},
            {"content": "三文鱼富含Omega-3脂肪酸，对心血管健康有益，每100克含20克优质蛋白。", "type": "ingredient", "category": "鱼类", "season": "全年"},
            {"content": "西兰花是营养密度最高的蔬菜之一，富含维生素C、维生素K和膳食纤维。", "type": "ingredient", "category": "蔬菜", "season": "冬季"},
            {"content": "糙米是全谷物，富含B族维生素和膳食纤维，升糖指数低于白米饭。", "type": "ingredient", "category": "谷物", "season": "全年"},
            {"content": "鸡蛋是完美的营养食品，富含优质蛋白和多种维生素，每个约含6克蛋白质。", "type": "ingredient", "category": "蛋类", "season": "全年"},
            
            # 饮食建议
            {"content": "减肥期间应控制每日热量摄入在基础代谢的1.2-1.5倍，同时保证蛋白质摄入。", "type": "advice", "category": "减肥"},
            {"content": "增肌人群需要每日摄入1.6-2.2克/公斤体重的蛋白质，并配合适量力量训练。", "type": "advice", "category": "增肌"},
            {"content": "控糖饮食应选择低升糖指数食物，避免精制糖和精制碳水化合物。", "type": "advice", "category": "控糖"},
            {"content": "健康人群应保持均衡饮食，多样化摄入各类食物，避免偏食和暴饮暴食。", "type": "advice", "category": "健康维持"},
            
            # 季节性
            {"content": "春季宜吃清淡蔬菜，如菠菜、油菜、芹菜等，可清肝火。", "type": "seasonal", "category": "春季"},
            {"content": "夏季宜吃清热解暑食物，如西瓜、黄瓜、苦瓜、绿豆汤等。", "type": "seasonal", "category": "夏季"},
            {"content": "秋季宜吃润燥食物，如梨、百合、银耳、蜂蜜等，可润肺止咳。", "type": "seasonal", "category": "秋季"},
            {"content": "冬季宜吃温热食物，如羊肉、核桃、红薯、姜汤等，可驱寒保暖。", "type": "seasonal", "category": "冬季"},
        ]
        
        for item in initial_knowledge:
            try:
                embedding = self.embedding_service.get_embedding(item["content"])
                self.vector_db.insert_vector(
                    content=item["content"],
                    embedding=embedding,
                    content_type=item["type"],
                    metadata=item.get("category")
                )
            except Exception as e:
                logger.warning(f"知识入库失败: {e}")
    
    async def generate_recipe_with_rag(
        self,
        user_context: Dict[str, Any],
        meal_type: Optional[str] = None,
        available_ingredients: Optional[List[str]] = None
    ) -> str:
        """使用RAG技术生成食谱"""
        # 构建检索查询
        query_parts = []
        if meal_type:
            query_parts.append(f"{meal_type}食谱")
        if user_context.get("goal_type"):
            query_parts.append(f"{user_context['goal_type']}饮食建议")
        if user_context.get("diet_type"):
            query_parts.append(f"{user_context['diet_type']}")
        
        if available_ingredients:
            query_parts.append(", ".join(available_ingredients))
        
        query = "，".join(query_parts) if query_parts else "营养均衡的食谱"
        
        # 检索相关知识
        context_docs = self.retrieve_knowledge(query, top_k=5)
        
        # 构建提示词
        system_prompt = self._build_recipe_system_prompt(user_context, meal_type)
        
        user_message = f"""基于以下背景信息和知识库内容，请推荐一个合适的食谱：

【用户背景信息】
{self._format_user_context(user_context)}

【可用食材】
{', '.join(available_ingredients) if available_ingredients else '无特定要求'}

【餐次类型】
{meal_type or '不限'}

【知识库检索结果】
{self._format_context_docs(context_docs)}

请提供：
1. 食谱名称
2. 所需食材及用量
3. 烹饪步骤
4. 营养价值分析
5. 适合人群说明"""

        # 调用LLM生成
        result = await self._call_llm(system_prompt, user_message)
        
        return result
    
    async def generate_nutrition_advice_with_rag(
        self,
        user_context: Dict[str, Any],
        question: str
    ) -> str:
        """使用RAG技术回答营养问题"""
        # 检索相关知识
        context_docs = self.retrieve_knowledge(question, top_k=5)
        
        # 构建提示词
        system_prompt = """你是一位专业的营养顾问助手。根据知识库中的营养知识和用户的问题，提供科学准确的营养建议。

回答要求：
1. 基于检索到的知识库内容进行回答
2. 回答应该简洁明了，控制在200字以内
3. 如果用户的问题涉及医疗诊断，请建议用户咨询专业医生"""

        user_message = f"""【用户问题】
{question}

【用户背景】
{self._format_user_context(user_context)}

【相关知识库内容】
{self._format_context_docs(context_docs)}

请根据以上内容回答用户的问题。"""

        # 调用LLM生成
        result = await self._call_llm(system_prompt, user_message)
        
        return result
    
    def retrieve_knowledge(self, query: str, content_type: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """检索知识库"""
        try:
            # 获取查询的嵌入向量
            query_embedding = self.embedding_service.get_embedding(query)
            
            # 搜索相似内容
            results = self.vector_db.search_similar(
                query_embedding=query_embedding,
                content_type=content_type,
                top_k=top_k
            )
            
            return results
        except Exception as e:
            logger.error(f"知识检索失败: {e}")
            return []
    
    def add_knowledge(
        self,
        content: str,
        content_type: str,
        metadata: Optional[Dict] = None,
        embedding: Optional[List[float]] = None
    ) -> bool:
        """添加知识到向量库"""
        try:
            if embedding is None:
                result = self.embedding_service.get_embedding(content)
                if result.get("success"):
                    embedding = result["embedding"]
                else:
                    logger.error(f"获取embedding失败: {result.get('error')}")
                    return False

            self.vector_db.insert_vector(
                content=content,
                embedding=embedding,
                content_type=content_type,
                metadata=metadata
            )
            return True
        except Exception as e:
            logger.error(f"知识添加失败: {e}")
            return False
    
    def get_all_knowledge(self, content_type: Optional[str] = None, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """获取所有知识"""
        if content_type:
            return self.vector_db.get_all_by_type(content_type)
        else:
            offset = (page - 1) * page_size
            return self.vector_db.get_all(limit=page_size, offset=offset)
    
    def delete_knowledge(self, knowledge_id: int) -> bool:
        """删除知识"""
        try:
            self.vector_db.delete_vector(knowledge_id)
            return True
        except Exception as e:
            logger.error(f"知识删除失败: {e}")
            return False
    
    def get_knowledge_stats(self) -> Dict[str, int]:
        """获取知识库统计"""
        types = ["nutrition", "recipe", "ingredient", "advice", "seasonal"]
        stats = {}
        for t in types:
            stats[t] = self.vector_db.count_vectors(t)
        stats["total"] = self.vector_db.count_vectors()
        return stats
    
    def _build_recipe_system_prompt(self, user_context: Dict, meal_type: Optional[str]) -> str:
        """构建食谱生成的系统提示"""
        prompt = """你是一位专业的食谱推荐师。根据用户的健康状况、饮食偏好和目标，结合知识库中的食谱和营养知识，推荐合适的食谱。

请提供详细的食谱信息，包括：
1. 食谱名称
2. 所需食材及用量（注意考虑用户是否有禁忌食材）
3. 烹饪步骤
4. 营养价值分析
5. 适合人群

请用友好的方式回答，控制在300字以内。"""
        return prompt
    
    def _format_user_context(self, context: Dict) -> str:
        """格式化用户背景信息"""
        parts = []
        if context.get("age"):
            parts.append(f"年龄：{context['age']}岁")
        if context.get("gender"):
            parts.append(f"性别：{context['gender']}")
        if context.get("height") and context.get("weight"):
            parts.append(f"身高：{context['height']}cm，体重：{context['weight']}kg")
        if context.get("bmi"):
            parts.append(f"BMI：{context['bmi']}")
        if context.get("goal_type"):
            goal_map = {"weight_loss": "减肥", "muscle_gain": "增肌", "blood_sugar_control": "控糖", "health_maintenance": "健康维持"}
            parts.append(f"健康目标：{goal_map.get(context['goal_type'], context['goal_type'])}")
        if context.get("taste_preference"):
            parts.append(f"口味偏好：{context['taste_preference']}")
        if context.get("diet_type"):
            parts.append(f"饮食类型：{context['diet_type']}")
        if context.get("allergies"):
            parts.append(f"过敏食物：{context['allergies']}")
        if context.get("forbidden_foods"):
            parts.append(f"禁忌食物：{context['forbidden_foods']}")
        
        return "；".join(parts) if parts else "用户尚未设置健康档案"
    
    def _format_context_docs(self, docs: List[Dict]) -> str:
        """格式化检索到的文档"""
        if not docs:
            return "无相关内容"
        
        formatted = []
        for i, doc in enumerate(docs, 1):
            similarity = doc.get("similarity", 0)
            content = doc.get("content", "")
            formatted.append(f"{i}. [{similarity:.2f}] {content}")
        
        return "\n".join(formatted)
    
    async def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """调用LLM生成回答"""
        headers = {
            "Authorization": f"Bearer {self.llm_api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        payload = {
            "model": self.llm_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.llm_api_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    return f"抱歉，暂时无法生成回答。请稍后重试。"
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return f"抱歉，处理您的请求时发生错误。请稍后重试。"


# 全局RAG服务实例
rag_service = RAGService()
