from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from app.db.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    full_name = Column(String(50), nullable=False)
    role = Column(Enum("USER", "ADMIN"), nullable=False, default="USER")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    campaigns = relationship("Campaign", back_populates="owner")
    campaign_members = relationship("CampaignMember",back_populates="user")
    assigned_tasks = relationship("CampaignTask",back_populates="assignee")