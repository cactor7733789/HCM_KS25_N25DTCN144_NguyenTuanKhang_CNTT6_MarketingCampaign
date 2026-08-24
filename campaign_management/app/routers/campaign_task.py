from fastapi import APIRouter, Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import (CampaignTask,CampaignMember,Campaign,User)
from app.schemas.campaign_task import CampaignTaskCreate , CampaignTaskBase,CampaignTaskResponse,CampaignTaskUpdate

from app.dependencies.auth import get_current_user
router = APIRouter(
    prefix = "/campaigns_task",
    tags = ["CampaignTask"]
)

def check_campaign_membership(db: Session, campaign_id: int, user_id: int):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chiến dịch không tồn tại",
        )
    is_owner = campaign.owner_id == user_id
    is_member = (
        db.query(CampaignMember)
        .filter(
            CampaignMember.campaign_id == campaign_id,
            CampaignMember.user_id == user_id,
        )
        .first()
        is not None
    )
    if not (is_owner or is_member):
        raise HTTPException(
            status_code=403,
            detail="Bạn không phải thành viên của chiến dịch này",
        )

    return campaign

@router.post("/{campaign_id}", status_code=status.HTTP_201_CREATED)
def create_task(campaign_id: int,task_in: CampaignTaskCreate,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(
        campaign_id == Campaign.id
    ).first()
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy campaign"
        )
    check_role = db.query(CampaignMember).filter(
        CampaignMember.campaign_id == campaign_id,
        current_user.id == CampaignMember.user_id
    ).first()
    if not check_role:
        raise HTTPException(
            status_code=403,
            detail="Không phải là member hoặc owner!"
        )
    if task_in:
        is_assignee_owner = campaign.owner_id == task_in.assignee_id
        is_assignee_member = db.query(CampaignMember).filter(
            CampaignMember.campaign_id == campaign_id,
            CampaignMember.user_id == task_in.assignee_id
        ).first()

        if not is_assignee_owner and not is_assignee_member:
            raise HTTPException(
                status_code=400,
                detail="Assignee không phải là thành viên trong chiến dịch!"
            )

    # Khởi tạo và lưu task mới vào Database
    new_task = CampaignTask(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        priority=task_in.priority,
        assignee_id=task_in.assignee_id,
        campaign_id=campaign_id,
        status= "TODO"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

@router.get("/{campaign_id}")
    