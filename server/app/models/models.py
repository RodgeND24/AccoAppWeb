import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from db.database import Base

class Language(enum.Enum):
    ru = 'ru'
    en = 'en'

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, nullable=False, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    uuid = Column(String)
    # access_token = Column(String, unique=True)

    # settings = relationship("Settings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # profits = relationship("Profits", back_populates="user")
    # expenses = relationship("Expenses", back_populates="user")
    settings: Mapped["Settings"] = relationship("Settings", back_populates="user", cascade="all, delete")
    profits: Mapped["Profits"] = relationship("Profits", back_populates="user", cascade="all, delete")
    expenses: Mapped["Expenses"] = relationship("Expenses", back_populates="user", cascade="all, delete")

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    description = Column(String)
    work = Column(String)

    is_online = Column(Boolean, default=False)
    language: Mapped[Language]
    country = Column(String, index=True, default="Russia")
    theme = Column(String, default="Light")

    user: Mapped[Users] = relationship("Users", back_populates="settings")

class Profits(Base):
    __tablename__ = "profit"
    id = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    type = Column(String)
    sum = Column(Numeric)
    date = Column(Date)

    user = relationship("Users", back_populates="profits")

class Expenses(Base):
    __tablename__ = "expense"
    id = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    shop = Column(String)
    sum = Column(Numeric)
    date = Column(Date)

    user = relationship("Users", back_populates="expenses")


