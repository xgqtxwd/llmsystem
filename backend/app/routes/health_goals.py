from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import UserHealthGoal
from app.schemas import HealthGoalCreate, HealthGoalResponse
from app.utils import get_current_user
from app.models import User

router = APIRouter(prefix="/health-goals", tags=["健康目标"])


@router.post("/", response_model=HealthGoalResponse, summary="创建健康目标")
def create_health_goal(
    goal_data: HealthGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(UserHealthGoal).filter(
        UserHealthGoal.user_id == current_user.id,
        UserHealthGoal.goal_type == goal_data.goal_type.value
    ).first()

    if existing:
        existing.target_weight = goal_data.target_weight
        existing.daily_calorie_target = goal_data.daily_calorie_target
        db.commit()
        db.refresh(existing)
        return HealthGoalResponse.model_validate(existing)
    else:
        new_goal = UserHealthGoal(
            user_id=current_user.id,
            goal_type=goal_data.goal_type.value,
            target_weight=goal_data.target_weight,
            daily_calorie_target=goal_data.daily_calorie_target,
            created_at=datetime.now()
        )
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)
        return HealthGoalResponse.model_validate(new_goal)


@router.get("/", response_model=List[HealthGoalResponse], summary="获取健康目标列表")
def get_health_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goals = db.query(UserHealthGoal).filter(
        UserHealthGoal.user_id == current_user.id
    ).all()
    return [HealthGoalResponse.model_validate(goal) for goal in goals]


@router.get("/{goal_id}", response_model=HealthGoalResponse, summary="获取单个健康目标")
def get_health_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(UserHealthGoal).filter(
        UserHealthGoal.id == goal_id,
        UserHealthGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到健康目标"
        )
    
    return HealthGoalResponse.model_validate(goal)


@router.put("/{goal_id}", response_model=HealthGoalResponse, summary="更新健康目标")
def update_health_goal(
    goal_id: int,
    goal_data: HealthGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(UserHealthGoal).filter(
        UserHealthGoal.id == goal_id,
        UserHealthGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到健康目标"
        )
    
    goal.goal_type = goal_data.goal_type.value
    goal.target_weight = goal_data.target_weight
    goal.daily_calorie_target = goal_data.daily_calorie_target
    
    db.commit()
    db.refresh(goal)
    return HealthGoalResponse.model_validate(goal)


@router.delete("/{goal_id}", summary="删除健康目标")
def delete_health_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(UserHealthGoal).filter(
        UserHealthGoal.id == goal_id,
        UserHealthGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到健康目标"
        )
    
    db.delete(goal)
    db.commit()
    
    return {"message": "健康目标已删除"}


@router.get("/progress/summary", summary="获取目标进度摘要")
def get_goal_progress_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models import UserHealthProfile
    
    profile = db.query(UserHealthProfile).filter(
        UserHealthProfile.user_id == current_user.id
    ).first()
    
    goals = db.query(UserHealthGoal).filter(
        UserHealthGoal.user_id == current_user.id
    ).all()
    
    current_weight = profile.weight if profile else None
    bmi = profile.bmi if profile else None
    
    progress = []
    for goal in goals:
        goal_progress = {
            "goal_type": goal.goal_type,
            "target_weight": goal.target_weight,
            "daily_calorie_target": goal.daily_calorie_target,
            "current_weight": current_weight,
            "current_bmi": bmi,
            "weight_diff": None,
            "progress_percentage": None
        }
        
        if goal.target_weight and current_weight:
            if goal.goal_type == "weight_loss":
                goal_progress["weight_diff"] = current_weight - goal.target_weight
                goal_progress["progress_percentage"] = max(0, min(100, (200 - current_weight) / (200 - goal.target_weight) * 100)) if goal.target_weight < 200 else 100
            elif goal.goal_type == "muscle_gain":
                goal_progress["weight_diff"] = goal.target_weight - current_weight
                goal_progress["progress_percentage"] = max(0, min(100, (current_weight - 50) / (goal.target_weight - 50) * 100)) if goal.target_weight > 50 else 100
        
        progress.append(goal_progress)
    
    return {
        "current_weight": current_weight,
        "current_bmi": bmi,
        "goals": progress
    }
