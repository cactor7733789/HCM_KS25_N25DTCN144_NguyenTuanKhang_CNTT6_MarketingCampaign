from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User

def get_my_profile(current_user: User):
      return current_user

def list_users(current_usr: User,db: Session,search: str | None = None,is_active: bool | None = None):
      query = db.query(User)
      if is_active is not None:
          query = query.filter(User.is_active == is_active)
      if search:
          query = query.filter(
              or_(
                   User.email.ilike(f"%{search}%"),
                   User.full_name.ilike(f"%{search}%"))
                   )
      return query.all()
