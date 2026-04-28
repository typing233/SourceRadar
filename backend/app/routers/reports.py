from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.content import Content
from ..schemas.content import ContentResponse
from ..services.recommendation import score_content_for_user
from ..services.email_service import send_weekly_report_email
from .auth import get_current_user_from_token

router = APIRouter()


@router.get("/weekly", response_model=List[ContentResponse])
def get_weekly_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    content = db.query(Content).filter(Content.created_at >= week_ago).all()

    scored = score_content_for_user(content, current_user.tags or [])
    scored.sort(key=lambda x: x[1], reverse=True)
    top_items = scored[:20]

    items = []
    for c, match_score in top_items:
        item = ContentResponse.model_validate(c)
        item.match_score = match_score
        items.append(item)
    return items


@router.post("/send")
async def send_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    content = db.query(Content).filter(Content.created_at >= week_ago).all()

    scored = score_content_for_user(content, current_user.tags or [])
    scored.sort(key=lambda x: x[1], reverse=True)
    top_items = [c for c, _ in scored[:20]]

    success = await send_weekly_report_email(current_user, top_items)
    if success:
        return {"message": "Weekly report sent successfully"}
    return {"message": "Report logged to console (email not configured)"}
