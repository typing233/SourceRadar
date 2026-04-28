import httpx
from typing import List, Dict, Any
from datetime import datetime


TECH_KEYWORDS = [
    "ai", "ml", "machine learning", "deep learning", "neural", "gpt", "llm",
    "rust", "go", "python", "javascript", "typescript", "react", "vue",
    "frontend", "backend", "devops", "docker", "kubernetes", "cloud",
    "open source", "cli", "tool", "library", "framework", "api",
    "web", "mobile", "security", "database", "sql", "productivity",
    "automation", "data", "startup", "indie", "saas", "web3", "blockchain",
]


def extract_tags_from_title(title: str) -> List[str]:
    title_lower = title.lower()
    tags = []
    for keyword in TECH_KEYWORDS:
        if keyword in title_lower:
            tags.append(keyword)

    if any(w in title_lower for w in ["show hn", "ask hn", "tell hn"]):
        tags.append("indie dev")
    if "show hn" in title_lower:
        tags.append("open source")
    if any(w in title_lower for w in ["gpt", "llm", "neural", "machine learning", "deep learning"]):
        if "ai" not in tags:
            tags.append("ai")

    return list(set(tags))[:10]


async def scrape_hacker_news() -> List[Dict[str, Any]]:
    url = "https://hn.algolia.com/api/v1/search?tags=story&hitsPerPage=50&numericFilters=points>10"
    results = []

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            for hit in data.get("hits", []):
                try:
                    title = hit.get("title", "")
                    if not title:
                        continue

                    story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                    points = hit.get("points", 0) or 0
                    story_id = hit.get("objectID", "")
                    tags = extract_tags_from_title(title)

                    created_at_str = hit.get("created_at")
                    published_at = None
                    if created_at_str:
                        try:
                            published_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                        except Exception:
                            published_at = datetime.utcnow()

                    results.append({
                        "title": title,
                        "description": f"Hacker News story with {points} points. Story ID: {story_id}",
                        "url": story_url,
                        "source": "hackernews",
                        "tags": tags,
                        "score": points,
                        "published_at": published_at or datetime.utcnow(),
                    })
                except Exception:
                    continue
        except Exception:
            pass

    return results
