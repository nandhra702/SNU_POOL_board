from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, database, deps

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=schemas.UserProfileResponse)
def read_users_me(current_user: models.User = Depends(deps.get_current_active_user)):
    return current_user

@router.put("/me", response_model=schemas.UserProfileResponse)
def update_user_profile(
    profile_update: schemas.UserProfileUpdate, 
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    current_user.name = profile_update.name
    current_user.phone = profile_update.phone
    current_user.year = profile_update.year
    current_user.department = profile_update.department
    current_user.is_profile_complete = True
    
    db.commit()
    db.refresh(current_user)
    return current_user
