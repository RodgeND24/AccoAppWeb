from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, nullable=False, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    access_token = Column(String, unique=True)

    settings = relationship("Settings", back_populates="user", uselist=False)
    profits = relationship("Profits", back_populates="user")
    expenses = relationship("Expenses", back_populates="user")

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), unique=True, nullable=False)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    description = Column(String)
    work = Column(String)

    is_online = Column(Boolean, default=False)
    language = Column(String, default="ru")
    country = Column(String, index=True, default="Russia")
    theme = Column(String, default="Light")

    user = relationship("Users", back_populates="settings")

class Profits(Base):
    __tablename__ = "profit"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    type = Column(String)
    sum = Column(Numeric)
    date = Column(Date)

    user = relationship("Users", back_populates="profits")

class Expenses(Base):
    __tablename__ = "expense"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False))
    shop = Column(String)
    sum = Column(Numeric)
    date = Column(Date)

    user = relationship("Users", back_populates="expenses")


