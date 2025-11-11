from sqlalchemy import String, Boolean, DateTime
from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from typing import List


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    post: Mapped["List[Post]"] = relationship("Post", back_populates="user",
                                              cascade="all, delete-orphan")
