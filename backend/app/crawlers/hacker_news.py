import asyncio
import logging
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
MIN_SCORE = 50
MAX_STORIES = 200
CONCURRENCY = 20


async def _fetch_item(client: httpx.AsyncClient, item_id: int) -> dict | None:
    try:
        resp = await client.get(ITEM_URL.format(item_id), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if not data or data.get("type") != "story" or not data.get("url"):
            return None
        if data.get("score", 0) < MIN_SCORE:
            return None
        ts = data.get("time")
        published_at = datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None) if ts else datetime.utcnow()
        return {
            "title": data.get("title", "")[:500],
            "url": data.get("url", ""),
            "description": data.get("text", "") or "",
            "source": "hn",
            "raw_tags": [],
            "score": float(data.get("score", 0)),
            "published_at": published_at,
        }
    except Exception as exc:
        logger.debug("HN item %s fetch failed: %s", item_id, exc)
        return None


async def _crawl_async() -> list[dict]:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(TOP_STORIES_URL, timeout=10)
            resp.raise_for_status()
            ids = resp.json()[:MAX_STORIES]
        except Exception as exc:
            logger.error("HN top stories fetch failed: %s", exc)
            return []

        sem = asyncio.Semaphore(CONCURRENCY)

        async def guarded(item_id):
            async with sem:
                return await _fetch_item(client, item_id)

        tasks = [guarded(i) for i in ids]
        raw = await asyncio.gather(*tasks)
        results = [r for r in raw if r is not None]
        logger.info("Hacker News: %d items (score>%d)", len(results), MIN_SCORE)
        return results


def crawl() -> list[dict]:
    return asyncio.run(_crawl_async())
