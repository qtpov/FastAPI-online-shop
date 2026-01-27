from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import hash_password
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.schemas.user import UserCreate, UserRead
from app.models.user import User
from app.core.database import get_db
from app.api.deps import get_refresh_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register", response_model=UserRead)
async def register(user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == user.email))
    
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    new_user = User(email=user.email, hashed_password=hash_password(user.password), role=user.role)  
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)



    return new_user

@router.post("/login")
async def login(email: str, password: str,db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh(user_id: int = Depends(get_refresh_user)):
    new_access_token = create_access_token(user_id)
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

