from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(min_length=8,
                          description="Пароль (минимум 8 символов)")


class UserBaseCreate(UserBase):
    pass


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PostBase(BaseModel):
    title: str
    text: str
    user_id: int


class PostBaseCreate(PostBase):
    pass


class ReviewBase(BaseModel):
    comment: str
    grade: float
    post_id: int
    user_id: int


class CreateReview(ReviewBase):
    pass
