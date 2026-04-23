from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import UserHealthProfile
from app.schemas import HealthProfileCreate, HealthProfileResponse
from app.utils import get_current_user
from app.models import User

router = APIRouter(prefix="/health-profile", tags=["健康档案"])


def calculate_bmi(height: float, weight: float) -> float:
    if height and weight:
        height_m = height / 100
        return round(weight / (height_m ** 2), 2)
    return None


@router.post("/", response_model=HealthProfileResponse, summary="创建或更新健康档案")
def create_or_update_health_profile(
    profile_data: HealthProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_profile = db.query(UserHealthProfile).filter(
        UserHealthProfile.user_id == current_user.id
    ).first()

    bmi = calculate_bmi(profile_data.height, profile_data.weight)

    if existing_profile:
        if profile_data.age is not None:
            existing_profile.age = profile_data.age
        if profile_data.gender is not None:
            existing_profile.gender = profile_data.gender.value if hasattr(profile_data.gender, 'value') else profile_data.gender
        if profile_data.height is not None:
            existing_profile.height = profile_data.height
        if profile_data.weight is not None:
            existing_profile.weight = profile_data.weight
        if profile_data.activity_level is not None:
            existing_profile.activity_level = profile_data.activity_level.value if hasattr(profile_data.activity_level, 'value') else profile_data.activity_level
        if profile_data.health_conditions is not None:
            existing_profile.health_conditions = profile_data.health_conditions
        existing_profile.bmi = bmi
        db.commit()
        db.refresh(existing_profile)
        return HealthProfileResponse.from_orm_with_bmi(existing_profile)
    else:
        new_profile = UserHealthProfile(
            user_id=current_user.id,
            age=profile_data.age,
            gender=profile_data.gender.value if hasattr(profile_data.gender, 'value') else profile_data.gender,
            height=profile_data.height,
            weight=profile_data.weight,
            activity_level=profile_data.activity_level.value if hasattr(profile_data.activity_level, 'value') else profile_data.activity_level,
            health_conditions=profile_data.health_conditions,
            bmi=bmi,
            created_at=datetime.now()
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        return HealthProfileResponse.from_orm_with_bmi(new_profile)


@router.get("/", response_model=HealthProfileResponse, summary="获取健康档案")
def get_health_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(UserHealthProfile).filter(
        UserHealthProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到健康档案"
        )
    
    return HealthProfileResponse.from_orm_with_bmi(profile)


@router.delete("/", summary="删除健康档案")
def delete_health_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(UserHealthProfile).filter(
        UserHealthProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到健康档案"
        )
    
    db.delete(profile)
    db.commit()
    
    return {"message": "健康档案已删除"}
