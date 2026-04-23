from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import base64
import uuid
from app.database import get_db
from app.models import User, Recipe, RecipeIngredient, RecipeNutrition, Ingredient, IngredientNutrition
from app.schemas import RecipeResponse, IngredientResponse
from app.utils import get_current_user
from app.services.rag_service import rag_service
from app.services.vector_service import VisionService
from app.services.llm_service import LLMService
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recipes", tags=["食谱推荐"])

vision_service = VisionService(
    api_key=settings.VISION_LLM_API_KEY,
    model=settings.VISION_LLM_MODEL
)

llm_service = LLMService()


def _get_default_seasonal_recommendation(season: str) -> str:
    """获取默认的季节推荐"""
    recommendations = {
        "春季": "春季宜多吃新鲜蔬菜和水果，推荐食谱：蒜蓉西兰花、香菇炒青菜、山药红枣粥。饮食注意：少食酸，多食甘。",
        "夏季": "夏季宜清淡解暑，推荐食谱：凉拌黄瓜、冬瓜排骨汤、绿豆粥、西瓜苦瓜汁。饮食注意：多喝水，少食辛辣。",
        "秋季": "秋季宜润燥养肺，推荐食谱：银耳莲子羹、雪梨蜂蜜水、山药排骨汤、百合炒芹菜。饮食注意：少食辛辣，多食滋阴润燥食物。",
        "冬季": "冬季宜温补养生，推荐食谱：羊肉萝卜汤、红枣桂圆粥、生姜红糖水、核桃芝麻糊。饮食注意：多食温热食物，保暖防寒。"
    }
    return recommendations.get(season, "请根据季节特点选择合适的食谱，保持饮食均衡。")


@router.get("/", response_model=List[RecipeResponse], summary="获取食谱列表")
async def get_recipes(
    meal_type: Optional[str] = None,
    difficulty: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Recipe)
    
    if meal_type:
        query = query.filter(Recipe.meal_type == meal_type)
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    
    offset = (page - 1) * page_size
    recipes = query.offset(offset).limit(page_size).all()
    
    return [RecipeResponse.model_validate(recipe) for recipe in recipes]


