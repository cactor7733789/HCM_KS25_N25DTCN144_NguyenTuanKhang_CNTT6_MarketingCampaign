import bcrypt
import jwt
from datetime import datetime, timedelta,timezone
from app.core.config import settings
from fastapi import HTTPException

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def create_access_token(data: dict) -> str:
      payload = data.copy()

      expire = datetime.now(timezone.utc) + timedelta(
          minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
      )

      payload.update({
          "exp": expire,
          "sub": str(data["sub"])
      })

      return jwt.encode(
          payload,
          settings.SECRET_KEY,
          algorithm=settings.ALGORITHM
      )

def decode_access_token(token:str):
    try:
         payload = jwt.decode(
              token,
              settings.SECRET_KEY,
              algorithms=[settings.ALGORITHM]
         )
         return payload
    except jwt.ExpiredSignatureError:
         raise HTTPException(
              status_code= 401,
              detail= "Token hết hạn"
         )
    except jwt.InvalidTokenError:
         raise HTTPException(
              status_code= 401,
              detail="không hợp lệ"
         )
    