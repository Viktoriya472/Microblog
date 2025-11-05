from fastapi import APIRouter, status, Depends, HTTPException
from models.schemas import PostBase, PostBaseCreate
from models.posts import Post
from sqlalchemy import select, update, delete
from core.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/posts", tags=["posts"],)


@router.get("/", response_model=list[PostBase])
async def get_all_posts(db: AsyncSession = Depends(get_db)):
    posts = await db.scalars(select(Post))
    return posts.all()


@router.post("/", response_model=PostBase, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBaseCreate,
                      db: AsyncSession = Depends(get_db)):
    db_post = Post(**post.model_dump())
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post


@router.put('/{post_id}')
async def update_post(post_id: int, post: PostBaseCreate,
                      db: AsyncSession = Depends(get_db)):
    db_post_result = await db.scalars(select(Post).where(Post.id == post_id))
    db_post = db_post_result.first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")
    await db.execute(
        update(Post).where(Post.id == post_id).values(**post.model_dump())
    )
    await db.commit()
    await db.refresh(db_post)
    return db_post


@router.delete("/{post_id}")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db)):
    db_post_result = await db.scalars(select(Post).where(Post.id == post_id))
    db_post = db_post_result.first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")
    await db.execute(
        delete(Post).where(Post.id == post_id)
    )
    await db.commit()
    return {"message": "Post was deleted"}
