from sqlalchemy.orm import Session
import models
from db.schemas import SpyCat, SpyCatCreate, SpyCatUpdate


def create_spy_cat(db: Session, cat: SpyCatCreate) -> models.SpyCat:
    db_cat = models.SpyCat(**cat.model_dump())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


def list_spy_cats(db: Session):
    return db.query(models.SpyCat).all()


def get_spy_cat(db: Session, cat_id: int):
    return db.query(models.SpyCat).filter(models.SpyCat.id == cat_id).first()


def update_spy_cat(db: Session, cat_id: int, cat_update: SpyCatUpdate):
    cat = get_spy_cat(db, cat_id)
    if not cat:
        return None
    cat.salary = cat_update.salary
    db.commit()
    db.refresh(cat)
    return cat


def delete_spy_cat(db: Session, cat_id: int) -> bool:
    cat = get_spy_cat(db, cat_id)
    if not cat:
        return False
    db.delete(cat)
    db.commit()
    return True
