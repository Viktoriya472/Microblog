from fastapi import APIRouter, status, Depends, HTTPException
from models.schemas import PostBase, PostBaseCreate
from models.posts import Post
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from core.db_depends import get_db


router = APIRouter(prefix="/posts", tags=["posts"],)


@router.get("/", response_model=list[PostBase])
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.scalars(select(Post)).all()
    return posts


@router.post("/", response_model=PostBase, status_code=status.HTTP_201_CREATED)
def create_post(post: PostBaseCreate, db: Session = Depends(get_db)):
    db_post = Post(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.put('/{post_id}')
def update_post(post_id: int, post: PostBaseCreate,
                db: Session = Depends(get_db)):
    db_post = db.scalars(select(Post).where(Post.id == post_id)).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")
    db.execute(
        update(Post).where(Post.id == post_id).values(**post.model_dump())
    )
    db.commit()
    db.refresh(db_post)
    return post_id


@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.scalars(select(Post).where(Post.id == post_id)).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")
    db.execute(
        delete(Post).where(Post.id == post_id)
    )
    db.commit()
    return {"message": "Post was deleted"}