@router.get("/recommend/ai", summary="AI智能推荐食谱（RAG）")
async def get_ai_recommended_recipes(
    meal_type: Optional[str] = None,
    available_ingredients: Optional[str] = None,
    season: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models import UserHealthProfile, UserDietPreference, UserHealthGoal
    
    user_context = {}
    
    profile = db.query(UserHealthProfile).filter(
        UserHealthProfile.user_id == current_user.id
    ).first()
    if profile:
        user_context["age"] = profile.age
        user_context["gender"] = profile.gender
        user_context["height"] = profile.height
        user_context["weight"] = profile.weight
        user_context["bmi"] = profile.bmi
    
    preference = db.query(UserDietPreference).filter(
        UserDietPreference.user_id == current_user.id
    ).first()
    if preference:
        user_context["diet_type"] = preference.diet_type
        user_context["taste_preference"] = preference.taste_preference
        user_context["allergies"] = preference.allergies
        user_context["forbidden_foods"] = preference.forbidden_foods
    
    goal = db.query(UserHealthGoal).filter(
        UserHealthGoal.user_id == current_user.id
    ).first()
    if goal:
        user_context["goal_type"] = goal.goal_type
        user_context["target_weight"] = goal.target_weight
    
    ingredients_list = None
    if available_ingredients:
        ingredients_list = [i.strip() for i in available_ingredients.split(",")]
    
    season_map = {
        "spring": "春季",
        "summer": "夏季", 
        "autumn": "秋季",
        "winter": "冬季"
    }
    chinese_season = season_map.get(season.lower(), season) if season else None
    
    try:
        if chinese_season:
            system_prompt = f"""你是一位专业的食谱推荐师。请根据季节特点推荐适合的食谱。
现在是{chinese_season}，请推荐适合这个季节的食谱，包括：
1. 适合这个季节的养生食物
2. 推荐食谱及其功效
3. 饮食注意事项

请用中文回复，内容简洁实用，控制在200字以内。"""

            logger.info("Calling LLM for seasonal recommendation...")
            result = await llm_service.chat_completion(
                messages=[{"role": "user", "content": f"请给我{chinese_season}的食谱推荐"}],
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=300
            )
            logger.info(f"LLM result: {result}")
            
            if result.get("success") and result.get("content"):
                recommendation = result["content"]
            else:
                recommendation = f"【{chinese_season}食谱推荐】\n\n" + _get_default_seasonal_recommendation(chinese_season)
        else:
            recommendation = await rag_service.generate_recipe_with_rag(
                user_context=user_context,
                meal_type=meal_type,
                available_ingredients=ingredients_list
            )
    except Exception as e:
        logger.error(f"RAG推荐失败: {e}")
        recommendation = "抱歉，暂时无法为您推荐食谱。请稍后重试。"
    
    response_data = {
        "recommendation": recommendation,
        "user_context": user_context,
        "meal_type": meal_type,
        "available_ingredients": ingredients_list,
        "season": chinese_season
    }
    logger.info(f"Response data: {response_data}")
    return response_data


@router.post("/recognize", summary="识别食材图片")
async def recognize_ingredients(
    image: UploadFile = File(None),
    image_url: str = Query(None, description="图片URL地址"),
    current_user: User = Depends(get_current_user)
):
    """通过视觉大模型识别食材图片并获取营养信息"""
    try:
        if not image and not image_url:
            return {"success": False, "error": "请提供图片文件或图片URL"}

        if image:
            image_content = await image.read()
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            result = vision_service.analyze_image_base64(
                image_base64=image_base64,
                prompt="请识别图片中的食材，并给出每种食材的营养信息（包括热量、蛋白质、脂肪、碳水化合物等），只需要列出食物原材料名称，不需要数量，用中文回复"
            )
            image_name = image.filename
        else:
            result = vision_service.analyze_image(
                image_url=image_url,
                prompt="请识别图片中的食材，并给出每种食材的营养信息（包括热量、蛋白质、脂肪、碳水化合物等），只需要列出食物原材料名称，不需要数量，用中文回复"
            )
            image_name = None

        if result.get("success"):
            logger.info(f"Recognize result: {result['content'][:200]}")
            return {
                "success": True,
                "result": result["content"],
                "image_name": image_name
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "识别失败")
            }
    except Exception as e:
        logger.error(f"食材识别失败: {e}")
        return {
            "success": False,
            "error": f"食材识别失败: {str(e)}"
        }


@router.get("/recognize-url", summary="识别食材图片URL")
async def recognize_ingredients_url(
    image_url: str = Query(..., description="图片URL地址"),
    current_user: User = Depends(get_current_user)
):
    """通过图片URL识别食材"""
    try:
        result = vision_service.analyze_image(
            image_url=image_url,
            prompt="请识别图片中的食材，只需要列出所有可见的食物原材料名称，不需要数量，用中文回复"
        )
        
        if result.get("success"):
            ingredients_text = result["content"]
            nutrition_info = await _get_nutrition_info(ingredients_text)
            
            return {
                "success": True,
                "ingredients": ingredients_text,
                "nutrition_details": nutrition_info
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "识别失败")
            }
    except Exception as e:
        logger.error(f"食材识别失败: {e}")
        return {
            "success": False,
            "error": f"食材识别失败: {str(e)}"
        }


@router.get("/substitute", summary="食材替代建议")
async def get_ingredient_substitute(
    ingredient: str = Query(..., description="要查询的食材"),
    current_user: User = Depends(get_current_user)
):
    """获取食材替代建议"""
    try:
        system_prompt = """你是一位专业的营养顾问。请根据用户的食材需求，给出健康、营养的替代食材建议。
请用中文回复，简洁明了地说明替代食材的名称、营养价值和适用场景。"""

        user_message = f"请推荐以下食材的健康替代选择：{ingredient}"

        result = await llm_service.chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )

        if result.get("success"):
            return {
                "success": True,
                "ingredient": ingredient,
                "suggestion": result["content"]
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "获取替代建议失败")
            }
    except Exception as e:
        logger.error(f"食材替代建议获取失败: {e}")
        return {
            "success": False,
            "error": f"获取替代建议失败: {str(e)}"
        }


