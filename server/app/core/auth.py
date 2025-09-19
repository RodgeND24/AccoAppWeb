from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, Annotated, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
import db.crud as crud

import schemas.schemas as schemas, models.models as models, db.crud as crud
from core.security import (auth_config, create_access_token, 
                           create_refresh_token, get_current_user,
                           verify_token, JWTError)
from core.utils import auth_config, set_cookies



router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post(
    "/login",
    summary='User sing in',
    response_model=schemas.TokenResponse
)
async def login(
    response: Response,
    user_data: schemas.UserLogin,
    db: AsyncSession = Depends(get_db)
):

    db_user = await crud.authenticate_user(db=db, username=user_data.username, password=user_data.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    user_data = {
        "sub": db_user.username,
        "username": db_user.username,
        "email": db_user.email
    }
    
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)

    # set cookies
    set_cookies(response, access_token, refresh_token)

    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer")

@router.post(
        "/register", 
         summary='User sing up', 
         response_model=schemas.User
         )
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db=db, username = user.username)
    if db_user:
       raise HTTPException(status_code=400, detail="User already exist")
    return await crud.create_user(db=db, user = user)

@router.post(
    "/refresh",
    response_model=schemas.TokenResponse
)
async def refresh_token(
    response: Response,
    # refresh_request: str = Cookie(..., alias=auth_config.JWT_REFRESH_COOKIE_NAME),
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    
    try:
        token_data = verify_token(refresh_token, is_refresh=True)
        username = token_data.get("sub")

        if not username:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        db_user = await crud.get_user_by_username(db=db, username=username)
        # need add the checking of "is_active" setting
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found or not active")

        user_data = {
        "username": db_user.username,
        "email": db_user.email
        }

        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)

        # set cookies
        set_cookies(response, access_token, refresh_token)
        # response = RedirectResponse("/", status_code=302)

        return schemas.TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer")

    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post(
            "/verify-token",
            # response_model=bool
)  
async def verify_token_from_client(token_data: schemas.TokenRequest):
    try:
        verify_token(token_data.token, token_data.is_refresh)
        return token_data.token
    except:
        raise HTTPException(status_code=401, detail='Invalid token')
    


@router.post("/logout")
async def logout(response: Response):
    # response = RedirectResponse("/", status_code=302)
    response.delete_cookie(auth_config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(auth_config.JWT_REFRESH_COOKIE_NAME) 
    return {"message": "User successfully logout"}