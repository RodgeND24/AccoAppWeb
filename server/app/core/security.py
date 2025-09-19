from fastapi import HTTPException, Security, Depends, Cookie, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from datetime import datetime, timezone
import jwt, uuid
from core.utils import verify_password, auth_config
from typing import Annotated, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import db.crud as crud
from db.database import get_db

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

def verify_token(token: str, is_refresh: str):
    try:
        token_data = jwt.decode(jwt = token, key = auth_config.JWT_PUBLIC_KEY, algorithms = [auth_config.JWT_ALGORITHM_])
        type = token_data.get("type")

        if int(is_refresh) and type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        if not int(is_refresh) and type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        return token_data

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: AsyncSession = Depends(get_db)):
    try:
        token = credentials.credentials
        token_data = verify_token(token, is_refresh='0')
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