from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class ActivityLevelEnum(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"
    very_active = "very_active"


class MealTypeEnum(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class GoalTypeEnum(str, Enum):
    weight_loss = "weight_loss"
    muscle_gain = "muscle_gain"
    blood_sugar_control = "blood_sugar_control"
    health_maintenance = "health_maintenance"


class UserRegister(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str = Field(..., min_length=6, max_length=50)

    @model_validator(mode='after')
    def check_at_least_one_contact(self):
        if not any([self.username, self.email, self.phone]):
            raise ValueError('At least one of username, email, or phone is required')
        return self


class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str


class UserResponse(BaseModel):
    id: int
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    is_admin: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class HealthProfileCreate(BaseModel):
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[GenderEnum] = None
    height: Optional[float] = Field(None, ge=50, le=250)
    weight: Optional[float] = Field(None, ge=20, le=500)
    activity_level: Optional[ActivityLevelEnum] = None
    health_conditions: Optional[str] = None


class HealthProfileResponse(BaseModel):
    id: int
    user_id: int
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    activity_level: Optional[str] = None
    health_conditions: Optional[str] = None
    bmi: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_bmi(cls, obj):
        bmi = None
        if obj.height and obj.weight:
            height_m = obj.height / 100
            bmi = round(obj.weight / (height_m ** 2), 2)
        obj.bmi = bmi
        return super().model_validate(obj)


class DietPreferenceCreate(BaseModel):
    taste_preference: Optional[str] = None
    diet_type: Optional[str] = None
    allergies: Optional[str] = None
    forbidden_foods: Optional[str] = None


class DietPreferenceResponse(BaseModel):
    id: int
    user_id: int
    taste_preference: Optional[str] = None
    diet_type: Optional[str] = None
    allergies: Optional[str] = None
    forbidden_foods: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HealthGoalCreate(BaseModel):
    goal_type: GoalTypeEnum
    target_weight: Optional[float] = Field(None, ge=20, le=500)
    daily_calorie_target: Optional[float] = Field(None, ge=500, le=10000)


class HealthGoalResponse(BaseModel):
    id: int
    user_id: int
    goal_type: str
    target_weight: Optional[float] = None
    daily_calorie_target: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    id: int
    user_id: int
    question: str
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True


class DietRecordCreate(BaseModel):
    meal_type: MealTypeEnum
    record_time: Optional[datetime] = None
    items: List[dict] = []


class DietRecordResponse(BaseModel):
    id: int
    user_id: int
    meal_type: str
    record_time: Optional[datetime] = None
    total_calories: Optional[float] = None
    items: List[dict] = []

    class Config:
        from_attributes = True


class FoodRecognitionRequest(BaseModel):
    image_url: str


class FoodRecognitionResponse(BaseModel):
    id: int
    user_id: int
    image_url: str
    recognized_food: str
    confidence: float
    recognized_at: datetime

    class Config:
        from_attributes = True


class NutritionKnowledgeResponse(BaseModel):
    id: int
    title: str
    content: str
    category: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecipeResponse(BaseModel):
    id: int
    name: str
    meal_type: Optional[str] = None
    difficulty: Optional[str] = None
    cook_time: Optional[int] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class IngredientResponse(BaseModel):
    id: int
    name: Optional[str] = None
    category: Optional[str] = None
    season: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True
