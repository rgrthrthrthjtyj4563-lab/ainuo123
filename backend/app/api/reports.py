"""
报告生成API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.models.database import get_db
from app.models.schemas import (
    ReportCreate, ReportUpdate, GenerateReportRequest, 
    DataResponse, ReportListResponse
)
from app.services.report_service import ReportService
from app.services.excel_service import ExcelService

router = APIRouter()


@router.post("", response_model=DataResponse)
async def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db)
):
    """创建报告"""
    service = ReportService(db)
    result = service.create_report(report)
    return DataResponse(data=result)


@router.get("", response_model=ReportListResponse)
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取报告列表"""
    service = ReportService(db)
    result = service.list_reports(page, page_size, status)
    return ReportListResponse(data=result)


@router.get("/{report_id}", response_model=DataResponse)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """获取报告详情"""
    service = ReportService(db)
    result = service.get_report(report_id)
    if not result:
        raise HTTPException(status_code=404, detail="报告不存在")
    return DataResponse(data=result)


@router.put("/{report_id}", response_model=DataResponse)
async def update_report(
    report_id: int,
    report: ReportUpdate,
    db: Session = Depends(get_db)
):
    """更新报告"""
    service = ReportService(db)
    result = service.update_report(report_id, report)
    if not result:
        raise HTTPException(status_code=404, detail="报告不存在")
    return DataResponse(data=result)


@router.post("/{report_id}/upload-excel", response_model=DataResponse)
async def upload_excel(
    report_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传Excel并解析"""
    excel_service = ExcelService()
    report_service = ReportService(db)
    
    # 解析Excel
    parsed_data = await excel_service.parse_excel(file)
    
    # 更新报告数据
    result = report_service.update_excel_data(report_id, parsed_data)
    if not result:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return DataResponse(data={"parsed_data": parsed_data})


@router.post("/{report_id}/generate", response_model=DataResponse)
async def generate_report(
    report_id: int,
    request: GenerateReportRequest,
    db: Session = Depends(get_db)
):
    """生成报告（异步）"""
    service = ReportService(db)
    result = service.start_generation(report_id, request.coze_workflow_id)
    if not result:
        raise HTTPException(status_code=404, detail="报告不存在")
    return DataResponse(data=result)


@router.get("/{report_id}/progress")
async def get_progress(
    report_id: int,
    db: Session = Depends(get_db)
):
    """获取生成进度（SSE流式）"""
    service = ReportService(db)
    
    async def event_generator():
        async for event in service.get_generation_progress(report_id):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.get("/{report_id}/export")
async def export_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """导出Word报告"""
    service = ReportService(db)
    file_path = service.export_word(report_id)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="报告不存在或未生成")
    
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"report_{report_id}.docx"
    )


@router.delete("/{report_id}", response_model=DataResponse)
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """删除报告"""
    service = ReportService(db)
    success = service.delete_report(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="报告不存在")
    return DataResponse()
