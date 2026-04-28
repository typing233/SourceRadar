import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

PH_URL = "https://www.producthunt.com/leaderboard/daily"
# NOTE: Product Hunt's HTML structure is undocumented and changes frequently.
# This scraper uses multiple CSS selector fallbacks to stay resilient, but may
# require selector updates when the site redesigns.
HEADERS = {
    "User-Agent": "SourceRadar/1.0 (https://github.com/typing233/SourceRadar)",
    "Accept-Language": "en-US,en;q=0.9",
}


def crawl() -> list[dict]:
    results = []
    try:
        resp = requests.get(PH_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Product Hunt renders items with data-test attributes or specific class patterns.
        # We target the product list items.
        items = soup.select("li[class*='item']") or soup.select("div[class*='post']") or []

        # Fallback: look for links with product patterns
        if not items:
            anchors = soup.select("a[href^='/posts/']")
            seen = set()
            for a in anchors:
                href = a.get("href", "")
                if href in seen or not href.startswith("/posts/"):
                    continue
                seen.add(href)
                name = a.get_text(strip=True)
                if not name:
                    continue
                url = f"https://www.producthunt.com{href}"
                results.append(
                    {
                        "title": name[:500],
                        "url": url,
                        "description": "",
                        "source": "ph",
                        "raw_tags": [],
                        "score": 0.0,
                        "published_at": datetime.utcnow(),
                    }
                )

        for li in items:
            try:
                name_el = li.select_one("h3") or li.select_one("h2") or li.select_one("[class*='name']")
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)

                link_el = li.select_one("a[href^='/posts/']") or li.select_one("a")
                href = link_el["href"] if link_el else ""
                if not href:
                    continue
                url = f"https://www.producthunt.com{href}" if href.startswith("/") else href

                tagline_el = li.select_one("[class*='tagline']") or li.select_one("p")
                tagline = tagline_el.get_text(strip=True) if tagline_el else ""

                topic_els = li.select("[class*='topic']") or li.select("[class*='tag']") or li.select("[class*='category']")
                topics = [el.get_text(strip=True).lower() for el in topic_els if el.get_text(strip=True)]

                results.append(
                    {
                        "title": name[:500],
                        "url": url,
                        "description": tagline[:1000],
                        "source": "ph",
                        "raw_tags": topics,
                        "score": 0.0,
                        "published_at": datetime.utcnow(),
                    }
                )
            except Exception as exc:
                logger.debug("PH item parse error: %s", exc)

    except Exception as exc:
        logger.error("Product Hunt crawl failed: %s", exc)

    # Deduplicate by URL
    seen: set[str] = set()
    unique = []
    for r in results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    logger.info("Product Hunt: %d items", len(unique))
    return unique
