from fastapi import HTTPException, Security, Depends, Cookie, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
import jwt, uuid
from core.utils import verify_password
from typing import Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import db.crud as crud
from db.database import get_db


# import environment variables
load_dotenv()
BASE_DIR = Path(__file__).parent

with open(BASE_DIR/os.getenv("JWT_PRIVATE_KEY_PATH"), 'r') as file:
    JWT_PRIVATE_KEY = file.read()
with open(BASE_DIR/os.getenv("JWT_PUBLIC_KEY_PATH"), 'r') as file:
    JWT_PUBLIC_KEY = file.read()

class JWTConfig(BaseModel):

    JWT_ALGORITHM_: str = os.getenv("JWT_ALGORITHM")
    
    JWT_ACCESS_TOKEN_EXPIRES: str = timedelta(minutes=1)
    JWT_ACCESS_TOKEN_EXPIRES_IN_MINUTES: str = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_IN_MINUTES"))
    
    JWT_REFRESH_TOKEN_EXPIRES: str = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES_IN_HOURS: str = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_IN_HOURS"))
    
    JWT_ACCESS_COOKIE_NAME: str = os.getenv("JWT_ACCESS_COOKIE_NAME")
    JWT_REFRESH_COOKIE_NAME: str = os.getenv("JWT_REFRESH_COOKIE_NAME")
    
    JWT_TOKEN_LOCATION: list[str] = ["headers", "cookies"]
    
    JWT_PRIVATE_KEY: str = None
    JWT_PUBLIC_KEY: str = None

# custom HTTPBearer
class AuthHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request, access_token: str = Cookie(None)) -> Optional[HTTPAuthorizationCredentials]:
        # check headers
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, credentials = get_authorization_scheme_param(authorization)
            if not (scheme and credentials):
                if self.auto_error:
                    raise HTTPException(status_code=401, detail="Not authentication", headers={"WWW-Authenticate": "Bearer"})
                return None
            if scheme.lower() != "bearer":
                if self.auto_error:
                    raise HTTPException(status_code=401, detail="Invalid authentication scheme", headers={"WWW-Authenticate": "Bearer"})
                return None
            return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)
        
        # check cookies
        if access_token:
            return HTTPAuthorizationCredentials(scheme="Bearer", credentials=access_token)   
        
        if self.auto_error:
            raise HTTPException(status_code=401, detail="Not authentication", headers={"WWW-Authenticate": "Bearer"})
        return None


auth_config = JWTConfig(JWT_PRIVATE_KEY=JWT_PRIVATE_KEY, JWT_PUBLIC_KEY=JWT_PUBLIC_KEY)
security = AuthHTTPBearer()


def create_access_token(user_data: dict[str, str]) -> str:
    payload = {
        "type": "access",
        "sub": user_data.get("username"),
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "exp": datetime.now(tz=timezone.utc) + auth_config.JWT_ACCESS_TOKEN_EXPIRES,
        "iat": datetime.now(tz=timezone.utc),
        "jti": str(uuid.uuid4())
    }

    token = jwt.encode(
        payload = payload,
        key = auth_config.JWT_PRIVATE_KEY,
        algorithm = auth_config.JWT_ALGORITHM_
    )
    return token

def create_refresh_token(user_data: dict[str, str]) -> str:
        payload = {
            "type": "refresh",
            "sub": user_data.get("username"),
            "exp": datetime.now(tz=timezone.utc) + auth_config.JWT_REFRESH_TOKEN_EXPIRES,
            "iat": datetime.now(tz=timezone.utc),
            "jti": str(uuid.uuid4())
        }

        token = jwt.encode(
            payload = payload,
            key = auth_config.JWT_PRIVATE_KEY,
            algorithm = auth_config.JWT_ALGORITHM_
        )
        return token

class JWTError(Exception):
    pass

def verify_token(token: str, is_refresh: bool = False):
    try:
        token_data = jwt.decode(jwt = token, key = auth_config.JWT_PUBLIC_KEY, algorithms = [auth_config.JWT_ALGORITHM_])
        type = token_data.get("type")

        if is_refresh and type != "refresh":
            raise JWTError("Invalid token type")
        if not is_refresh and type != "access":
            raise JWTError("Invalid token type")
        
        return token_data

    except jwt.ExpiredSignatureError:
        raise JWTError("Token expired")
    except jwt.InvalidTokenError:
        raise JWTError("Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: AsyncSession = Depends(get_db)):
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        username = token_data.get("username")
        email = token_data.get("email")

        if not username or not email:
            raise JWTError("Invalid token payload")

        db_user = await crud.get_user_by_username(db=db, username=username)
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid token or username")

        return db_user

    except JWTError as e:
        raise HTTPException(status_code=401, detail=str(e), headers={"WWW-Authenticate": "Bearer"})