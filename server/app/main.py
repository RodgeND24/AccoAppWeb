from fastapi import FastAPI, Depends, HTTPException
import api.services, models.models, schemas.schemas
from db.db import engine, get_db
from sqlalchemy.orm import Session
from typing import Dict
from uvicorn import run

app = FastAPI()

@app.get("/users", tags=['Users'], response_model=list[schemas.schemas.User])
def get_all_users(db: Session = Depends(get_db)):
    return api.services.get_users(db)

@app.get("/users/{user_id}", tags=['Users'], response_model=schemas.schemas.User | Dict[str,str])
def get_all_users(user_id: int, db: Session = Depends(get_db)):
    user = api.services.get_user(db, user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User doesn't exist!")

@app.post("/users", tags=['Users'], response_model=schemas.schemas.User)
def create_new_user(user: schemas.schemas.UserCreate, db: Session = Depends(get_db)):
    return api.services.create_user(db, user)

# @app.delete("/users/{user_id}")

if __name__=="__main__":
    run("main:app", reload=True)