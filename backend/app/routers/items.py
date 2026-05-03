import json
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db
from app.services.feed import score_item

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("", response_model=schemas.FeedResponse)
def get_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user_tags = [ut.tag.name for ut in current_user.user_tags]

    query = db.query(models.Item)
    if source:
        query = query.filter(models.Item.source == source)
    if q:
        search = f"%{q}%"
        query = query.filter(
            models.Item.title.ilike(search) | models.Item.description.ilike(search)
        )

    all_items = query.all()

    # Score and sort
    scored = []
    for item in all_items:
        ms = score_item(item, user_tags)
        scored.append((item, ms))

    scored.sort(key=lambda x: (x[1], x[0].published_at or x[0].created_at), reverse=True)

    total = len(scored)
    start = (page - 1) * page_size
    page_items = scored[start: start + page_size]

    result = []
    for item, ms in page_items:
        result.append(
            schemas.ItemOut(
                id=item.id,
                title=item.title,
                url=item.url,
                description=item.description or "",
                source=item.source,
                raw_tags=item.get_raw_tags(),
                semantic_tags=item.get_semantic_tags(),
                category=item.category,
                score=item.score,
                published_at=item.published_at,
                created_at=item.created_at,
                analyzed_at=item.analyzed_at,
                match_score=ms,
            )
        )

    return schemas.FeedResponse(items=result, total=total, page=page)
