import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://github.com/trending"
HEADERS = {"User-Agent": "SourceRadar/1.0 (https://github.com/typing233/SourceRadar)"}


def crawl() -> list[dict]:
    results = []
    try:
        resp = requests.get(BASE_URL, params={"since": "daily"}, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        for article in soup.select("article.Box-row"):
            try:
                h2 = article.select_one("h2 a")
                if not h2:
                    continue
                path = h2["href"].strip("/")
                url = f"https://github.com/{path}"
                title = path.replace("/", " / ")

                desc_el = article.select_one("p")
                description = desc_el.get_text(strip=True) if desc_el else ""

                lang_el = article.select_one("[itemprop='programmingLanguage']")
                language = lang_el.get_text(strip=True) if lang_el else ""

                stars_el = article.select_one("a[href$='/stargazers']")
                stars_text = stars_el.get_text(strip=True).replace(",", "") if stars_el else "0"
                try:
                    stars = int(stars_text)
                except ValueError:
                    stars = 0

                raw_tags = [language.lower()] if language else []

                results.append(
                    {
                        "title": title,
                        "url": url,
                        "description": description,
                        "source": "github",
                        "raw_tags": raw_tags,
                        "score": float(stars),
                        "published_at": datetime.utcnow(),
                    }
                )
            except Exception as exc:
                logger.debug("Error parsing GH trending row: %s", exc)

    except Exception as exc:
        logger.error("GitHub trending crawl failed: %s", exc)

    logger.info("GitHub trending: %d items", len(results))
    return results
