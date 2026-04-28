import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
import re


def extract_tags_from_tagline(tagline: str, name: str) -> List[str]:
    text = f"{name} {tagline}".lower()
    tag_map = {
        "ai": ["ai", "artificial intelligence", "gpt", "llm", "neural", "machine learning"],
        "productivity": ["productivity", "workflow", "automation", "task", "organize"],
        "developer tool": ["developer", "api", "code", "programming", "dev tool", "cli"],
        "design": ["design", "ui", "ux", "figma", "creative"],
        "marketing": ["marketing", "seo", "analytics", "growth"],
        "saas": ["saas", "subscription", "platform"],
        "open source": ["open source", "github", "free"],
        "mobile": ["mobile", "ios", "android", "app"],
        "web": ["web", "browser", "extension", "chrome"],
        "security": ["security", "privacy", "encryption", "auth"],
        "database": ["database", "data", "sql", "storage"],
    }

    tags = []
    for tag, keywords in tag_map.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)

    return tags[:8]


async def scrape_product_hunt() -> List[Dict[str, Any]]:
    results = []

    graphql_query = """
    {
      posts(order: VOTES, first: 30) {
        edges {
          node {
            id
            name
            tagline
            url
            votesCount
            createdAt
            topics {
              edges {
                node {
                  name
                }
              }
            }
          }
        }
      }
    }
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        try:
            response = await client.post(
                "https://api.producthunt.com/v2/api/graphql",
                json={"query": graphql_query},
                headers=headers,
            )
            if response.status_code == 200:
                data = response.json()
                edges = data.get("data", {}).get("posts", {}).get("edges", [])
                for edge in edges:
                    node = edge.get("node", {})
                    try:
                        name = node.get("name", "")
                        tagline = node.get("tagline", "")
                        url = node.get("url", "")
                        votes = node.get("votesCount", 0) or 0
                        created_at_str = node.get("createdAt", "")
                        topic_edges = node.get("topics", {}).get("edges", [])
                        topic_names = [e["node"]["name"].lower() for e in topic_edges if e.get("node")]

                        published_at = None
                        if created_at_str:
                            try:
                                published_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                            except Exception:
                                published_at = datetime.utcnow()

                        tags = extract_tags_from_tagline(tagline, name)
                        tags.extend(topic_names)
                        tags = list(set(tags))[:10]

                        if url and name:
                            results.append({
                                "title": name,
                                "description": tagline,
                                "url": url,
                                "source": "producthunt",
                                "tags": tags,
                                "score": votes,
                                "published_at": published_at or datetime.utcnow(),
                            })
                    except Exception:
                        continue
                if results:
                    return results
        except Exception:
            pass

        try:
            response = await client.get(
                "https://www.producthunt.com/",
                headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            product_items = soup.select("li[data-test='post-item']")
            if not product_items:
                product_items = soup.select("[class*='item_'][class*='post']")

            for item in product_items[:30]:
                try:
                    name_el = item.select_one("h3") or item.select_one("[class*='title']")
                    if not name_el:
                        continue
                    name = name_el.get_text(strip=True)

                    tagline_el = item.select_one("[class*='tagline']") or item.select_one("p")
                    tagline = tagline_el.get_text(strip=True) if tagline_el else ""

                    link_el = item.select_one("a[href*='/posts/']")
                    if not link_el:
                        continue
                    href = link_el.get("href", "")
                    url = f"https://www.producthunt.com{href}" if href.startswith("/") else href

                    votes_el = item.select_one("[class*='vote']") or item.select_one("button")
                    votes_text = votes_el.get_text(strip=True) if votes_el else "0"
                    votes = int(re.sub(r"[^\d]", "", votes_text) or "0")

                    tags = extract_tags_from_tagline(tagline, name)

                    if url and name:
                        results.append({
                            "title": name,
                            "description": tagline,
                            "url": url,
                            "source": "producthunt",
                            "tags": tags,
                            "score": votes,
                            "published_at": datetime.utcnow(),
                        })
                except Exception:
                    continue
        except Exception:
            pass

    return results
