from fastapi import APIRouter, status, Depends, HTTPException
from models.schemas import UserBase, UserBaseCreate
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from core.db_depends import get_db
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/users", tags=["users"],)


@router.get("/", response_model=list[UserBase])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    users = await db.scalars(select(User))
    return users.all()


@router.post("/", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBaseCreate,
                      db: AsyncSession = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.put('/{user_id}', response_model=UserBase)
async def update_user(user_id: int, user: UserBaseCreate,
                      db: AsyncSession = Depends(get_db)):
    db_user_result = await db.scalars(select(User).where(User.id == user_id))
    db_user = db_user_result.first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    await db.execute(
        update(User).where(User.id == user_id).values(**user.model_dump())
    )
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user_result = await db.scalars(select(User).where(User.id == user_id))
    db_user = db_user_result.first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    await db.execute(
        delete(User).where(User.id == user_id)
    )
    await db.commit()
    return {"message": "User was deleted"}
