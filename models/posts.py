from core.database import Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Post(Base):
    __tablename__ = "microblog_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    text = Column(String(350))
    date = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="posts")
