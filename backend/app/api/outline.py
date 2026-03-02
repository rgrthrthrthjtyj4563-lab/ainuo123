from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.schemas import (
    OutlineChapterCreate, OutlineChapterUpdate, OutlineChapterResponse, 
    OutlineReorderRequest, DataResponse, ListResponse
)
from app.services.outline_service import OutlineService

router = APIRouter()

@router.get("/templates/{template_id}/outline", response_model=ListResponse)
async def get_template_outline(
    template_id: int,
    db: Session = Depends(get_db)
):
    """获取模板大纲"""
    service = OutlineService(db)
    chapters = service.get_outline(template_id)
    # 使用 Pydantic 模型进行序列化
    return ListResponse(data={"list": [OutlineChapterResponse.model_validate(c) for c in chapters]})

@router.post("/templates/{template_id}/outline/reset", response_model=ListResponse)
async def reset_template_outline(
    template_id: int,
    db: Session = Depends(get_db)
):
    """重置模板大纲"""
    service = OutlineService(db)
    chapters = service.reset_outline(template_id)
    return ListResponse(data={"list": [OutlineChapterResponse.model_validate(c) for c in chapters]})

@router.post("/outline/chapters", response_model=DataResponse)
async def add_chapter(
    chapter: OutlineChapterCreate,
    db: Session = Depends(get_db)
):
    """添加自定义章节"""
    service = OutlineService(db)
    result = service.add_custom_chapter(chapter)
    return DataResponse(data=result)

@router.put("/outline/chapters/{chapter_id}", response_model=DataResponse)
async def update_chapter(
    chapter_id: int,
    chapter: OutlineChapterUpdate,
    db: Session = Depends(get_db)
):
    """更新章节"""
    service = OutlineService(db)
    result = service.update_chapter(chapter_id, chapter)
    if not result:
        raise HTTPException(status_code=404, detail="章节不存在")
    return DataResponse(data=result)

@router.post("/outline/chapters/reorder", response_model=DataResponse)
async def reorder_chapters(
    reorder_data: OutlineReorderRequest,
    db: Session = Depends(get_db)
):
    """重新排序章节"""
    service = OutlineService(db)
    service.reorder_chapters(reorder_data)
    return DataResponse(message="排序更新成功")

@router.delete("/outline/chapters/{chapter_id}", response_model=DataResponse)
async def delete_chapter(
    chapter_id: int,
    db: Session = Depends(get_db)
):
    """删除章节"""
    service = OutlineService(db)
    success = service.delete_chapter(chapter_id)
    if not success:
        raise HTTPException(status_code=404, detail="章节不存在")
    return DataResponse(message="删除成功")
