import models.models as models, schemas.schemas as schemas
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from db.database import engine, get_db
import db.crud as crud

router = APIRouter(prefix="/users")

'''Users'''
@router.get(
        "", 
         tags=['Users'], 
         summary = "Get all users", 
         response_model=list[schemas.User]
         )
async def get_all_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    users = await crud.get_users(db=db, skip = skip, limit = limit)
    return users

@router.get(
        "/username/{username}", 
         tags=['Users'], 
         summary = "Get users by username", 
         response_model=schemas.User
         )
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db=db, username = username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get(
        "/id/{user_id}", 
         tags=['Users'], 
         summary = "Get users by id", 
         response_model=schemas.User
         )
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db=db, user_id = user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post(
        "", 
         tags=['Users'], 
         summary = "Create user", 
         response_model=schemas.User
         )
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db=db, email = user.email)
    if db_user:
       raise HTTPException(status_code=400, detail="User already exist")
    return await crud.create_user(db=db, user = user)

@router.delete(
        "/id/{user_id}", 
         tags=['Users'], 
         summary = "Delete user by id", 
         response_model=schemas.User
         )
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User don't exist")
    return await crud.delete_user_by_id(db=db, user_id=user_id)

'''Settings'''
@router.get(
        "/{user_id}/settings", 
         tags=['Settings'], 
         summary = "Get user's settings", 
         response_model=schemas.Settings
         )
async def get_settings(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user_settings = await crud.get_settings(db=db, user_id = user_id)
    if not db_user_settings:
        raise HTTPException(status_code=404, detail="User's settings not found")
    return db_user_settings

@router.post(
        "/{user_id}/settings", 
         tags=['Settings'], 
         summary = "Set all user's settings", 
         response_model=schemas.SettingsCreate
         )
async def create_settings(user_id: int, settings: schemas.SettingsCreate, db: AsyncSession = Depends(get_db)):
   return await crud.create_settings(db=db, settings=settings, user_id=user_id)