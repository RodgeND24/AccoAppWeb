# Pydantic-schemas for database tables

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from models.models import Language

'''Classes for Settings'''
class SettingsBase(BaseModel):
    firstname: str
    lastname: str | None = None
    description: str | None = None
    work: str | None = None
    language: str
    country: str | None = None
    theme: str

class SettingsCreate(SettingsBase):
    pass

class Settings(SettingsBase):
    id: int
    user_id: int
    is_online: bool = False

    class Config:
        from_attributes = True


'''Classes for Profits'''
class ProfitsBase(BaseModel):
    type: str
    sum: int
    date: date

class ProfitsCreate(ProfitsBase):
    pass

class Profits(ProfitsBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

'''Classes for Expenses'''
class ExpensesBase(BaseModel):
    shop: str
    sum: int
    date: date

class ExpensesCreate(ExpensesBase):
    pass

class Expenses(ExpensesBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

'''Classes for Users'''
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=10)


    @field_validator("password")
    def check_password(cls, value):
        not_access_symbols = '\'\"[]{};:=><|()~`\\'
        for symbol in not_access_symbols:
            if symbol in value:
                raise ValueError("Password contains invalid symbols")
        return value

class User(UserBase):
    id: int
    created_at: datetime
    uuid: str | None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=10)

'''Classes for Tokens'''
class RefreshTokenPayload(BaseModel):
    type: str
    sub: str

class AccessTokenPayload(RefreshTokenPayload):
    username: str
    email: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


'''Class for relationships'''
class SettingsRel(Settings):
    user: "User"

class UsersRel(User):
    settings: "Settings"