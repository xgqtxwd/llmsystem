from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import UserDietPreference
from app.schemas import DietPreferenceCreate, DietPreferenceResponse
from app.utils import get_current_user
from app.models import User

router = APIRouter(prefix="/diet-preferences", tags=["饮食偏好"])


@router.post("/", response_model=DietPreferenceResponse, summary="创建或更新饮食偏好")
def create_or_update_diet_preference(
    preference_data: DietPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(UserDietPreference).filter(
        UserDietPreference.user_id == current_user.id
    ).first()

    if existing:
        if preference_data.taste_preference is not None:
            existing.taste_preference = preference_data.taste_preference
        if preference_data.diet_type is not None:
            existing.diet_type = preference_data.diet_type
        if preference_data.allergies is not None:
            existing.allergies = preference_data.allergies
        if preference_data.forbidden_foods is not None:
            existing.forbidden_foods = preference_data.forbidden_foods
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)
        return DietPreferenceResponse.model_validate(existing)
    else:
        new_preference = UserDietPreference(
            user_id=current_user.id,
            taste_preference=preference_data.taste_preference,
            diet_type=preference_data.diet_type,
            allergies=preference_data.allergies,
            forbidden_foods=preference_data.forbidden_foods,
            updated_at=datetime.now()
        )
        db.add(new_preference)
        db.commit()
        db.refresh(new_preference)
        return DietPreferenceResponse.model_validate(new_preference)


@router.get("/", response_model=DietPreferenceResponse, summary="获取饮食偏好")
def get_diet_preference(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    preference = db.query(UserDietPreference).filter(
        UserDietPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到饮食偏好设置"
        )
    
    return DietPreferenceResponse.model_validate(preference)


@router.delete("/", summary="删除饮食偏好")
def delete_diet_preference(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    preference = db.query(UserDietPreference).filter(
        UserDietPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到饮食偏好设置"
        )
    
    db.delete(preference)
    db.commit()
    
    return {"message": "饮食偏好已删除"}


@router.post("/allergies", summary="添加过敏食物")
def add_allergy(
    allergy: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(UserDietPreference).filter(
        UserDietPreference.user_id == current_user.id
    ).first()
    
    allergies_list = []
    if existing and existing.allergies:
        allergies_list = [a.strip() for a in existing.allergies.split(',') if a.strip()]
    
    if allergy not in allergies_list:
        allergies_list.append(allergy)
        allergies_str = ','.join(allergies_list)
        
        if existing:
            existing.allergies = allergies_str
            existing.updated_at = datetime.now()
        else:
            new_preference = UserDietPreference(
                user_id=current_user.id,
                allergies=allergies_str,
                updated_at=datetime.now()
            )
            db.add(new_preference)
        
        db.commit()
    
    return {"message": "过敏食物已添加", "allergies": allergies_list}


@router.delete("/allergies", summary="删除过敏食物")
def remove_allergy(
    allergy: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(UserDietPreference).filter(
        UserDietPreference.user_id == current_user.id
    ).first()
    
    if not existing or not existing.allergies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到过敏食物记录"
        )
    
    allergies_list = [a.strip() for a in existing.allergies.split(',') if a.strip()]
    
    if allergy in allergies_list:
        allergies_list.remove(allergy)
        existing.allergies = ','.join(allergies_list)
        existing.updated_at = datetime.now()
        db.commit()
    
    return {"message": "过敏食物已删除", "allergies": allergies_list}


@router.post("/forbidden-foods", summary="添加禁忌食物")
def add_forbidden_food(
    food: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(UserDietPreference).filter(
        UserDietPreference.user_id == current_user.id
    ).first()
    
    foods_list = []
    if existing and existing.forbidden_foods:
        foods_list = [f.strip() for f in existing.forbidden_foods.split(',') if f.strip()]
    
    if food not in foods_list:
        foods_list.append(food)
        foods_str = ','.join(foods_list)
        
        if existing:
            existing.forbidden_foods = foods_str
            existing.updated_at = datetime.now()
        else:
            new_preference = UserDietPreference(
                user_id=current_user.id,
                forbidden_foods=foods_str,
                updated_at=datetime.now()
            )
            db.add(new_preference)
        
        db.commit()
    
    return {"message": "禁忌食物已添加", "forbidden_foods": foods_list}


@router.delete("/forbidden-foods", summary="删除禁忌食物")
def remove_forbidden_food(
    food: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(UserDietPreference).filter(
        UserDietPreference.user_id == current_user.id
    ).first()
    
    if not existing or not existing.forbidden_foods:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到禁忌食物记录"
        )
    
    foods_list = [f.strip() for f in existing.forbidden_foods.split(',') if f.strip()]
    
    if food in foods_list:
        foods_list.remove(food)
        existing.forbidden_foods = ','.join(foods_list)
        existing.updated_at = datetime.now()
        db.commit()
    
    return {"message": "禁忌食物已删除", "forbidden_foods": foods_list}
