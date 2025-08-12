from pydantic import BaseModel, Field

class UsersBase(BaseModel):
    username: str
    firstname: str
    lastname: str
    age: int
    email: str
    phone: str 
    about: str = None

class UserCreate(UsersBase):
    pass

class User(UsersBase):
    id: int

    class config:
        from_attribute = True