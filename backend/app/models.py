from sqlalchemy import Column, BigInteger, String, Text, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户唯一ID")
    username = Column(String(50), nullable=True, comment="用户名")
    email = Column(String(100), nullable=True, comment="用户邮箱")
    phone = Column(String(20), nullable=True, comment="用户手机号")
    password_hash = Column(String(255), nullable=False, comment="加密后的密码")
    avatar = Column(String(255), nullable=True, comment="用户头像URL")
    is_admin = Column(Boolean, default=False, comment="是否为管理员")
    created_at = Column(DateTime, nullable=True, comment="账户创建时间")

    health_profile = relationship("UserHealthProfile", back_populates="user", uselist=False)
    diet_preferences = relationship("UserDietPreference", back_populates="user", uselist=False)
    health_goals = relationship("UserHealthGoal", back_populates="user")
    chat_records = relationship("ChatRecord", back_populates="user")
    diet_records = relationship("DietRecord", back_populates="user")
    food_recognition_records = relationship("FoodRecognitionRecord", back_populates="user")


class UserHealthProfile(Base):
    __tablename__ = "user_health_profile"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="用户ID")
    age = Column(Integer, nullable=True, comment="年龄")
    gender = Column(String(10), nullable=True, comment="性别")
    height = Column(Float, nullable=True, comment="身高(cm)")
    weight = Column(Float, nullable=True, comment="体重(kg)")
    activity_level = Column(String(20), nullable=True, comment="活动水平")
    health_conditions = Column(Text, nullable=True, comment="健康状况")
    bmi = Column(Float, nullable=True, comment="身体质量指数")
    created_at = Column(DateTime, nullable=True, comment="记录创建时间")

    user = relationship("User", back_populates="health_profile")


class UserDietPreference(Base):
    __tablename__ = "user_diet_preferences"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="用户ID")
    taste_preference = Column(String(50), nullable=True, comment="口味偏好")
    diet_type = Column(String(50), nullable=True, comment="饮食类型")
    allergies = Column(Text, nullable=True, comment="过敏食物")
    forbidden_foods = Column(Text, nullable=True, comment="禁忌食物")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")

    user = relationship("User", back_populates="diet_preferences")


class UserHealthGoal(Base):
    __tablename__ = "user_health_goals"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="用户ID")
    goal_type = Column(String(50), nullable=True, comment="目标类型(减肥/增肌/控糖)")
    target_weight = Column(Float, nullable=True, comment="目标体重")
    daily_calorie_target = Column(Float, nullable=True, comment="每日目标热量")
    created_at = Column(DateTime, nullable=True, comment="创建时间")

    user = relationship("User", back_populates="health_goals")


class ChatRecord(Base):
    __tablename__ = "chat_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="用户ID")
    question = Column(Text, nullable=True, comment="用户问题")
    answer = Column(Text, nullable=True, comment="AI回答")
    created_at = Column(DateTime, nullable=True, comment="对话时间")

    user = relationship("User", back_populates="chat_records")


class DietRecord(Base):
    __tablename__ = "diet_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="用户ID")
    meal_type = Column(String(20), nullable=True, comment="餐次类型")
    record_time = Column(DateTime, nullable=True, comment="记录时间")
    total_calories = Column(Float, nullable=True, comment="总热量")

    user = relationship("User", back_populates="diet_records")
    items = relationship("DietRecordItem", back_populates="record")


class DietRecordItem(Base):
    __tablename__ = "diet_record_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    record_id = Column(BigInteger, ForeignKey("diet_records.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="饮食记录ID")
    food_name = Column(String(100), nullable=True, comment="食物名称")
    quantity = Column(Float, nullable=True, comment="食用数量")
    calories = Column(Float, nullable=True, comment="摄入热量")

    record = relationship("DietRecord", back_populates="items")


class FoodRecognitionRecord(Base):
    __tablename__ = "food_recognition_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="用户ID")
    image_url = Column(String(255), nullable=True, comment="图片地址")
    recognized_food = Column(String(100), nullable=True, comment="识别食物")
    confidence = Column(Float, nullable=True, comment="识别置信度")
    recognized_at = Column(DateTime, nullable=True, comment="识别时间")

    user = relationship("User", back_populates="food_recognition_records")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="食材ID")
    name = Column(String(100), nullable=True, comment="食材名称")
    category = Column(String(50), nullable=True, comment="食材类别")
    season = Column(String(20), nullable=True, comment="适宜季节")
    description = Column(Text, nullable=True, comment="食材描述")

    nutrition = relationship("IngredientNutrition", back_populates="ingredient", uselist=False)


class IngredientNutrition(Base):
    __tablename__ = "ingredient_nutrition"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    ingredient_id = Column(BigInteger, ForeignKey("ingredients.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="食材ID")
    calories = Column(Float, nullable=True, comment="热量")
    protein = Column(Float, nullable=True, comment="蛋白质")
    fat = Column(Float, nullable=True, comment="脂肪")
    carbohydrate = Column(Float, nullable=True, comment="碳水化合物")
    fiber = Column(Float, nullable=True, comment="膳食纤维")
    vitamins = Column(Text, nullable=True, comment="维生素信息")
    minerals = Column(Text, nullable=True, comment="矿物质信息")

    ingredient = relationship("Ingredient", back_populates="nutrition")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="食谱ID")
    name = Column(String(100), nullable=True, comment="食谱名称")
    meal_type = Column(String(20), nullable=True, comment="餐次类型")
    difficulty = Column(String(20), nullable=True, comment="制作难度")
    cook_time = Column(Integer, nullable=True, comment="烹饪时间(分钟)")
    description = Column(Text, nullable=True, comment="食谱介绍")
    created_at = Column(DateTime, nullable=True, comment="创建时间")

    ingredients = relationship("RecipeIngredient", back_populates="recipe")
    nutrition = relationship("RecipeNutrition", back_populates="recipe", uselist=False)


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    recipe_id = Column(BigInteger, ForeignKey("recipes.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="食谱ID")
    ingredient_id = Column(BigInteger, ForeignKey("ingredients.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="食材ID")
    quantity = Column(Float, nullable=True, comment="食材用量")
    unit = Column(String(20), nullable=True, comment="单位")

    recipe = relationship("Recipe", back_populates="ingredients")


class RecipeNutrition(Base):
    __tablename__ = "recipe_nutrition"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    recipe_id = Column(BigInteger, ForeignKey("recipes.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="食谱ID")
    calories = Column(Float, nullable=True, comment="热量")
    protein = Column(Float, nullable=True, comment="蛋白质")
    fat = Column(Float, nullable=True, comment="脂肪")
    carbohydrate = Column(Float, nullable=True, comment="碳水化合物")

    recipe = relationship("Recipe", back_populates="nutrition")


class NutritionKnowledge(Base):
    __tablename__ = "nutrition_knowledge"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="知识ID")
    title = Column(String(200), nullable=True, comment="知识标题")
    content = Column(Text, nullable=True, comment="知识内容")
    category = Column(String(50), nullable=True, comment="知识分类")
    source = Column(String(100), nullable=True, comment="数据来源")
    created_at = Column(DateTime, nullable=True, comment="创建时间")


class KnowledgeEmbedding(Base):
    __tablename__ = "knowledge_embeddings"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    knowledge_id = Column(BigInteger, ForeignKey("nutrition_knowledge.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=True, comment="知识ID")
    embedding_vector = Column(Text, nullable=True, comment="向量数据")
    model_name = Column(String(100), nullable=True, comment="Embedding模型")
