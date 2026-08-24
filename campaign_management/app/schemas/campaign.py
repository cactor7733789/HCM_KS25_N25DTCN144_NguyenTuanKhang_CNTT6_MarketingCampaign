from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic import BaseModel, Field, field_validator

class CampaignBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Tên campaign không được để trống")
        return value

class CampaignCreate(CampaignBase):
    owner_id: int | None = None

class CampaignUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class CampaignResponse(CampaignBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)