from fastapi import APIRouter, status, Depends, HTTPException
from models.schemas import UserBase, UserBaseCreate
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from core.db_depends import get_db
from models.users import User


router = APIRouter(prefix="/users", tags=["users"],)


@router.get("/", response_model=list[UserBase])
def get_all_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User)).all()
    return users


@router.post("/", response_model=UserBase, status_code=status.HTTP_201_CREATED)
def create_user(user: UserBaseCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.put('/{user_id}', response_model=UserBase)
def update_user(user_id: int, user: UserBaseCreate,
                db: Session = Depends(get_db)):
    db_user = db.scalars(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    db.execute(
        update(User).where(User.id == user_id).values(**user.model_dump())
    )
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.scalars(select(User).where(User.id == user_id)).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    db.execute(
        delete(User).where(User.id == user_id)
    )
    db.commit()
    return {"message": "User was deleted"}
