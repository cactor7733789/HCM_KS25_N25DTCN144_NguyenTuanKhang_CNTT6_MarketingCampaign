from fastapi import Depends,HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.core.security import decode_access_token
bearer_scheme = HTTPBearer()

def get_current_user(
      auth_info: HTTPAuthorizationCredentials = Depends(bearer_scheme),
      db: Session = Depends(get_db)
  ):
      token = auth_info.credentials
      payload = decode_access_token(token)
      user_id = payload.get("sub")
      if not user_id:
          raise HTTPException(
              status_code=401,
              detail="Token không chứa thông tin user"
          )
      try:
          user_id = int(user_id)
      except (TypeError, ValueError):
          raise HTTPException(
              status_code=401,
              detail="User ID trong token không hợp lệ"
          )
      user = db.query(User).filter(
          User.id == user_id
      ).first()
      if not user:
          raise HTTPException(
              status_code=401,
              detail="User không tồn tại"
          )
      if not user.is_active:
          raise HTTPException(
              status_code=403,
              detail="Tài khoản đã bị vô hiệu hóa"
          )
      return user

def require_admin(
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only Admin :3"
        )
    return current_user

