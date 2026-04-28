from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db
from app.services.digest import build_digest_for_user
from app.services.email import send_digest_email

router = APIRouter(prefix="/api/digest", tags=["digest"])


def _serialize_digest(digest: models.Digest) -> schemas.DigestOut:
    items_out = []
    for di in digest.digest_items:
        item = di.item
        items_out.append(
            schemas.DigestItemOut(
                id=di.id,
                item_id=item.id,
                match_score=di.match_score,
                title=item.title,
                url=item.url,
                description=item.description or "",
                source=item.source,
                raw_tags=item.get_raw_tags(),
                published_at=item.published_at,
            )
        )
    items_out.sort(key=lambda x: x.match_score, reverse=True)
    return schemas.DigestOut(
        id=digest.id,
        user_id=digest.user_id,
        week_start=datetime.combine(digest.week_start, datetime.min.time()),
        created_at=digest.created_at,
        sent_at=digest.sent_at,
        items=items_out,
    )


@router.get("", response_model=Optional[schemas.DigestOut])
def get_digest(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    digest = (
        db.query(models.Digest)
        .filter(models.Digest.user_id == current_user.id)
        .order_by(models.Digest.created_at.desc())
        .first()
    )
    if not digest:
        return None
    return _serialize_digest(digest)


@router.post("/generate", response_model=schemas.DigestOut)
async def generate_digest(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    digest = build_digest_for_user(db, current_user)
    if not digest:
        raise HTTPException(status_code=404, detail="No items found for digest")
    try:
        await send_digest_email(current_user, digest)
        digest.sent_at = datetime.utcnow()
        db.commit()
        db.refresh(digest)
    except Exception as exc:
        # Email failure should not block the response; log for debugging
        import logging
        logging.getLogger(__name__).warning("Digest email failed for %s: %s", current_user.email, exc)
    return _serialize_digest(digest)
