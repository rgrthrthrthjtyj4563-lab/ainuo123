"""
维度管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import DimensionCreate, DimensionUpdate, DataResponse
from app.services.template_service import TemplateService

router = APIRouter()


@router.post("/{template_id}/dimensions", response_model=DataResponse)
async def create_dimension(
    template_id: int,
    dimension: DimensionCreate,
    db: Session = Depends(get_db)
):
    """添加维度"""
    service = TemplateService(db)
    result = service.create_dimension(template_id, dimension)
    if not result:
        raise HTTPException(status_code=404, detail="模板不存在")
    return DataResponse(data=result)


@router.put("/{dimension_id}", response_model=DataResponse)
async def update_dimension(
    dimension_id: int,
    dimension: DimensionUpdate,
    db: Session = Depends(get_db)
):
    """更新维度"""
    service = TemplateService(db)
    result = service.update_dimension(dimension_id, dimension)
    if not result:
        raise HTTPException(status_code=404, detail="维度不存在")
    return DataResponse(data=result)


@router.delete("/{dimension_id}", response_model=DataResponse)
async def delete_dimension(
    dimension_id: int,
    db: Session = Depends(get_db)
):
    """删除维度"""
    service = TemplateService(db)
    success = service.delete_dimension(dimension_id)
    if not success:
        raise HTTPException(status_code=404, detail="维度不存在")
    return DataResponse()
