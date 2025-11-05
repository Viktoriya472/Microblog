from core.database import Base
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from models.users import User


class Post(Base):
    __tablename__ = "microblog_posts"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String(350))
    date: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),
                                         nullable=False)
    user: Mapped["User"] = relationship("User", back_populates='post')
