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

def update_user(db: Session, user: UserCreate, user_id: int):
    user_query = db.query(Users).filter(Users.id == user_id).first()
    if user_query:
        for key, value in user.model_dump().items():
            setattr(user_query, key, value)
        db.commit()
        db.refresh(user_query)
    return user_query

def delete_user(db: Session, user_id: int):
    user = db.query(Users).filter(Users.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user    