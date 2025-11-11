from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(min_length=8,
                          description="Пароль (минимум 8 символов)")


class UserBaseCreate(UserBase):
    pass


class PostBase(BaseModel):
    title: str
    text: str
    user_id: int


class PostBaseCreate(PostBase):
    pass
