from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
import db.crud as crud

import schemas.schemas as schemas, models.models as models, db.crud as crud
from core.security import (auth_config, create_access_token, 
                           create_refresh_token, get_current_user,
                           verify_token, JWTError)


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/login",
    response_model=schemas.TokenResponse
)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    db_user = await crud.authenticate_user(db=db, username=form_data.username, password=form_data.password)
    if not db_user:
        raise HTTPException(status_code=404, detail="Invalid username or password")
    
    user_data = {
        "username": db_user.username,
        "email": db_user.email
    }
    
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)

    # set cookies
    response.set_cookie(
        key = auth_config.JWT_ACCESS_COOKIE_NAME,
        value = access_token,
        max_age = auth_config.JWT_ACCESS_TOKEN_EXPIRES_IN_MINUTES * 60,
        secure=False,   # True in production
        httponly=True,
        samesite="lax"
    )
    response.set_cookie(
        key = auth_config.JWT_REFRESH_COOKIE_NAME,
        value = refresh_token,
        max_age = auth_config.JWT_REFRESH_TOKEN_EXPIRES_IN_HOURS * 60 * 60,
        secure=False,   # True in production
        httponly=True,
        samesite="lax"
    )

    return schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer")

@router.post(
    "/refresh",
    response_model=schemas.TokenResponse
)
async def refresh_token(
    response: Response,
    refresh_request: str = Cookie(..., alias=auth_config.JWT_REFRESH_COOKIE_NAME),
    db: AsyncSession = Depends(get_db)
):
    
    try:
        token_data = verify_token(refresh_request, is_refresh=True)
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
        response.set_cookie(
            key = auth_config.JWT_ACCESS_COOKIE_NAME,
            value = access_token,
            max_age = auth_config.JWT_ACCESS_TOKEN_EXPIRES_IN_MINUTES * 60,
            secure=False,
            httponly=False    
        )
        response.set_cookie(
            key = auth_config.JWT_REFRESH_COOKIE_NAME,
            value = refresh_token,
            max_age = auth_config.JWT_REFRESH_TOKEN_EXPIRES_IN_HOURS * 60 * 60,
            secure=False,
            httponly=False
        )

        return schemas.TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer")

    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e))

    
    


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(auth_config.JWT_ACCESS_COOKIE_NAME)
    response.delete_cookie(auth_config.JWT_REFRESH_COOKIE_NAME) 
    return {"message": "User successfully logout"}