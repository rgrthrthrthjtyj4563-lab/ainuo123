from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db, TemplateExtraction
from app.services.word_extractor import WordStructureExtractor
from app.schemas.report_structure import (
    ReportStructureCreate, ReportStructureUpdate, ReportStructureResponse, ReportStructureDetailResponse, ReportStructureListResponse,
    StructureNodeCreate, StructureNodeUpdate, StructureNodeResponse,
    StructureNodeReorderRequest, StructureImportRequest
)
from app.services.structure_service import StructureService
from app.models.schemas import DataResponse, ListResponse

router = APIRouter()

@router.post("/structures/extract")
async def extract_structure_from_word(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """从Word文件提取报告结构"""
    if not file.filename.lower().endswith(('.docx', '.doc')):
        raise HTTPException(status_code=400, detail="仅支持Word文件 (.docx)")
    
    content = await file.read()
    extractor = WordStructureExtractor()
    
    try:
        result = extractor.extract(content, file.filename)
        
        # Save extraction record
        extraction_record = TemplateExtraction(
            file_name=result['file_name'],
            file_hash=result['file_hash'],
            extracted_structure=result['structure'],
            status='completed'
        )
        db.add(extraction_record)
        db.commit()
        db.refresh(extraction_record)
        
        return DataResponse(data={
            "extraction_id": extraction_record.id,
            "structure": result['structure']
        })
        
    except Exception as e:
        print(f"Extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")


@router.get("/structures", response_model=ReportStructureListResponse)
async def get_structures(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: bool = Query(None),
    db: Session = Depends(get_db)
):
    """获取报告结构列表"""
    service = StructureService(db)
    skip = (page - 1) * page_size
    structures, total = service.get_structures(skip=skip, limit=page_size, is_active=is_active)
    
    return ReportStructureListResponse(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": [ReportStructureResponse.model_validate(s) for s in structures]
    })

@router.post("/structures", response_model=DataResponse)
async def create_structure(
    structure: ReportStructureCreate,
    db: Session = Depends(get_db)
):
    """创建报告结构"""
    service = StructureService(db)
    new_structure = service.create_structure(structure)
    return DataResponse(data=ReportStructureResponse.model_validate(new_structure))

@router.get("/structures/{structure_id}", response_model=DataResponse)
async def get_structure(
    structure_id: int,
    db: Session = Depends(get_db)
):
    """获取报告结构详情"""
    service = StructureService(db)
    structure = service.get_structure(structure_id)
    if not structure:
        raise HTTPException(status_code=404, detail="结构不存在")
    
    # Manually populate nodes as tree
    nodes = service.get_structure_nodes(structure_id)
    
    # We construct the response manually or use Pydantic
    # ReportStructureDetailResponse expects 'nodes' field
    response = ReportStructureDetailResponse.model_validate(structure)
    response.nodes = [StructureNodeResponse.model_validate(n) for n in nodes]
    
    return DataResponse(data=response)

@router.put("/structures/{structure_id}", response_model=DataResponse)
async def update_structure(
    structure_id: int,
    structure: ReportStructureUpdate,
    db: Session = Depends(get_db)
):
    """更新报告结构"""
    service = StructureService(db)
    updated_structure = service.update_structure(structure_id, structure)
    if not updated_structure:
        raise HTTPException(status_code=404, detail="结构不存在")
    return DataResponse(data=ReportStructureResponse.model_validate(updated_structure))

@router.delete("/structures/{structure_id}", response_model=DataResponse)
async def delete_structure(
    structure_id: int,
    db: Session = Depends(get_db)
):
    """删除报告结构"""
    service = StructureService(db)
    success = service.delete_structure(structure_id)
    if not success:
        raise HTTPException(status_code=404, detail="结构不存在")
    return DataResponse(message="删除成功")

# Node operations

@router.post("/structures/nodes", response_model=DataResponse)
async def create_node(
    node: StructureNodeCreate,
    db: Session = Depends(get_db)
):
    """创建结构节点"""
    service = StructureService(db)
    new_node = service.create_node(node)
    return DataResponse(data=StructureNodeResponse.model_validate(new_node))

@router.put("/structures/nodes/{node_id}", response_model=DataResponse)
async def update_node(
    node_id: int,
    node: StructureNodeUpdate,
    db: Session = Depends(get_db)
):
    """更新结构节点"""
    service = StructureService(db)
    updated_node = service.update_node(node_id, node)
    if not updated_node:
        raise HTTPException(status_code=404, detail="节点不存在")
    return DataResponse(data=StructureNodeResponse.model_validate(updated_node))

@router.delete("/structures/nodes/{node_id}", response_model=DataResponse)
async def delete_node(
    node_id: int,
    db: Session = Depends(get_db)
):
    """删除结构节点"""
    service = StructureService(db)
    success = service.delete_node(node_id)
    if not success:
        raise HTTPException(status_code=404, detail="节点不存在")
    return DataResponse(message="删除成功")

@router.post("/structures/nodes/reorder", response_model=DataResponse)
async def reorder_nodes(
    reorder_data: StructureNodeReorderRequest,
    db: Session = Depends(get_db)
):
    """重新排序节点"""
    service = StructureService(db)
    service.reorder_nodes(reorder_data)
    return DataResponse(message="排序更新成功")

@router.post("/structures/{structure_id}/import", response_model=DataResponse)
async def import_structure_nodes(
    structure_id: int,
    request: StructureImportRequest,
    db: Session = Depends(get_db)
):
    """导入结构节点（递归）"""
    service = StructureService(db)
    
    # Check if structure exists
    structure = service.get_structure(structure_id)
    if not structure:
        raise HTTPException(status_code=404, detail="结构不存在")
        
    # Recursive function to create nodes
    def create_nodes_recursive(nodes, parent_id=None):
        for node_data in nodes:
            # Create the node
            new_node = service.create_node(StructureNodeCreate(
                structure_id=structure_id,
                parent_id=parent_id,
                level=node_data.level,
                node_type=node_data.node_type,
                title=node_data.title,
                sort_order=node_data.sort_order,
                question_number=node_data.question_number,
                show_data_table=node_data.show_data_table,
                show_ai_interpretation=node_data.show_ai_interpretation,
                prompt_config_id=node_data.prompt_config_id,
                fixed_content=node_data.fixed_content,
                confidence_score=node_data.confidence_score,
                ai_reasoning=node_data.ai_reasoning,
                is_ai_generated=node_data.is_ai_generated
            ))
            
            # Process children
            if node_data.children:
                create_nodes_recursive(node_data.children, new_node.id)

    create_nodes_recursive(request.nodes)
    
    return DataResponse(message="导入成功")
