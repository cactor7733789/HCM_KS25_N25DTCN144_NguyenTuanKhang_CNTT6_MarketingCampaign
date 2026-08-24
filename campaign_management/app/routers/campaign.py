from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.campaign import Campaign, CampaignMember
from app.models.campaign_task import CampaignTask
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignResponse,CampaignUpdate
from app.schemas.campaign_member import CampaignMemberResponse,CampaignMemberCreate
from app.dependencies.auth import get_current_user
from app.dependencies.auth import require_admin


router = APIRouter(
    prefix = "/campaigns",
    tags = ["Campaigns"]
)

@router.post("/", response_model=CampaignResponse, status_code=201)
def create_campaign(campaign_data: CampaignCreate,current_user: User = Depends(get_current_user),db:Session = Depends(get_db)):
    new_campaign = Campaign(
        name = campaign_data.name,
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

@router.get("/", response_model=list[CampaignResponse])
def get_all_info_user(search:str | None = None,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    query = db.query(Campaign).join(CampaignMember).filter(
        CampaignMember.user_id == current_user.id
    )
    if search:
          query = query.filter(
              Campaign.name.ilike(f"%{search}%")
          )
    return query.all()

@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_single_info(campaign_id: int,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
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

@router.patch("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(campaign_id: int,campaign_data: CampaignUpdate,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
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

        campaign.name = name

    if campaign_data.description is not None:
        campaign.description = campaign_data.description

    db.commit()
    db.refresh(campaign)

    return campaign

@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Campaign không tồn tại"
        )
    if not campaign.owner_id == current_user.id:
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

@router.post(
      "/{campaign_id}/members",
      response_model=CampaignMemberResponse,
      status_code=201
  )
def add_member(campaign_id: int,member_data: CampaignMemberCreate,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)
):
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

@router.delete("/{campaign_id}/members/{user_id}")
def delete_member(campaign_id: int,user_id:int,current_user: User = Depends(get_current_user),db : Session = Depends(get_db)):
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

@router.get("/{campaign_id}/members",response_model=list[CampaignMemberResponse])
def get_member(campaign_id: int,current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy CamPaign"
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
    




    

    
    


    
