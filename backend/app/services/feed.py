import json


def score_item(item, user_tags: list[str]) -> float:
    """Score an item based on overlap with user's tags (case-insensitive substring match)."""
    if not user_tags:
        return 0.0
    tags_lower = [t.lower() for t in user_tags]
    raw = item.raw_tags if isinstance(item.raw_tags, str) else "[]"
    try:
        item_tags = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        item_tags = []
    text = f"{item.title} {item.description or ''} {' '.join(item_tags)}".lower()
    hits = sum(1 for t in tags_lower if t in text)
    return hits / max(len(tags_lower), 1)
