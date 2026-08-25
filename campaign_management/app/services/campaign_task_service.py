from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from app.models import CampaignTask,CampaignMember,Campaign,User
from app.schemas.campaign_task import CampaignTaskCreate,CampaignTaskUpdate

def check_campaign_membership(db: Session, campaign_id: int, user_id: int):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chiến dịch không tồn tại",
        )
    is_owner = campaign.owner_id == user_id
    is_member = (db.query(CampaignMember).filter(
        CampaignMember.campaign_id == campaign_id,
        CampaignMember.user_id == user_id,).first() 
        is not None
    )
    if not (is_owner or is_member):
        raise HTTPException(
            status_code=403,
            detail="Bạn không phải thành viên của chiến dịch này",
        )

    return campaign

def create_task_service(campaign_id: int,task_in: CampaignTaskCreate,current_user: User,db: Session):
    campaign = check_campaign_membership(
        db,
        campaign_id,
        current_user.id
    )

    if task_in.assignee_id is not None:
        is_assignee_owner = campaign.owner_id == task_in.assignee_id
        is_assignee_member = (
            db.query(CampaignMember)
            .filter(
                CampaignMember.campaign_id == campaign_id,
                CampaignMember.user_id == task_in.assignee_id
            )
            .first()
            is not None
        )
        if not is_assignee_member and not is_assignee_owner:
            raise HTTPException(
                status_code=400,
                detail="assignee không phải là thành viên trong chiến dịch"
            )

    new_task = CampaignTask(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        priority=task_in.priority,
        assignee_id=task_in.assignee_id,
        campaign_id=campaign_id,
        status=task_in.status
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

def get_all_task_service(campaign_id: int,current_user: User,db: Session,limit: int,offset: int,search: str | None = None,task_status: str | None = None,priority: str | None = None,assignee_id: int | None = None,sort_by: str | None = None,sort_order: str | None = None):
    check_campaign_membership(db, campaign_id, current_user.id)
    if limit <= 0:
        raise HTTPException(
            status_code=400,
            detail="limit phải lớn hơn 0"
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="offset không được nhỏ hơn 0"
        )

    query = db.query(CampaignTask).filter(
        CampaignTask.campaign_id == campaign_id
    )

    if search is not None and search.strip():
        query = query.filter(
            CampaignTask.title.ilike(f"%{search.strip()}%")
        )

    if task_status is not None:
        query = query.filter(
            CampaignTask.status == task_status
        )

    if priority is not None:
        query = query.filter(
            CampaignTask.priority == priority
        )

    if assignee_id is not None:
        query = query.filter(
            CampaignTask.assignee_id == assignee_id
        )

    if sort_by == "due_date":
        if sort_order == "desc":
            query = query.order_by(CampaignTask.due_date.desc())
        else:
            query = query.order_by(CampaignTask.due_date.asc())

    elif sort_by == "created_at":
        if sort_order == "desc":
            query = query.order_by(CampaignTask.created_at.desc())
        else:
            query = query.order_by(CampaignTask.created_at.asc())

    return query.offset(offset).limit(limit).all()
    
def get_single_task_service(task_id: int,campaign_id: int,current_user: User,db: Session):
    campaign = check_campaign_membership(db,campaign_id,current_user.id)

    check_task = db.query(CampaignTask).filter(
        CampaignTask.campaign_id == campaign_id,
        CampaignTask.id == task_id,
    ).first()

    if not check_task:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy task"
        )
    return check_task

def update_task_service(campaign_id: int,task_id:int,task_data: CampaignTaskUpdate,current_user: User,db: Session):
    campaign = check_campaign_membership(db,campaign_id,current_user.id)

    check_task = db.query(CampaignTask).filter(
        CampaignTask.campaign_id == campaign_id,
        CampaignTask.id == task_id,
    ).first()

    if not check_task:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy task"
        )

    is_owner = (campaign.owner_id == current_user.id)
    is_assignee = (check_task.assignee_id == current_user.id)
    if not is_owner and not is_assignee:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền cập nhật task"
        )

    if not is_owner and is_assignee:
        if (
            task_data.title is not None
            or task_data.description is not None
            or task_data.priority is not None
            or task_data.due_date is not None
            or task_data.assignee_id is not None
        ):
            raise HTTPException(
                status_code=403,
                detail="Assignee chỉ được phép cập nhật status"
            )
    if (
        task_data.title is None
        and task_data.description is None
        and task_data.assignee_id is None
        and task_data.status is None
        and task_data.priority is None
        and task_data.due_date is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Không có dữ liệu cập nhật"
        )

    if task_data.title is not None:
        title = task_data.title.strip()
        if not title:
            raise HTTPException(
                status_code=400,
                detail="Tiêu đề task không được để trống"
            )

        check_task.title = title

    if task_data.description is not None:
        check_task.description = task_data.description

    if task_data.assignee_id is not None:
        is_assignee_owner = campaign.owner_id == task_data.assignee_id
        is_assignee_member = (
            db.query(CampaignMember)
            .filter(
                CampaignMember.campaign_id == campaign_id,
                CampaignMember.user_id == task_data.assignee_id
            ).first()
            is not None
        )

        if not is_assignee_owner and not is_assignee_member:
            raise HTTPException(
                status_code=400,
                detail="Assignee không phải là thành viên trong chiến dịch!"
            )

        check_task.assignee_id = task_data.assignee_id

    if task_data.status is not None:
        check_task.status = task_data.status
        

    if task_data.priority is not None:
        check_task.priority = task_data.priority

    if task_data.due_date is not None:
        check_task.due_date = task_data.due_date

    db.commit()
    db.refresh(check_task)

    return check_task

def delete_task_service(campaign_id: int,task_id: int,current_user: User,db: Session):
    campaign = check_campaign_membership(
        db,
        campaign_id,
        current_user.id
    )
    if campaign.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền xóa task này"
        )
    check_task = db.query(CampaignTask).filter(
        CampaignTask.id == task_id,
        CampaignTask.campaign_id == campaign_id
    ).first()

    if not check_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy task"
        )

    db.delete(check_task)
    db.commit()

    return None

def change_assignee_service(campaign_id: int,task_id: int,new_assignee_id: int,current_user: User,db:Session):
    campaign = check_campaign_membership(db,campaign_id,current_user.id)
    if campaign.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền thay đổi assignee"
        )
    check_task = db.query(CampaignTask).filter(
        CampaignTask.campaign_id == campaign_id,
        CampaignTask.id == task_id,
    ).first()

    if not check_task:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy task"
        )
    
    is_assignee_owner = campaign.owner_id == new_assignee_id

    is_assignee_member = (
        db.query(CampaignMember)
        .filter(
            CampaignMember.campaign_id == campaign_id,
            CampaignMember.user_id == new_assignee_id
        )
        .first()
        is not None
    )

    if not is_assignee_owner and not is_assignee_member:
        raise HTTPException(
            status_code=400,
            detail="assignee không phải là thành viên trong chiến dịch"
        )

    check_task.assignee_id = new_assignee_id

    db.commit()
    db.refresh(check_task)

    return check_task
