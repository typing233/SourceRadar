import json
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models

logger = logging.getLogger(__name__)


def _upsert_items(db: Session, items: list[dict]) -> int:
    count = 0
    for data in items:
        existing = db.query(models.Item).filter(models.Item.url == data["url"]).first()
        if existing:
            continue
        item = models.Item(
            title=data["title"][:500],
            url=data["url"][:1000],
            description=data.get("description", "")[:5000],
            source=data["source"],
            raw_tags=json.dumps(data.get("raw_tags", [])),
            score=data.get("score", 0.0),
            published_at=data.get("published_at"),
        )
        db.add(item)
        count += 1
    db.commit()
    return count


def run_crawlers():
    from app.crawlers.github_trending import crawl as gh_crawl
    from app.crawlers.hacker_news import crawl as hn_crawl
    from app.crawlers.product_hunt import crawl as ph_crawl

    db = SessionLocal()
    try:
        for crawl_fn in [gh_crawl, hn_crawl, ph_crawl]:
            try:
                items = crawl_fn()
                n = _upsert_items(db, items)
                logger.info("Crawled %d new items via %s", n, crawl_fn.__module__)
            except Exception as exc:
                logger.exception("Crawler %s failed: %s", crawl_fn.__module__, exc)
    finally:
        db.close()


def run_weekly_digests():
    import asyncio
    from app.services.digest import build_digest_for_user
    from app.services.email import send_digest_email

    db = SessionLocal()
    try:
        users = (
            db.query(models.User)
            .filter(models.User.is_active, models.User.receive_digest)
            .all()
        )
        for user in users:
            try:
                digest = build_digest_for_user(db, user)
                if digest:
                    asyncio.run(send_digest_email(user, digest))
                    digest.sent_at = datetime.utcnow()
                    db.commit()
            except Exception as exc:
                logger.exception("Digest for user %s failed: %s", user.email, exc)
    finally:
        db.close()


def start_scheduler():
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BackgroundScheduler()

    # Every 6 hours
    scheduler.add_job(run_crawlers, "interval", hours=6, id="crawlers", replace_existing=True)

    # Every Monday at 08:00 UTC
    scheduler.add_job(
        run_weekly_digests,
        CronTrigger(day_of_week="mon", hour=8, minute=0, timezone="UTC"),
        id="weekly_digest",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started")
    return scheduler
