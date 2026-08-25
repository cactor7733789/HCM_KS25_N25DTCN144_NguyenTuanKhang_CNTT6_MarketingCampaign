from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserLogin
from app.core.security import verify_password, create_access_token

def register_user(user: UserCreate,db: Session):
    existing_user = db.query(User).filter(
        User.email == user.email
        ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="email đã được đăng kí"
        )
    hashed_password = hash_password(user.password)
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(user_data: UserLogin, db: Session):
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()
    
    if not user or not verify_password(user_data.password,user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không đúng"
        )
    if not user.is_active:
        raise HTTPException(
        status_code=403,
        detail="Tài khoản đã bị vô hiệu hóa"
    )
    token_data = {
      "sub": user.id,
      "role": user.role
    }
    access_token = create_access_token(token_data)

    return {
      "access_token": access_token,
      "token_type": "bearer"
    }
