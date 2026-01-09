from core.database import Base
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    comment:  Mapped[str] = mapped_column(String())
    comment_date: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now())
    grade: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"),
                                         nullable=False)
    post: Mapped["Post"] = relationship("Post", back_populates="reviews")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),
                                         nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="reviews")
