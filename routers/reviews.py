from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from core.db_depends import get_db
from models.reviews import Review
from models.posts import Post
from models.users import User
from models.schemas import ReviewBase, CreateReview
from routers.auth import get_current_auth_user


router = APIRouter(prefix="/reviews", tags=["review"])


@router.get("/", response_model=list[ReviewBase])
async def all_reviews(db: AsyncSession = Depends(get_db)):
    review = await db.scalars(select(Review))
    return review.all()


@router.get("/{post_id}")
async def post_reviews(post_id:  int, db: AsyncSession = Depends(get_db)):
    post = await db.scalar(select(Post).where(
        Post.id == post_id))
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no post found"
        )
    review = await db.scalars(select(Review).where(
        Review.post_id == post_id))
    return review.all()


@router.post("/", response_model=ReviewBase,
             status_code=status.HTTP_201_CREATED)
async def create_review(review: CreateReview,
                        db: AsyncSession = Depends(get_db),
                        user_auth: User = Depends(get_current_auth_user)):

    post = await db.scalar(select(Post).where(
        Post.id == review.post_id))
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no post found'
        )
    db_review = Review(**review.model_dump())
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review


@router.delete('/{review_id}')
async def delete_reviews(review_id: int,
                         db: AsyncSession = Depends(get_db),
                         get_user: User = Depends(get_current_auth_user)):
    db_review_result = await db.scalars(select(Review).where(
        Review.id == review_id))
    db_review = db_review_result.first()
    if not db_review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Review not found")
    await db.execute(delete(Review).where(
            Review.id == review_id))
    await db.commit()
    return {"message": "Review was deleted"}
