from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User
from app.schemas.campaign_task import CampaignTaskCreate, CampaignTaskResponse, CampaignTaskUpdate, TaskPriority, TaskStatus
from app.dependencies.auth import get_current_user
from app.services.campaign_task_service import (
    create_task_service,
    get_all_task_service,
    get_single_task_service,
    update_task_service,
    delete_task_service,
    change_assignee_service
)

router = APIRouter(
    prefix="/campaigns_task",
    tags=["CampaignTask"]
)

@router.post(
    "/{campaign_id}",
    response_model=CampaignTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo đầu việc chiến dịch",
    description="Thành viên chiến dịch tạo đầu việc mới với tiêu đề, mô tả, hạn xử lý (due_date) và độ ưu tiên. Assignee (nếu có) phải thuộc chiến dịch."
)
def create_task(
    campaign_id: int,
    task_in: CampaignTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_task_service(campaign_id, task_in, current_user, db)

@router.get(
    "/{campaign_id}",
    response_model=list[CampaignTaskResponse],
    status_code=status.HTTP_200_OK,
    summary="Danh sách đầu việc chiến dịch (Filter & Phân trang)",
    description="Lấy danh sách task của chiến dịch. Hỗ trợ tìm kiếm theo tiêu đề, lọc theo status/priority/assignee, phân trang limit/offset và sắp xếp theo due_date/created_at."
)
def get_all_task(
    campaign_id: int,
    limit: int = 10,
    offset: int = 0,
    search: str | None = None,
    task_status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    assignee_id: int | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_all_task_service(
        campaign_id,
        current_user,
        db,
        limit,
        offset,
        search,
        task_status,
        priority,
        assignee_id,
        sort_by,
        sort_order
    )

@router.get(
    "/{campaign_id}/{task_id}",
    response_model=CampaignTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Chi tiết đầu việc chiến dịch",
    description="Xem chi tiết một task. Chỉ thành viên trong chiến dịch mới có quyền truy cập."
)
def get_single_task(
    task_id: int,
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_single_task_service(task_id, campaign_id, current_user, db)

@router.patch(
    "/{campaign_id}/{task_id}",
    response_model=CampaignTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật đầu việc chiến dịch",
    description="Cập nhật thông tin task theo ma trận quyền: OWNER sửa tất cả các trường; ASSIGNEE chỉ được sửa trạng thái (status); thành viên khác bị chặn (403)."
)
def update_task(
    campaign_id: int,
    task_id: int,
    task_data: CampaignTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_task_service(campaign_id, task_id, task_data, current_user, db)

@router.delete(
    "/{campaign_id}/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa đầu việc chiến dịch",
    description="Xóa một task khỏi chiến dịch. Chỉ OWNER của chiến dịch mới có quyền xóa (chặn 403 nếu là Member thường)."
)
def delete_task(
    campaign_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_task_service(campaign_id, task_id, current_user, db)

@router.patch(
    "/{campaign_id}/{task_id}/assignee",
    response_model=CampaignTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Thay đổi người thực hiện task (Change Assignee)",
    description="Phân công lại người thực hiện task. Chỉ OWNER mới có quyền đổi và người được giao mới phải thuộc chiến dịch."
)
def change_assignee(
    campaign_id: int,
    task_id: int,
    new_assignee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return change_assignee_service(campaign_id, task_id, new_assignee_id, current_user, db)
