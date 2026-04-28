from typing import List, Tuple, Any


def score_content_for_user(content_items: List[Any], user_tags: List[str]) -> List[Tuple[Any, float]]:
    if not user_tags:
        return [(item, float(item.score or 0)) for item in content_items]

    user_tags_lower = [tag.lower() for tag in user_tags]
    scored = []

    for item in content_items:
        base_score = float(item.score or 0)
        content_tags_lower = [t.lower() for t in (item.tags or [])]
        title_lower = (item.title or "").lower()
        description_lower = (item.description or "").lower()

        matching_tags = 0
        for user_tag in user_tags_lower:
            if user_tag in content_tags_lower:
                matching_tags += 1
            elif user_tag in title_lower or user_tag in description_lower:
                matching_tags += 0.5

        tag_match_bonus = 100.0
        match_score = base_score + tag_match_bonus * matching_tags
        scored.append((item, match_score))

    return scored
