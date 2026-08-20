from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base


class CampaignMember(Base):
    __tablename__ = "campaign_members"

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(Enum("OWNER", "MEMBER"), nullable=False)
    joined_at = Column(DateTime, nullable=False, default=datetime.now)

    campaign = relationship("Campaign", back_populates="campaign_members")
    user = relationship("User", back_populates="campaign_members")
