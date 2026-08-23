from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.campaign import Campaign, CampaignMember
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignResponse
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

@router.get("/campaigns/{campaign_id}")
def get_single_info(campaign_id: str,current_user: User = Depends(get_current_user),db: Session= Depends(get_db)):
    query = db.query(Campaign).join(CampaignMember).filter(
        CampaignMember.user_id == current_user.id
    )
    if campaign_id:
         query = query.filter(
              Campaign.id == campaign_id
         )

         return query.all()
@router
    


    
