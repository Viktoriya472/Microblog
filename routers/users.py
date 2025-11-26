from fastapi import APIRouter, status, Depends, HTTPException
from models.schemas import UserBase, UserBaseCreate
from sqlalchemy import select, update, delete
from core.db_depends import get_db
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from routers.auth import verify_password, hash_password, create_access_token
from routers.auth import get_current_superuser, get_current_auth_user, create_refresh_token
import jwt
from config import SECRET_KEY, ALGORITHM

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
            detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email,
                                             "id": user.id})
    # Функция возвращает словарь с двумя ключами: access_token (содержит сгенерированный JWT)
    # Этот ответ соответствует стандарту OAuth2 и может быть использован клиентом для последующих авторизованных запросов.
    refresh_token = create_refresh_token(data={"sub": user.email,
                                               "id": user.id})
    return {"access_token": access_token,
            "refresh_token": refresh_token}


@router.post("/refresh-token")
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token")
    try:
        # декодируем рефреш-токен, проверяя его подпись и срок действия (exp)
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    # проверяем, существует ли активный пользователь с указанным email
    result = await db.scalars(select(User).where(User.email == email))
    user = result.first()
    if user is None:
        raise credentials_exception
    # создаём новый access-токен с тем же payload (sub, id) и сроком действия
    access_token = create_access_token(data={"sub": user.email,
                                             "id": user.id})
    return {"accsess_token": access_token}


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
