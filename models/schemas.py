from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserBaseCreate(UserBase):
    pass


class PostBase(BaseModel):
    title: str
    text: str
    user_id: int


class PostBaseCreate(PostBase):
    pass
