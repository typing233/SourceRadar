import logging
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from ..database import SessionLocal

logger = logging.getLogger(__name__)


def run_scrapers():
    from ..scrapers.github_trending import scrape_github_trending
    from ..scrapers.hacker_news import scrape_hacker_news
    from ..scrapers.product_hunt import scrape_product_hunt
    from ..models.content import Content

    db = SessionLocal()
    total_scraped = 0
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for scraper_fn, name in [
            (scrape_github_trending, "GitHub Trending"),
            (scrape_hacker_news, "Hacker News"),
            (scrape_product_hunt, "Product Hunt"),
        ]:
            try:
                items = loop.run_until_complete(scraper_fn())
                for item in items:
                    existing = db.query(Content).filter(Content.url == item["url"]).first()
                    if not existing:
                        content = Content(**item)
                        db.add(content)
                        total_scraped += 1
                db.commit()
                logger.info(f"Scraped {len(items)} items from {name}")
            except Exception as e:
                logger.error(f"Error scraping {name}: {e}")

        loop.close()
    except Exception as e:
        logger.error(f"Scheduler scrape error: {e}")
    finally:
        db.close()

    logger.info(f"Total new items scraped: {total_scraped}")


def send_weekly_reports():
    from ..services.email_service import send_weekly_reports_to_all

    db = SessionLocal()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_weekly_reports_to_all(db))
        loop.close()
    except Exception as e:
        logger.error(f"Error sending weekly reports: {e}")
    finally:
        db.close()


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        run_scrapers,
        trigger=IntervalTrigger(hours=6),
        id="scrape_all",
        name="Scrape all sources",
        replace_existing=True,
        misfire_grace_time=300,
    )

    scheduler.add_job(
        send_weekly_reports,
        trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
        id="weekly_reports",
        name="Send weekly reports",
        replace_existing=True,
        misfire_grace_time=600,
    )

    return scheduler
