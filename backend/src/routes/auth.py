"""Authentication routes for registration and login."""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from src.core.auth.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# In-memory user store for development
# Format: {email: {"email": email, "password": hashed_password}}
users_db = {}

class UserBase(BaseModel):
    """Base user model."""
    email: str  # Plain str to avoid strict RFC-validation rejecting common inputs

class UserCreate(UserBase):
    """User registration model."""
    password: str

class UserLogin(UserBase):
    """User login model."""
    password: str

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user."""
    if user.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = hash_password(user.password)
    users_db[user.email] = {
        "email": user.email,
        "password": hashed_password
    }
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login an existing user."""
    db_user = users_db.get(user.email)
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token}
