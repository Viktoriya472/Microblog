from fastapi import APIRouter, status, Depends, HTTPException
from models.schemas import UserBase, UserBaseCreate
from sqlalchemy import select, update, delete
from core.db_depends import get_db
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from routers.auth import verify_password, hash_password, create_access_token
from routers.auth import get_current_superuser, get_current_auth_user


router = APIRouter(prefix="/users", tags=["users"],)


@router.get("/", response_model=list[UserBase])
async def get_all_users(current_user: User = Depends(get_current_superuser),
                        db: AsyncSession = Depends(get_db)):
    users = await db.scalars(select(User))
    return users.all()


@router.post("/", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBaseCreate,
                      db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(User).where(User.email == user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")
    db_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(db_user)
    await db.commit()
    return db_user


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    result = await db.scalars(
        select(User).where(User.email == form_data.username))
    user = result.first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "id": user.id})
    # Функция возвращает словарь с двумя ключами: access_token (содержит сгенерированный JWT)
    # и token_type (с значением bearer, указывающим, что это токен типа Bearer для использования в заголовках Authorization).
    # Этот ответ соответствует стандарту OAuth2 и может быть использован клиентом для последующих авторизованных запросов.
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/{user_id}", response_model=UserBase)
async def update_user(user_id: int,
                      user: UserBaseCreate,
                      db: AsyncSession = Depends(get_db),
                      auth_user: User = Depends(get_current_auth_user),):
    db_user_result = await db.scalars(select(User).where(User.id == user_id))
    db_user = db_user_result.first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    await db.execute(
        update(User).where(User.id == user_id).values(
            name=user.name,
            email=user.email,
            password=hash_password(user.password))
        )
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
async def delete_user(user_id: int,
                      auth_user: User = Depends(get_current_auth_user),
                      db: AsyncSession = Depends(get_db)):
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
