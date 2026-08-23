
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.dependencies.auth import require_admin
from sqlalchemy import or_

router = APIRouter(
      prefix="/users",
      tags=["Users"]
  )

#get me trả ttin user
@router.get("/me", response_model=UserResponse)
def get_my_profile(
      current_user: User = Depends(get_current_user)
  ):
      return current_user

@router.get("/", response_model=list[UserResponse])
def list_users(current_usr: User = Depends(require_admin),db: Session = Depends(get_db),search: str | None = None,is_active: bool | None = None):
      query = db.query(User)
      if is_active is not None:
          query = query.filter(User.is_active == is_active)
      if search:
          query = query.filter(
              or_(
                  User.email.ilike(f"%{search}%"),
                  User.full_name.ilike(f"%{search}%")
              )
          )
      return query.all()

