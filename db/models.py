from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from db.database import Base


class SpyCat(Base):
    __tablename__ = "spy_cats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    years_of_experience = Column(Integer, nullable=False)
    breed = Column(String, nullable=False)
    salary = Column(Float, nullable=False)

    missions = relationship("Mission", back_populates="cat")


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(Integer, ForeignKey("spy_cats.id"), nullable=True)
    complete = Column(Boolean, default=False, nullable=False)

    cat = relationship("SpyCat", back_populates="missions")
    targets = relationship(
        "Target", back_populates="mission", cascade="all, delete-orphan"
    )


class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    notes = Column(Text, default="")
    complete = Column(Boolean, default=False, nullable=False)

    mission = relationship("Mission", back_populates="targets")
