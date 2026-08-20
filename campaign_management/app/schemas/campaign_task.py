from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CampaignTaskBase(BaseModel):
    campaign_id: int
    title: str
    description: str | None = None
    assignee_id: int | None = None
    status: str = "TODO"
    priority: str = "MEDIUM"
    due_date: datetime | None = None

class CampaignTaskCreate(CampaignTaskBase):
    pass

class CampaignTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    status: str | None = None
    priority: str | None = None
    due_date: datetime | None = None

class CampaignTaskResponse(CampaignTaskBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)