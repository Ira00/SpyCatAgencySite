from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.schemas import (
    Mission,
    MissionAssign,
    MissionCreate,
    MissionUpdate,
    Target,
    TargetUpdate,
)
from db.database import get_db
import services.mission_service as crud

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("/", response_model=Mission, status_code=status.HTTP_201_CREATED)
def create_mission(mission: MissionCreate, db: Session = Depends(get_db)):
    return crud.create_mission(db, mission)


@router.get("/", response_model=List[Mission])
def list_missions(db: Session = Depends(get_db)):
    return crud.list_missions(db)


@router.get("/{mission_id}", response_model=Mission)
def get_mission(mission_id: int, db: Session = Depends(get_db)):
    mission = crud.get_mission(db, mission_id)
    if not mission:
        raise HTTPException(
            status_code=404, detail=f"Mission with id {mission_id} not found"
        )
    return mission


@router.patch("/{mission_id}", response_model=Mission)
def update_mission(
    mission_id: int, mission_update: MissionUpdate, db: Session = Depends(get_db)
):
    result = crud.update_mission(db, mission_id, mission_update)
    if result is None:
        raise HTTPException(
            status_code=404, detail=f"Mission with id {mission_id} not found"
        )
    if result == "cat_conflict":
        raise HTTPException(
            status_code=400,
            detail="Cannot reactivate mission: cat already has an active mission",
        )
    return result


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(mission_id: int, db: Session = Depends(get_db)):
    result = crud.delete_mission(db, mission_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail=f"Mission with id {mission_id} not found"
        )
    if result == "assigned":
        raise HTTPException(
            status_code=400, detail="Cannot delete mission that is assigned to a cat"
        )
    return None


@router.patch("/{mission_id}/assign", response_model=Mission)
def assign_cat_to_mission(
    mission_id: int, assignment: MissionAssign, db: Session = Depends(get_db)
):
    mission, error = crud.assign_cat_to_mission(db, mission_id, assignment)
    if error == "mission_not_found":
        raise HTTPException(
            status_code=404, detail=f"Mission with id {mission_id} not found"
        )
    if error == "cat_not_found":
        raise HTTPException(
            status_code=404, detail=f"Spy cat with id {assignment.cat_id} not found"
        )
    if error == "cat_conflict":
        raise HTTPException(
            status_code=400,
            detail=f"Cat {assignment.cat_id} already has an active mission",
        )
    return mission


@router.patch("/{mission_id}/targets/{target_id}", response_model=Target)
def update_target(
    mission_id: int,
    target_id: int,
    target_update: TargetUpdate,
    db: Session = Depends(get_db),
):
    target, error = crud.update_target(db, mission_id, target_id, target_update)
    if error == "mission_not_found":
        raise HTTPException(
            status_code=404, detail=f"Mission with id {mission_id} not found"
        )
    if error == "target_not_found":
        raise HTTPException(
            status_code=404,
            detail=f"Target with id {target_id} not found in mission {mission_id}",
        )
    if error == "cannot_update_notes":
        raise HTTPException(
            status_code=400,
            detail="Cannot update notes: target or mission is already completed",
        )
    return target
