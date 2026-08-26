from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.campaign import Campaign, CampaignMember
from app.models.campaign_task import CampaignTask
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.schemas.campaign_member import CampaignMemberCreate

def create_campaign_service(campaign_data: CampaignCreate,current_user: User,db:Session):
    name = campaign_data.name.strip()
    existing_campaign = db.query(Campaign).filter(
        Campaign.name == name
    ).first()
    if existing_campaign:
        raise HTTPException(
            status_code=400,
            detail="Tên chiến dịch đã tồn tại"
        )

    new_campaign = Campaign(
        name = name,
        description = campaign_data.description,
        owner_id = current_user.id
    )

    db.add(new_campaign)
    db.flush()

    new_member = CampaignMember(
        campaign_id = new_campaign.id,
        user_id = current_user.id,
        role = "OWNER"
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_campaign)
    return new_campaign

def get_all_info_user_service(search:str | None,current_user: User,db: Session):
    query = db.query(Campaign).join(CampaignMember).filter(
        CampaignMember.user_id == current_user.id
    )
    if search:
          query = query.filter(
              Campaign.name.ilike(f"%{search}%")
          )
    return query.all()

def get_single_info_service(campaign_id: int,current_user: User,db: Session):
    query = db.query(Campaign).join(CampaignMember).filter(
        CampaignMember.user_id == current_user.id,
        Campaign.id == campaign_id
    )
    campaign = query.first()
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign không tồn tại hoặc bạn không phải thành viên"
        )
    return campaign

def update_campaign_service(campaign_id: int,campaign_data: CampaignUpdate,current_user: User,db: Session):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy campaign"
        )

    if campaign.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền cập nhật campaign này"
        )

    if campaign_data.name is None and campaign_data.description is None:
          raise HTTPException(
              status_code=400,
              detail="Không có dữ liệu cập nhật"
          )

    if campaign_data.name is not None:
        name = campaign_data.name.strip()
        if not name:
            raise HTTPException(
                  status_code=400,
                  detail="Tên campaign không được để trống"
              )

        existing_campaign = db.query(Campaign).filter(
            Campaign.name == name,
            Campaign.id != campaign_id
        ).first()
        if existing_campaign:
            raise HTTPException(
                status_code=400,
                detail="Tên chiến dịch đã tồn tại"
            )

        campaign.name = name

    if campaign_data.description is not None:
        campaign.description = campaign_data.description

    db.commit()
    db.refresh(campaign)

    return campaign

def delete_campaign_service(campaign_id: int,current_user: User,db: Session):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign không tồn tại"
        )
    if campaign.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Không có quyền xoá"
        )
    
    members = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id).all()
    for member in members:
        db.delete(member)

    tasks = db.query(CampaignTask).filter(CampaignTask.campaign_id == campaign_id).all()
    for task in tasks:
        db.delete(task)

    db.delete(campaign)
    db.commit()
    
    return {
        "message":"xoá thành công!"
    }

def add_member_service(campaign_id: int,member_data: CampaignMemberCreate,current_user: User,db: Session):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy campaign"
        )

    if campaign.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không phải owner của campaign"
          )
    user = db.query(User).filter(User.id == member_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy user"
        )

    existing_member = db.query(CampaignMember).filter(CampaignMember.campaign_id == campaign_id,CampaignMember.user_id == member_data.user_id).first()

    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="User đã là thành viên của campaign"
        )

    new_member = CampaignMember(
        campaign_id=campaign_id,
        user_id=member_data.user_id,
        role="MEMBER"
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member

def delete_member_service(campaign_id: int,user_id:int,current_user: User,db : Session):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="không tìm thấy campaign"
        )
    if campaign.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Không phải owner!"
        )
    check_member = db.query(CampaignMember).filter(
        CampaignMember.campaign_id == campaign_id,
        CampaignMember.user_id == user_id
        ).first()
    if not check_member:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy user nào thuộc campaign"
        )
    if check_member.user_id == campaign.owner_id:
        raise HTTPException(
            status_code=400,
            detail="Không được xoá owner!"
        )
    
    db.delete(check_member)
    db.commit()
    return {
        "message":"xoá thành công member"
    }

def get_member_service(campaign_id: int,current_user: User,db: Session):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy campaign"
        )
    check_exist = db.query(CampaignMember).filter(
        CampaignMember.campaign_id == campaign_id,
        CampaignMember.user_id == current_user.id
    ).first()
    if not check_exist:
        raise HTTPException(
            status_code=403,
            detail="Không phải member"
        )
    show_member = db.query(CampaignMember).filter(
        CampaignMember.campaign_id == campaign_id
    ).all()
    return show_member
