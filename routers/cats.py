from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import requests

from db.schemas import SpyCat, SpyCatCreate, SpyCatUpdate
from db.database import get_db
import services.cats_service as crud

router = APIRouter(prefix="/cats", tags=["cats"])

CAT_API_URL = "https://api.thecatapi.com/v1/breeds"


def validate_breed(breed: str) -> bool:
    try:
        response = requests.get(CAT_API_URL)
        response.raise_for_status()
        breeds = response.json()
        valid_breeds = [b.get("name", "").lower() for b in breeds]
        return breed.lower() in valid_breeds
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to validate breed with TheCatAPI: {str(e)}",
        )


@router.post("/", response_model=SpyCat, status_code=status.HTTP_201_CREATED)
def create_spy_cat(cat: SpyCatCreate, db: Session = Depends(get_db)):
    if not validate_breed(cat.breed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid breed: {cat.breed}. Please use a valid breed from TheCatAPI.",
        )
    return crud.create_spy_cat(db, cat)


@router.get("/", response_model=List[SpyCat])
def list_spy_cats(db: Session = Depends(get_db)):
    return crud.list_spy_cats(db)


@router.get("/{cat_id}", response_model=SpyCat)
def get_spy_cat(cat_id: int, db: Session = Depends(get_db)):
    cat = crud.get_spy_cat(db, cat_id)
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spy cat with id {cat_id} not found",
        )
    return cat


@router.patch("/{cat_id}", response_model=SpyCat)
def update_spy_cat(
    cat_id: int, cat_update: SpyCatUpdate, db: Session = Depends(get_db)
):
    cat = crud.update_spy_cat(db, cat_id, cat_update)
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spy cat with id {cat_id} not found",
        )
    return cat


@router.delete("/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spy_cat(cat_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_spy_cat(db, cat_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spy cat with id {cat_id} not found",
        )
    return None
