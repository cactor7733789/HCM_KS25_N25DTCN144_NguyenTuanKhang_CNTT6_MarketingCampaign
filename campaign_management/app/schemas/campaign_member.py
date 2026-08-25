from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CampaignMemberBase(BaseModel):
    campaign_id: int
    user_id: int
    role: str = "MEMBER"

class CampaignMemberCreate(BaseModel):
    user_id: int

class CampaignMemberUpdate(BaseModel):
    role: str | None = None

class CampaignMemberResponse(CampaignMemberBase):
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
