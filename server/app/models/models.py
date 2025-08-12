from db.db import Base
from sqlalchemy import Integer, Column, String

class Users(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    age = Column(Integer)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    about = Column(String)