@router.get("/seasonal", summary="季节性推荐食谱")
async def get_seasonal_recipes(
    season: str = Query(..., description="季节：spring/summer/autumn/winter"),
    current_user: User = Depends(get_current_user)
):
    """获取季节性推荐食谱"""
    logger.info(f"Seasonal request received: {season}")
    season_map = {
        "spring": "春季",
        "summer": "夏季", 
        "autumn": "秋季",
        "winter": "冬季"
    }
    
    chinese_season = season_map.get(season.lower(), season)
    logger.info(f"Chinese season: {chinese_season}")
    
    try:
        system_prompt = f"""你是一位专业的食谱推荐师。请根据季节特点推荐适合的食谱。
现在是{chinese_season}，请推荐适合这个季节的食谱，包括：
1. 适合这个季节的养生食物
2. 推荐食谱及其功效
3. 饮食注意事项

请用中文回复，内容丰富实用。"""

        logger.info("Calling LLM service...")
        result = await llm_service.chat_completion(
            messages=[{"role": "user", "content": f"请给我{chinese_season}的食谱推荐"}],
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=800
        )
        logger.info(f"LLM result: {result}")

        if result.get("success"):
            return {
                "success": True,
                "season": chinese_season,
                "recommendation": result["content"]
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "获取推荐失败")
            }
    except Exception as e:
        logger.error(f"季节性推荐获取失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": f"获取推荐失败: {str(e)}"
        }


@router.get("/{recipe_id}", summary="获取食谱详情")
async def get_recipe_detail(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到食谱"
        )
    
    ingredients = db.query(RecipeIngredient).filter(
        RecipeIngredient.recipe_id == recipe_id
    ).all()
    
    ingredient_details = []
    for ing in ingredients:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ing.ingredient_id).first()
        if ingredient:
            nutrition = db.query(IngredientNutrition).filter(
                IngredientNutrition.ingredient_id == ingredient.id
            ).first()
            ingredient_details.append({
                "name": ingredient.name,
                "quantity": ing.quantity,
                "unit": ing.unit,
                "calories": nutrition.calories if nutrition else None,
                "protein": nutrition.protein if nutrition else None,
                "fat": nutrition.fat if nutrition else None,
                "carbohydrate": nutrition.carbohydrate if nutrition else None
            })
    
    nutrition = db.query(RecipeNutrition).filter(
        RecipeNutrition.recipe_id == recipe_id
    ).first()
    
    return {
        "id": recipe.id,
        "name": recipe.name,
        "meal_type": recipe.meal_type,
        "difficulty": recipe.difficulty,
        "cook_time": recipe.cook_time,
        "description": recipe.description,
        "ingredients": ingredient_details,
        "nutrition": {
            "calories": nutrition.calories if nutrition else None,
            "protein": nutrition.protein if nutrition else None,
            "fat": nutrition.fat if nutrition else None,
            "carbohydrate": nutrition.carbohydrate if nutrition else None
        } if nutrition else None
    }


@router.get("/ingredients", response_model=List[IngredientResponse], summary="获取食材列表")
async def get_ingredients(
    category: Optional[str] = None,
    season: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Ingredient)
    
    if category:
        query = query.filter(Ingredient.category == category)
    if season:
        query = query.filter(Ingredient.season == season)
    
    offset = (page - 1) * page_size
    ingredients = query.offset(offset).limit(page_size).all()
    
    return [IngredientResponse.model_validate(ing) for ing in ingredients]


@router.get("/ingredients/{ingredient_id}", summary="获取食材详情")
async def get_ingredient_detail(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到食材"
        )
    
    nutrition = db.query(IngredientNutrition).filter(
        IngredientNutrition.ingredient_id == ingredient_id
    ).first()
    
    return {
        "id": ingredient.id,
        "name": ingredient.name,
        "category": ingredient.category,
        "season": ingredient.season,
        "description": ingredient.description,
        "nutrition": {
            "calories": nutrition.calories if nutrition else None,
            "protein": nutrition.protein if nutrition else None,
            "fat": nutrition.fat if nutrition else None,
            "carbohydrate": nutrition.carbohydrate if nutrition else None,
            "fiber": nutrition.fiber if nutrition else None,
            "vitamins": nutrition.vitamins if nutrition else None,
            "minerals": nutrition.minerals if nutrition else None
        } if nutrition else None
    }
