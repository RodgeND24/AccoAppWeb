from fastapi import FastAPI, Depends, HTTPException
import api.services, models.models, schemas.schemas
from db.db import engine, get_db
from sqlalchemy.orm import Session
from typing import Dict
from uvicorn import run

app = FastAPI()

@app.get(
        "/users", 
         tags=['Users'], 
         summary = "Get all users", 
         response_model=list[schemas.schemas.User]
         )
def get_all_users(db: Session = Depends(get_db)):
    return api.services.get_users(db)

@app.get(
        "/users/{user_id}",
         tags = ['Users'],
         summary = "Get user by user_id",
         response_model = schemas.schemas.User | Dict[str,str]
         )
def get_all_users(user_id: int, db: Session = Depends(get_db)):
    user = api.services.get_user(db, user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User doesn't exist!")

@app.post(
        "/users", 
        tags=['Users'], 
        summary="Create new user",
        response_model=schemas.schemas.User
        )
def create_new_user(user: schemas.schemas.UserCreate, db: Session = Depends(get_db)):
    return api.services.create_user(db, user)

@app.put(
        "/users/{user_id}", 
        tags=['Users'], 
        summary="Update user by user_id",
        response_model=schemas.schemas.User
        )
def update_user(user: schemas.schemas.UserCreate, user_id: int, db: Session = Depends(get_db)):
    db_update = api.services.update_user(db, user, user_id)
    if not db_update:
        raise HTTPException(status_code=404, detail="User not found!")
    return db_update
        

@app.delete(
        "/users/{user_id}", 
        tags=['Users'], 
        summary="Delete user by user_id",
        response_model=schemas.schemas.User
        )
def delete_old_user(user_id: int, db: Session = Depends(get_db)):
    user_delete = api.services.delete_user(db, user_id)
    if not user_delete:
        raise HTTPException(status_code=404, detail="User not found!")
    return user_delete

if __name__=="__main__":
    run("main:app", reload=True)