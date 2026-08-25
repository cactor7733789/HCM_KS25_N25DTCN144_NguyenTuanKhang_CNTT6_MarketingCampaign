from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

TaskStatus = Literal["TODO", "IN_PROGRESS", "DONE"]
TaskPriority = Literal["LOW", "MEDIUM", "HIGH"]

class CampaignTaskBase(BaseModel):
    campaign_id: int
    title: str
    description: str | None = None
    assignee_id: int | None = None
    status: TaskStatus = "TODO"
    priority: TaskPriority = "MEDIUM"
    due_date: datetime | None = None

class CampaignTaskCreate(CampaignTaskBase):
    pass

class CampaignTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None

class CampaignTaskResponse(CampaignTaskBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskSort(BaseModel):
    created_at: bool = False
    due_date: bool = False
