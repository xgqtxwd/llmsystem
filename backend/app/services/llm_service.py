import json
import httpx
from typing import Optional, Dict, Any
from app.config import settings
from app.runtime_config import ConfigAccessor
import logging

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.max_retries = 2
        self.timeout = httpx.Timeout(60.0, connect=15.0)

    def _get_api_key(self) -> str:
        return ConfigAccessor.get_llm_api_key()

    def _get_api_url(self) -> str:
        return ConfigAccessor.get_llm_api_url()

    def _get_model_name(self) -> str:
        return ConfigAccessor.get_llm_model_name()

    def _get_temperature(self) -> float:
        return ConfigAccessor.get_llm_temperature()

    def _get_max_tokens(self) -> int:
        return ConfigAccessor.get_llm_max_tokens()

    def _get_top_p(self) -> float:
        return ConfigAccessor.get_llm_top_p()

    async def chat_completion(
        self,
        messages: list,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        api_key = self._get_api_key()
        api_url = self._get_api_url()
        model_name = self._get_model_name()

        temp = temperature if temperature is not None else self._get_temperature()
        tokens = max_tokens if max_tokens is not None else self._get_max_tokens()

        logger.info(f"LLM API URL: {api_url}/chat/completions")
        logger.info(f"LLM Model: {model_name}")
        logger.info(f"Request messages: {messages}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)
        
        logger.info(f"Formatted messages: {formatted_messages}")

        payload = {
            "model": model_name,
            "messages": formatted_messages,
            "temperature": temp,
            "max_tokens": tokens,
            "top_p": self._get_top_p()
        }
        
        logger.info(f"Calling LLM API...")

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{api_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    
                    logger.info(f"Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"LLM response: {result}")
                        return {
                            "success": True,
                            "content": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                            "usage": result.get("usage", {})
                        }
                    elif response.status_code == 401:
                        return {
                            "success": False,
                            "error": "API密钥无效"
                        }
                    else:
                        error_detail = response.text
                        logger.error(f"API error: {response.status_code}, {error_detail}")
                        return {
                            "success": False,
                            "error": f"API请求失败: {response.status_code}, {error_detail}"
                        }
                        
            except httpx.TimeoutException:
                logger.error("Request timeout")
                return {
                    "success": False,
                    "error": "请求超时，请稍后重试"
                }
            except Exception as e:
                logger.error(f"Request exception: {e}")
                return {
                    "success": False,
                    "error": f"请求异常: {str(e)}"
                }
        
        return {
            "success": False,
            "error": "请求失败，请稍后重试"
        }

    async def generate_nutrition_advice(
        self,
        user_context: Dict[str, Any],
        question: str
    ) -> str:
        system_prompt = """你是一位专业的营养顾问助手。你的职责是：
1. 根据用户的健康状况和饮食偏好，提供科学的营养建议
2. 回答关于营养成分、食物搭配、健康饮食等问题
3. 提供个性化的饮食建议
4. 纠正用户存在的饮食误区

请用友好、专业的方式回答用户的问题。回答应该简洁明了，控制在200字以内。
如果用户的问题涉及医疗诊断，请建议用户咨询专业医生。"""

        context_info = self._build_user_context(user_context)
        
        messages = [
            {"role": "user", "content": f"用户背景信息：{context_info}\n\n用户问题：{question}"}
        ]

        result = await self.chat_completion(messages, system_prompt)
        
        if result["success"]:
            return result["content"]
        else:
            return f"抱歉，现在无法回答您的问题。请稍后重试。"

    async def generate_recipe_recommendation(
        self,
        user_context: Dict[str, Any],
        meal_type: Optional[str] = None
    ) -> str:
        system_prompt = """你是一位专业的食谱推荐师。根据用户的健康状况、饮食偏好和目标，推荐合适的食谱。
请提供详细的食谱信息，包括：
1. 食谱名称
2. 所需食材
3. 烹饪步骤
4. 营养价值分析
5. 适合人群

请用友好的方式回答。"""

        context_info = self._build_user_context(user_context)
        
        if meal_type:
            context_info += f"\n餐次类型：{meal_type}"
        
        messages = [
            {"role": "user", "content": f"用户背景信息：{context_info}\n\n请根据以上信息推荐一个合适的食谱。"}
        ]

        result = await self.chat_completion(messages, system_prompt)
        
        if result["success"]:
            return result["content"]
        else:
            return "抱歉，暂时无法为您推荐食谱。请稍后重试。"

    def _build_user_context(self, user_context: Dict[str, Any]) -> str:
        context_parts = []
        
        if user_context.get("age"):
            context_parts.append(f"年龄：{user_context['age']}岁")
        if user_context.get("gender"):
            context_parts.append(f"性别：{user_context['gender']}")
        if user_context.get("height") and user_context.get("weight"):
            context_parts.append(f"身高：{user_context['height']}cm，体重：{user_context['weight']}kg")
        if user_context.get("bmi"):
            context_parts.append(f"BMI：{user_context['bmi']}")
        if user_context.get("activity_level"):
            context_parts.append(f"活动水平：{user_context['activity_level']}")
        if user_context.get("goal_type"):
            context_parts.append(f"健康目标：{user_context['goal_type']}")
        if user_context.get("taste_preference"):
            context_parts.append(f"口味偏好：{user_context['taste_preference']}")
        if user_context.get("diet_type"):
            context_parts.append(f"饮食类型：{user_context['diet_type']}")
        if user_context.get("allergies"):
            context_parts.append(f"过敏食物：{user_context['allergies']}")
        if user_context.get("forbidden_foods"):
            context_parts.append(f"禁忌食物：{user_context['forbidden_foods']}")
        
        if not context_parts:
            return "用户尚未设置健康档案"
        
        return "；".join(context_parts)


llm_service = LLMService()
