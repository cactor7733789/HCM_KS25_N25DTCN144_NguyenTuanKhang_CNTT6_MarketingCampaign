from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.db.database import Base
from sqlalchemy.orm import relationship

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    owner = relationship("User", back_populates="campaigns")
    campaign_members = relationship("CampaignMember", back_populates="campaign")
    tasks = relationship("CampaignTask", back_populates="campaign")