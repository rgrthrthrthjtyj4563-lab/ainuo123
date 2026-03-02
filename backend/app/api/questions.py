"""
问题配置API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import QuestionCreate, QuestionUpdate, DataResponse
from app.services.template_service import TemplateService

router = APIRouter()


@router.post("/{dimension_id}/questions", response_model=DataResponse)
async def create_question(
    dimension_id: int,
    question: QuestionCreate,
    db: Session = Depends(get_db)
):
    """添加问题"""
    service = TemplateService(db)
    result = service.create_question(dimension_id, question)
    if not result:
        raise HTTPException(status_code=404, detail="维度不存在")
    return DataResponse(data=result)


@router.put("/{question_id}", response_model=DataResponse)
async def update_question(
    question_id: int,
    question: QuestionUpdate,
    db: Session = Depends(get_db)
):
    """更新问题"""
    service = TemplateService(db)
    result = service.update_question(question_id, question)
    if not result:
        raise HTTPException(status_code=404, detail="问题不存在")
    return DataResponse(data=result)


@router.delete("/{question_id}", response_model=DataResponse)
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """删除问题"""
    service = TemplateService(db)
    success = service.delete_question(question_id)
    if not success:
        raise HTTPException(status_code=404, detail="问题不存在")
    return DataResponse()
