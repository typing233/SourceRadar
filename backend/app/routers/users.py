from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserResponse, UserTagsUpdate, UserProfileUpdate
from .auth import get_current_user_from_token

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user_from_token)):
    return current_user


@router.put("/tags", response_model=UserResponse)
def update_tags(
    tags_data: UserTagsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    current_user.tags = tags_data.tags
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    if profile_data.email_reports is not None:
        current_user.email_reports = profile_data.email_reports
    db.commit()
    db.refresh(current_user)
    return current_user
