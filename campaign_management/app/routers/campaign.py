from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from app.schemas.campaign_member import CampaignMemberResponse, CampaignMemberCreate
from app.dependencies.auth import get_current_user
from app.services.campaign_service import (
    create_campaign_service,
    get_all_info_user_service,
    get_single_info_service,
    update_campaign_service,
    delete_campaign_service,
    add_member_service,
    delete_member_service,
    get_member_service
)

router = APIRouter(
    prefix="/campaigns",
    tags=["Campaigns"]
)

@router.post(
    "/",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo chiến dịch mới",
    description="Người dùng đăng nhập tạo chiến dịch mới và tự động được phân quyền OWNER trong chiến dịch đó."
)
def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_campaign_service(campaign_data, current_user, db)

@router.get(
    "/",
    response_model=list[CampaignResponse],
    status_code=status.HTTP_200_OK,
    summary="Danh sách chiến dịch của tôi",
    description="Trả về danh sách các chiến dịch mà người dùng hiện tại đang tham gia (là OWNER hoặc MEMBER). Hỗ trợ tìm kiếm theo tên."
)
def get_campaign(
    search: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_all_info_user_service(search, current_user, db)

@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Chi tiết chiến dịch",
    description="Xem thông tin chi tiết của chiến dịch. Chỉ thành viên (OWNER hoặc MEMBER) thuộc chiến dịch mới có quyền truy cập."
)
def get_single_info(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_single_info_service(campaign_id, current_user, db)

@router.patch(
    "/{campaign_id}",
    response_model=CampaignResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật chiến dịch",
    description="Cập nhật tên hoặc mô tả chiến dịch. Chỉ OWNER của chiến dịch mới có quyền sửa (chặn 403 nếu không phải Owner)."
)
def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_campaign_service(campaign_id, campaign_data, current_user, db)

@router.delete(
    "/{campaign_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa chiến dịch",
    description="Xóa hoàn toàn chiến dịch cùng các thành viên và đầu việc liên quan. Chỉ OWNER mới có quyền xóa (chặn 403)."
)
def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_campaign_service(campaign_id, current_user, db)

@router.post(
    "/{campaign_id}/members",
    response_model=CampaignMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm thành viên vào chiến dịch",
    description="OWNER thêm một người dùng vào chiến dịch với vai trò MEMBER. Chặn thêm trùng hoặc người không tồn tại."
)
def add_member(
    campaign_id: int,
    member_data: CampaignMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return add_member_service(campaign_id, member_data, current_user, db)

@router.delete(
    "/{campaign_id}/members/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa thành viên khỏi chiến dịch",
    description="OWNER xóa một thành viên khỏi chiến dịch. Không cho phép xóa chính OWNER của chiến dịch."
)
def delete_member(
    campaign_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_member_service(campaign_id, user_id, current_user, db)

@router.get(
    "/{campaign_id}/members",
    response_model=list[CampaignMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="Danh sách thành viên chiến dịch",
    description="Xem danh sách tất cả thành viên và vai trò (OWNER / MEMBER) trong chiến dịch. Chỉ thành viên mới được xem."
)
def get_member(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_member_service(campaign_id, current_user, db)
    




    

    
    


    
