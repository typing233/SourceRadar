import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db
from app.services.semantic import SemanticService, LLMConfig, get_semantic_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["llm"])


def get_user_semantic_service(user: models.User) -> SemanticService:
    if user.llm_base_url and user.llm_api_key:
        config = LLMConfig(
            base_url=user.llm_base_url,
            api_key=user.llm_api_key,
            model_name=user.llm_model_name or "gpt-3.5-turbo",
            embedding_model=user.llm_embedding_model or "text-embedding-ada-002",
        )
        return SemanticService(config)
    return get_semantic_service()


@router.get("/config", response_model=schemas.LLMConfigOut)
def get_llm_config(
    current_user: models.User = Depends(get_current_user),
):
    configured = bool(current_user.llm_api_key)
    return schemas.LLMConfigOut(
        base_url=current_user.llm_base_url,
        model_name=current_user.llm_model_name,
        embedding_model=current_user.llm_embedding_model,
        configured=configured,
    )


@router.put("/config", response_model=schemas.LLMConfigOut)
def update_llm_config(
    payload: schemas.LLMConfigUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.base_url is not None:
        current_user.llm_base_url = payload.base_url.rstrip("/") if payload.base_url else None
    if payload.api_key is not None:
        current_user.llm_api_key = payload.api_key
    if payload.model_name is not None:
        current_user.llm_model_name = payload.model_name
    if payload.embedding_model is not None:
        current_user.llm_embedding_model = payload.embedding_model

    db.commit()
    db.refresh(current_user)

    configured = bool(current_user.llm_api_key)
    return schemas.LLMConfigOut(
        base_url=current_user.llm_base_url,
        model_name=current_user.llm_model_name,
        embedding_model=current_user.llm_embedding_model,
        configured=configured,
    )


@router.post("/test-connection", response_model=schemas.LLMConnectionTest)
async def test_llm_connection(
    current_user: models.User = Depends(get_current_user),
):
    semantic_service = get_user_semantic_service(current_user)
    success, message = await semantic_service.test_connection()
    return schemas.LLMConnectionTest(success=success, message=message)


@router.post("/analyze-item/{item_id}", response_model=schemas.ItemOut)
async def analyze_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    semantic_service = get_user_semantic_service(current_user)

    raw_tags = item.get_raw_tags()
    semantic_tags = await semantic_service.generate_tags(
        item.title,
        item.description,
        raw_tags
    )
    item.set_semantic_tags(semantic_tags)

    category = await semantic_service.categorize_project(item.title, item.description)
    item.category = category
    item.analyzed_at = datetime.utcnow()

    db.commit()
    db.refresh(item)

    user_tags = [ut.tag.name for ut in current_user.user_tags]
    from app.services.feed import score_item
    match_score = score_item(item, user_tags)

    return schemas.ItemOut(
        id=item.id,
        title=item.title,
        url=item.url,
        description=item.description or "",
        source=item.source,
        raw_tags=item.get_raw_tags(),
        semantic_tags=item.get_semantic_tags(),
        category=item.category,
        score=item.score,
        published_at=item.published_at,
        created_at=item.created_at,
        analyzed_at=item.analyzed_at,
        match_score=match_score,
    )


@router.post("/analyze-all", response_model=dict)
async def analyze_all_items(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    items = db.query(models.Item).filter(models.Item.analyzed_at == None).all()
    semantic_service = get_user_semantic_service(current_user)

    analyzed_count = 0
    for item in items:
        try:
            raw_tags = item.get_raw_tags()
            semantic_tags = await semantic_service.generate_tags(
                item.title,
                item.description,
                raw_tags
            )
            item.set_semantic_tags(semantic_tags)

            category = await semantic_service.categorize_project(item.title, item.description)
            item.category = category
            item.analyzed_at = datetime.utcnow()

            analyzed_count += 1
        except Exception as e:
            logger.error(f"Failed to analyze item {item.id}: {e}")
            continue

    db.commit()

    return {"analyzed": analyzed_count, "total": len(items)}
