from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/user", tags=["tags"])


@router.get("/tags", response_model=list[schemas.TagOut])
def get_tags(current_user: models.User = Depends(get_current_user)):
    return [ut.tag for ut in current_user.user_tags]


@router.put("/tags", response_model=list[schemas.TagOut])
def update_tags(
    payload: schemas.UserTagsUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Remove all existing user tags
    db.query(models.UserTag).filter(models.UserTag.user_id == current_user.id).delete()

    new_user_tags = []
    for tag_name in payload.tags:
        tag_name = tag_name.strip().lower()
        if not tag_name:
            continue
        tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not tag:
            tag = models.Tag(name=tag_name)
            db.add(tag)
            db.flush()
        ut = models.UserTag(user_id=current_user.id, tag_id=tag.id)
        db.add(ut)
        new_user_tags.append(tag)

    db.commit()
    return new_user_tags


@router.put("/settings", response_model=schemas.UserOut)
def update_settings(
    payload: schemas.UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.receive_digest is not None:
        current_user.receive_digest = payload.receive_digest

    if payload.tags is not None:
        db.query(models.UserTag).filter(models.UserTag.user_id == current_user.id).delete()
        for tag_name in payload.tags:
            tag_name = tag_name.strip().lower()
            if not tag_name:
                continue
            tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
            if not tag:
                tag = models.Tag(name=tag_name)
                db.add(tag)
                db.flush()
            db.add(models.UserTag(user_id=current_user.id, tag_id=tag.id))

    db.commit()
    db.refresh(current_user)
    return current_user
