from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import requests

import models
import schemas
from database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spy Cat Agency API", version="1.0.0")

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
            detail=f"Unable to validate breed with TheCatAPI: {str(e)}"
        )

@app.post("/cats", response_model=schemas.SpyCat, status_code=status.HTTP_201_CREATED)
def create_spy_cat(cat: schemas.SpyCatCreate, db: Session = Depends(get_db)):
    if not validate_breed(cat.breed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid breed: {cat.breed}. Please use a valid breed from TheCatAPI."
        )
    
    db_cat = models.SpyCat(**cat.model_dump())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@app.get("/cats", response_model=List[schemas.SpyCat])
def list_spy_cats(db: Session = Depends(get_db)):
    cats = db.query(models.SpyCat).all()
    return cats

@app.get("/cats/{cat_id}", response_model=schemas.SpyCat)
def get_spy_cat(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(models.SpyCat).filter(models.SpyCat.id == cat_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spy cat with id {cat_id} not found"
        )
    return cat

@app.patch("/cats/{cat_id}", response_model=schemas.SpyCat)
def update_spy_cat(cat_id: int, cat_update: schemas.SpyCatUpdate, db: Session = Depends(get_db)):
    cat = db.query(models.SpyCat).filter(models.SpyCat.id == cat_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spy cat with id {cat_id} not found"
        )
    
    cat.salary = cat_update.salary
    db.commit()
    db.refresh(cat)
    return cat

@app.delete("/cats/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spy_cat(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(models.SpyCat).filter(models.SpyCat.id == cat_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spy cat with id {cat_id} not found"
        )
    
    db.delete(cat)
    db.commit()
    return None

@app.post("/missions", response_model=schemas.Mission, status_code=status.HTTP_201_CREATED)
def create_mission(mission: schemas.MissionCreate, db: Session = Depends(get_db)):
    db_mission = models.Mission(complete=mission.complete)
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    
    for target_data in mission.targets:
        db_target = models.Target(
            mission_id=db_mission.id,
            **target_data.model_dump()
        )
        db.add(db_target)
    
    db.commit()
    db.refresh(db_mission)
    return db_mission

@app.get("/missions", response_model=List[schemas.Mission])
def list_missions(db: Session = Depends(get_db)):
    missions = db.query(models.Mission).all()
    return missions

@app.get("/missions/{mission_id}", response_model=schemas.Mission)
def get_mission(mission_id: int, db: Session = Depends(get_db)):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    return mission

@app.patch("/missions/{mission_id}", response_model=schemas.Mission)
def update_mission(mission_id: int, mission_update: schemas.MissionUpdate, db: Session = Depends(get_db)):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    
    if mission_update.complete is not None:
        if mission_update.complete:
            mission.complete = True
            mission.cat_id = None
        else:
            if mission.cat_id is not None:
                existing_mission = db.query(models.Mission).filter(
                    models.Mission.cat_id == mission.cat_id,
                    models.Mission.complete == False,
                    models.Mission.id != mission_id
                ).first()
                
                if existing_mission:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Cannot reactivate mission: cat {mission.cat_id} already has an active mission (id: {existing_mission.id})"
                    )
            
            mission.complete = False
    
    db.commit()
    db.refresh(mission)
    return mission

@app.delete("/missions/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(mission_id: int, db: Session = Depends(get_db)):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    
    if mission.cat_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete mission that is assigned to a cat"
        )
    
    db.delete(mission)
    db.commit()
    return None

@app.patch("/missions/{mission_id}/assign", response_model=schemas.Mission)
def assign_cat_to_mission(mission_id: int, assignment: schemas.MissionAssign, db: Session = Depends(get_db)):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    
    cat = db.query(models.SpyCat).filter(models.SpyCat.id == assignment.cat_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spy cat with id {assignment.cat_id} not found"
        )
    
    existing_mission = db.query(models.Mission).filter(
        models.Mission.cat_id == assignment.cat_id,
        models.Mission.complete == False
    ).first()
    
    if existing_mission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cat {assignment.cat_id} already has an active mission (id: {existing_mission.id})"
        )
    
    mission.cat_id = assignment.cat_id
    db.commit()
    db.refresh(mission)
    return mission

@app.patch("/missions/{mission_id}/targets/{target_id}", response_model=schemas.Target)
def update_target(
    mission_id: int,
    target_id: int,
    target_update: schemas.TargetUpdate,
    db: Session = Depends(get_db)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission with id {mission_id} not found"
        )
    
    target = db.query(models.Target).filter(
        models.Target.id == target_id,
        models.Target.mission_id == mission_id
    ).first()
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target with id {target_id} not found in mission {mission_id}"
        )
    
    if target_update.notes is not None:
        if target.complete or mission.complete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update notes: target or mission is already completed"
            )
        target.notes = target_update.notes
    
    if target_update.complete is not None:
        target.complete = target_update.complete
    
    db.commit()
    db.refresh(target)
    return target

@app.get("/")
def root():
    return {
        "message": "Welcome to Spy Cat Agency API",
        "docs": "/docs",
        "version": "1.0.0"
    }