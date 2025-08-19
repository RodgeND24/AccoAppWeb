from sqlalchemy import (select, insert, update, delete, case, func, 
                        and_, or_, not_, between, cast, desc, asc, 
                        distinct, text, null, extract,
                        union, union_all, intersect, except_, join)
from sqlalchemy.orm import (aliased, joinedload, selectinload, subqueryload)
from sqlalchemy.sql import (expression, label, literal_column, table, exists, any_, all_)
from sqlalchemy.ext.asyncio import AsyncSession
import models.models as models, schemas.schemas as schemas
from passlib.context import CryptContext
# import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

'''User operations'''
# get user by id
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Users).filter(models.Users.id == user_id))
    return result.scalars().first()

# get user by email
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.Users).filter(models.Users.username == username))
    return result.scalars().first()

# get all users
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Users).offset(skip).limit(limit))
    return result.scalars().all()

# create user
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    # hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.getsalt())
    hashed_password = pwd_context.hash(user.password)
    db_user = models.Users(username = user.username, email = user.email, hashed_password = hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Settings).filter(models.Settings.user_id == user_id))
    user = result.scalars().first()
    if user:
        db.execute()

'''Settings operations'''
# Create user's settings
async def create_settings(db: AsyncSession, settings: schemas.SettingsCreate, user_id: int):
    db_settings = models.Settings(**settings.dict(), user_id = user_id)
    db.add(db_settings)
    await db.commit()
    await db.refresh(db_settings)
    return db_settings

# Update user's settings
async def update_settings(db: AsyncSession, settings: schemas.Settings, user_id: int):
    result = await db.execute(select(models.Settings).filter(models.Settings.user_id == user_id))
    user = result.scalars().first()
    if user:
        user.firstname = settings.firstname
        user.lastname = settings.lastname
        user.description = settings.description
        user.is_online = settings.is_online
        user.language = user.language
        user.country = user.country
        user.theme = settings.theme

        db.flush()
        db.commit()
    return user
    
# Get user's settings
async def get_settings(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Settings).filter(models.Settings.user_id == user_id))
    return result.scalars().first()
