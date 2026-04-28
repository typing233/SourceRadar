from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from ..database import get_db
from ..models.content import Content
from ..models.user import User
from ..schemas.content import ContentResponse, FeedResponse
from ..services.recommendation import score_content_for_user
from .auth import get_current_user_from_token

router = APIRouter()


@router.get("/feed", response_model=FeedResponse)
def get_feed(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    query = db.query(Content)
    if source:
        query = query.filter(Content.source == source)

    all_content = query.all()
    scored = score_content_for_user(all_content, current_user.tags or [])
    scored.sort(key=lambda x: x[1], reverse=True)

    total = len(scored)
    start = (page - 1) * size
    end = start + size
    page_items = scored[start:end]

    items = []
    for content, match_score in page_items:
        item = ContentResponse.model_validate(content)
        item.match_score = match_score
        items.append(item)

    return FeedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.get("/search", response_model=FeedResponse)
def search_content(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    query_lower = f"%{q.lower()}%"
    results = db.query(Content).filter(
        or_(
            Content.title.ilike(query_lower),
            Content.description.ilike(query_lower),
        )
    ).all()

    scored = score_content_for_user(results, current_user.tags or [])
    scored.sort(key=lambda x: x[1], reverse=True)

    total = len(scored)
    start = (page - 1) * size
    end = start + size
    page_items = scored[start:end]

    items = []
    for content, match_score in page_items:
        item = ContentResponse.model_validate(content)
        item.match_score = match_score
        items.append(item)

    return FeedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if total > 0 else 0,
    )


@router.post("/refresh")
async def refresh_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    from ..scrapers.github_trending import scrape_github_trending
    from ..scrapers.hacker_news import scrape_hacker_news
    from ..scrapers.product_hunt import scrape_product_hunt

    results = {"scraped": 0, "errors": []}

    for scraper_fn, name in [
        (scrape_github_trending, "GitHub Trending"),
        (scrape_hacker_news, "Hacker News"),
        (scrape_product_hunt, "Product Hunt"),
    ]:
        try:
            items = await scraper_fn()
            for item in items:
                existing = db.query(Content).filter(Content.url == item["url"]).first()
                if not existing:
                    content = Content(**item)
                    db.add(content)
                    results["scraped"] += 1
            db.commit()
        except Exception as e:
            results["errors"].append(f"{name}: {str(e)}")

    return results
