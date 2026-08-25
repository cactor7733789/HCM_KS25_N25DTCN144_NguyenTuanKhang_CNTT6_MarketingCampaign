from fastapi import APIRouter, Depends, status
from app.dependencies.auth import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import UserResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.user_service import get_my_profile as get_my_profile_service, list_users as list_users_service

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Xem thông tin cá nhân",
    description="Trả về thông tin hồ sơ của người dùng hiện tại từ JWT token (không bao gồm password_hash)."
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return get_my_profile_service(current_user)

@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Danh sách người dùng (Chỉ Admin)",
    description="Dành riêng cho Admin. Hỗ trợ tìm kiếm theo họ tên/email và lọc theo trạng thái hoạt động (is_active)."
)
def list_users(
    current_usr: User = Depends(require_admin),
    db: Session = Depends(get_db),
    search: str | None = None,
    is_active: bool | None = None
):
    return list_users_service(current_usr, db, search, is_active)
