"""
模板管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.schemas import (
    TemplateCreate, TemplateUpdate, TemplateResponse, 
    TemplateDetailResponse, TemplateListResponse, DataResponse,
    DimensionCreate
)
from app.services.template_service import TemplateService

router = APIRouter()


@router.post("", response_model=DataResponse)
async def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db)
):
    """创建维度模板"""
    service = TemplateService(db)
    result = service.create_template(template)
    return DataResponse(data=result)


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    report_type: str = Query(None),
    db: Session = Depends(get_db)
):
    """获取模板列表"""
    service = TemplateService(db)
    result = service.list_templates(page, page_size, report_type)
    return TemplateListResponse(data=result)


@router.get("/{template_id}", response_model=DataResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """获取模板详情"""
    service = TemplateService(db)
    result = service.get_template(template_id)
    if not result:
        raise HTTPException(status_code=404, detail="模板不存在")
    return DataResponse(data=result)


@router.put("/{template_id}", response_model=DataResponse)
async def update_template(
    template_id: int,
    template: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """更新模板"""
    service = TemplateService(db)
    result = service.update_template(template_id, template)
    if not result:
        raise HTTPException(status_code=404, detail="模板不存在")
    return DataResponse(data=result)


@router.delete("/{template_id}", response_model=DataResponse)
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """删除模板"""
    service = TemplateService(db)
    success = service.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="模板不存在")
    return DataResponse()


@router.get("/{template_id}/dimensions", response_model=DataResponse)
async def list_dimensions(
    template_id: int,
    db: Session = Depends(get_db)
):
    """获取模板下的所有维度"""
    service = TemplateService(db)
    result = service.list_dimensions(template_id)
    return DataResponse(data=result)


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
