from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app import models
from app.services.feed import score_item

TOP_N = 20


def _week_start() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())


def build_digest_for_user(db: Session, user: models.User) -> models.Digest | None:
    user_tags = [ut.tag.name for ut in user.user_tags]

    # Items from the past 7 days
    since = datetime.utcnow() - timedelta(days=7)
    items = db.query(models.Item).filter(models.Item.created_at >= since).all()

    if not items:
        return None

    scored = sorted(
        [(item, score_item(item, user_tags)) for item in items],
        key=lambda x: (x[1], x[0].published_at or x[0].created_at),
        reverse=True,
    )[:TOP_N]

    week_start = _week_start()
    digest = models.Digest(user_id=user.id, week_start=week_start)
    db.add(digest)
    db.flush()

    for item, ms in scored:
        di = models.DigestItem(digest_id=digest.id, item_id=item.id, match_score=ms)
        db.add(di)

    db.commit()
    db.refresh(digest)
    return digest
