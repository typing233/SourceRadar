import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
import re


TECH_KEYWORDS = {
    "ai", "ml", "machine learning", "deep learning", "neural", "gpt", "llm",
    "rust", "go", "python", "javascript", "typescript", "react", "vue", "angular",
    "frontend", "backend", "devops", "docker", "kubernetes", "cloud",
    "open source", "cli", "tool", "library", "framework", "api",
    "web", "mobile", "ios", "android", "security", "database", "sql",
    "productivity", "automation", "bot", "scraper", "data",
}


def extract_tags_from_text(text: str, language: str = "") -> List[str]:
    tags = []
    if language:
        tags.append(language.lower())
        lang_map = {
            "javascript": "javascript",
            "typescript": "typescript",
            "python": "python",
            "rust": "rust",
            "go": "go",
            "java": "backend",
            "c++": "systems",
            "c": "systems",
            "swift": "mobile",
            "kotlin": "mobile",
        }
        mapped = lang_map.get(language.lower())
        if mapped and mapped not in tags:
            tags.append(mapped)

    text_lower = text.lower()
    for keyword in TECH_KEYWORDS:
        if keyword in text_lower:
            tags.append(keyword)

    if any(w in text_lower for w in ["neural", "gpt", "llm", "machine learning", "deep learning"]):
        if "ai" not in tags:
            tags.append("ai")
    if any(w in text_lower for w in ["react", "vue", "angular", "svelte", "frontend"]):
        if "frontend" not in tags:
            tags.append("frontend")

    return list(set(tags))[:10]


async def scrape_github_trending() -> List[Dict[str, Any]]:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    results = []
    urls = ["https://github.com/trending", "https://github.com/trending?since=weekly"]

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for url in urls:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "lxml")

                repo_items = soup.select("article.Box-row")
                for item in repo_items:
                    try:
                        name_tag = item.select_one("h2 a")
                        if not name_tag:
                            continue

                        repo_path = name_tag.get("href", "").strip("/")
                        repo_url = f"https://github.com/{repo_path}"

                        title_parts = [p.strip() for p in name_tag.get_text().split("/")]
                        title = " / ".join(p for p in title_parts if p)

                        desc_tag = item.select_one("p")
                        description = desc_tag.get_text(strip=True) if desc_tag else ""

                        lang_tag = item.select_one("[itemprop='programmingLanguage']")
                        language = lang_tag.get_text(strip=True) if lang_tag else ""

                        stars_tag = item.select_one("a[href$='/stargazers']")
                        stars_text = stars_tag.get_text(strip=True).replace(",", "") if stars_tag else "0"
                        stars = int(re.sub(r"[^\d]", "", stars_text) or "0")

                        tags = extract_tags_from_text(f"{title} {description}", language)

                        if repo_url not in [r["url"] for r in results]:
                            results.append({
                                "title": title,
                                "description": description,
                                "url": repo_url,
                                "source": "github",
                                "tags": tags,
                                "score": stars,
                                "published_at": datetime.utcnow(),
                            })
                    except Exception:
                        continue
            except Exception:
                continue

    return results
