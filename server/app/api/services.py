from models.models import Users
from sqlalchemy.orm import Session
from schemas.schemas import UserCreate

def create_user(db: Session, data: UserCreate):
    user_instance = Users(**data.model_dump())
    db.add(user_instance)
    db.commit()
    db.refresh(user_instance)
    return user_instance

def get_users(db: Session):
    return db.query(Users).all()

def get_user(db: Session, user_id: int):
    return db.query(Users).filter(Users.id == user_id).first()
