from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import jwt
from config import SECRET_KEY, ALGORITHM
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.db_depends import get_db
from sqlalchemy import select
from models.users import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# создаём объект OAuth2, который указывает, что эндпоинт логина находится по адресу /users/token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    # Создаёт копию входного словаря data, чтобы избежать изменения оригинала
    to_encode = data.copy()
    # Вычисляет время истечения токена
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Добавляет поле exp (expiration) в payload токена
    to_encode.update({"exp": expire,
                      "token_type": "access"})
    # Кодирует данные в JWT с использованием SECRET_KEY и алгоритма подписи
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire,
                      "token_type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_db)):
    # token- извлекает токен из заголовка запроса с помощью OAuth2PasswordBearer
    # Проверяет JWT и возвращает пользователя из базы
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",)
    try:
        # Декодирует JWT, проверяя его подпись с использованием SECRET_KEY и алгоритма
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    # Исключение, которое выбрасывается если токен истёк
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    # Этот блок перехватывает все остальные возможные ошибки, связанные с JWT
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.scalars(select(User).where(User.email == email))
    user = result.first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_superuser(
        current_superuser: User = Depends(get_current_user)):
    if not current_superuser.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only superuser can perform this action")


async def get_current_auth_user(
        current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only authorized users can perform this action")
