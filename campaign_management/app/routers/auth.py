from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.auth_service import register_user, login_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
    description="Tạo tài khoản người dùng mới. Kiểm tra email trùng và mã hóa mật khẩu bằng bcrypt."
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(user, db)

@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập nhận JWT Token",
    description="Xác thực email và mật khẩu, trả về Bearer JWT access token để truy cập các API được bảo vệ."
)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    return login_user(user_data, db)
