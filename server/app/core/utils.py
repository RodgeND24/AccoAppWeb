from fastapi import Response
from pydantic import BaseModel
from datetime import timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv
from pathlib import Path
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password:str, hash: str) -> bool:
    return pwd_context.verify(password, hash)

# import environment variables
load_dotenv()
BASE_DIR = Path(__file__).parent

with open(BASE_DIR/os.getenv("JWT_PRIVATE_KEY_PATH"), 'r') as file:
    JWT_PRIVATE_KEY = file.read()
with open(BASE_DIR/os.getenv("JWT_PUBLIC_KEY_PATH"), 'r') as file:
    JWT_PUBLIC_KEY = file.read()

class JWTConfig(BaseModel):

    JWT_ALGORITHM_: str = os.getenv("JWT_ALGORITHM")
    
    JWT_ACCESS_TOKEN_EXPIRES: str = timedelta(minutes=30)
    JWT_ACCESS_TOKEN_EXPIRES_IN_MINUTES: str = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_IN_MINUTES"))
    
    JWT_REFRESH_TOKEN_EXPIRES: str = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES_IN_HOURS: str = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_IN_HOURS"))
    
    JWT_ACCESS_COOKIE_NAME: str = os.getenv("JWT_ACCESS_COOKIE_NAME")
    JWT_REFRESH_COOKIE_NAME: str = os.getenv("JWT_REFRESH_COOKIE_NAME")
    
    JWT_TOKEN_LOCATION: list[str] = ["headers", "cookies"]
    
    JWT_PRIVATE_KEY: str = None
    JWT_PUBLIC_KEY: str = None

auth_config = JWTConfig(JWT_PRIVATE_KEY=JWT_PRIVATE_KEY, JWT_PUBLIC_KEY=JWT_PUBLIC_KEY)

def set_cookies(response: Response, access_token: str, refresh_token: str):
    # set cookies
    response.set_cookie(
        key = auth_config.JWT_ACCESS_COOKIE_NAME,
        value = access_token,
        max_age = auth_config.JWT_ACCESS_TOKEN_EXPIRES * 60,
        secure=False,   # True in production
        httponly=False,
        samesite="lax",
        # domain='domain.com'
    )
    response.set_cookie(
        key = auth_config.JWT_REFRESH_COOKIE_NAME,
        value = refresh_token,
        max_age = auth_config.JWT_REFRESH_TOKEN_EXPIRES * 60 * 60,
        secure=False,   # True in production
        httponly=False,
        samesite="lax",
        # domain='domain.com'
    )
