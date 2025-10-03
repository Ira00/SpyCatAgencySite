from sqlalchemy.orm import Session
import models
from db.schemas import (
    Mission,
    MissionAssign,
    MissionCreate,
    MissionUpdate,
    TargetUpdate,
)


def create_mission(db: Session, mission: MissionCreate) -> models.Mission:
    db_mission = models.Mission(complete=mission.complete)
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)

    for target_data in mission.targets:
        db_target = models.Target(mission_id=db_mission.id, **target_data.model_dump())
        db.add(db_target)

    db.commit()
    db.refresh(db_mission)
    return db_mission


def list_missions(db: Session):
    return db.query(models.Mission).all()


def get_mission(db: Session, mission_id: int):
    return db.query(models.Mission).filter(models.Mission.id == mission_id).first()


def update_mission(db: Session, mission_id: int, mission_update: MissionUpdate):
    mission = get_mission(db, mission_id)
    if not mission:
        return None

    if mission_update.complete is not None:
        if mission_update.complete:
            mission.complete = True
            mission.cat_id = None
        else:
            if mission.cat_id is not None:
                existing_mission = (
                    db.query(models.Mission)
                    .filter(
                        models.Mission.cat_id == mission.cat_id,
                        models.Mission.complete == False,
                        models.Mission.id != mission_id,
                    )
                    .first()
                )

                if existing_mission:
                    return "cat_conflict"

            mission.complete = False

    db.commit()
    db.refresh(mission)
    return mission


def delete_mission(db: Session, mission_id: int):
    mission = get_mission(db, mission_id)
    if not mission:
        return None
    if mission.cat_id is not None:
        return "assigned"
    db.delete(mission)
    db.commit()
    return True


def assign_cat_to_mission(db: Session, mission_id: int, assignment: MissionAssign):
    mission = get_mission(db, mission_id)
    if not mission:
        return None, "mission_not_found"

    cat = db.query(models.SpyCat).filter(models.SpyCat.id == assignment.cat_id).first()
    if not cat:
        return None, "cat_not_found"

    existing_mission = (
        db.query(models.Mission)
        .filter(
            models.Mission.cat_id == assignment.cat_id, models.Mission.complete == False
        )
        .first()
    )

    if existing_mission:
        return None, "cat_conflict"

    mission.cat_id = assignment.cat_id
    db.commit()
    db.refresh(mission)
    return mission, None


def update_target(
    db: Session, mission_id: int, target_id: int, target_update: TargetUpdate
):
    mission = get_mission(db, mission_id)
    if not mission:
        return None, "mission_not_found"

    target = (
        db.query(models.Target)
        .filter(models.Target.id == target_id, models.Target.mission_id == mission_id)
        .first()
    )

    if not target:
        return None, "target_not_found"

    if target_update.notes is not None:
        if target.complete or mission.complete:
            return None, "cannot_update_notes"
        target.notes = target_update.notes

    if target_update.complete is not None:
        target.complete = target_update.complete

    db.commit()
    db.refresh(target)
    return target, None
