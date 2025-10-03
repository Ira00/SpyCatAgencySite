from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import requests

from db.models import Base
from db.database import engine, get_db
from routers import cats, missions


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spy Cat Agency API", version="1.0.0")
app.include_router(cats.router)
app.include_router(missions.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Spy Cat Agency API",
        "docs": "/docs",
        "version": "1.0.0",
    }
