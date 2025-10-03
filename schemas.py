from pydantic import BaseModel, Field, validator
from typing import List, Optional


class TargetBase(BaseModel):
    name: str
    country: str
    notes: str = ""
    complete: bool = False


class TargetCreate(TargetBase):
    pass


class TargetUpdate(BaseModel):
    notes: Optional[str] = None
    complete: Optional[bool] = None


class Target(TargetBase):
    id: int
    mission_id: int
    
    class Config:
        from_attributes = True


class SpyCatBase(BaseModel):
    name: str
    years_of_experience: int
    breed: str
    salary: float


class SpyCatCreate(SpyCatBase):
    pass


class SpyCatUpdate(BaseModel):
    salary: float


class SpyCat(SpyCatBase):
    id: int
    
    class Config:
        from_attributes = True


class MissionBase(BaseModel):
    complete: bool = False


class MissionCreate(MissionBase):
    targets: List[TargetCreate] = Field(..., min_length=1, max_length=3)
    
    @validator('targets')
    def validate_targets_count(cls, v):
        if len(v) < 1 or len(v) > 3:
            raise ValueError('Mission must have between 1 and 3 targets')
        return v


class MissionUpdate(BaseModel):
    complete: Optional[bool] = None


class Mission(MissionBase):
    id: int
    cat_id: Optional[int] = None
    targets: List[Target] = []
    
    class Config:
        from_attributes = True


class MissionAssign(BaseModel):
    cat_id: int
