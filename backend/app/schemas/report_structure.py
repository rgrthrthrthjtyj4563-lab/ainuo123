from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from app.models.schemas import ResponseBase, ListResponse

class StructureNodeBase(BaseModel):
    level: int = Field(..., ge=1, description="节点层级")
    node_type: str = Field(..., pattern="^(ai_chapter|fixed_content|container|data_analysis)$", description="节点类型")
    title: str = Field(..., min_length=1, max_length=200, description="节点标题")
    sort_order: int = Field(default=0, description="同级排序")
    question_number: Optional[int] = Field(default=None, description="关联Excel题号")
    show_data_table: bool = Field(default=True, description="显示数据表格")
    show_ai_interpretation: bool = Field(default=False, description="显示AI解读")
    
    # === 新增字段 ===
    charts: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="图表配置列表 [{chart_type, sort_order, config}]"
    )

    prompt_config_id: Optional[int] = Field(default=None, description="关联提示词配置")
    fixed_content: Optional[str] = Field(default=None, description="固定内容文本")
    
    # AI fields
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1, description="AI置信度")
    ai_reasoning: Optional[str] = Field(default=None, description="AI推荐理由")
    is_ai_generated: bool = Field(default=False, description="是否AI生成")

class StructureNodeCreate(StructureNodeBase):
    structure_id: int
    parent_id: Optional[int] = None

class StructureNodeUpdate(BaseModel):
    title: Optional[str] = None
    sort_order: Optional[int] = None
    question_number: Optional[int] = None
    show_data_table: Optional[bool] = None
    show_ai_interpretation: Optional[bool] = None
    charts: Optional[List[Dict[str, Any]]] = None
    prompt_config_id: Optional[int] = None
    fixed_content: Optional[str] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    node_type: Optional[str] = None

class StructureNodeResponse(StructureNodeBase):
    id: int
    structure_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    children: List['StructureNodeResponse'] = Field(default_factory=list)

    class Config:
        from_attributes = True

class StructureNodeReorderItem(BaseModel):
    id: int
    sort_order: int
    parent_id: Optional[int] = None
    level: int

class StructureNodeReorderRequest(BaseModel):
    items: List[StructureNodeReorderItem]

class ReportStructureBase(BaseModel):
    structure_name: str = Field(..., min_length=1, max_length=100, description="结构名称")
    report_type: str = Field(..., pattern="^(doctor|patient)$", description="报告类型")
    analysis_depth: int = Field(default=3, ge=1, le=3, description="分析层级深度")
    description: Optional[str] = Field(default=None, max_length=500, description="结构描述")
    is_active: bool = Field(default=True, description="是否启用")

class ReportStructureCreate(ReportStructureBase):
    pass

class ReportStructureUpdate(BaseModel):
    structure_name: Optional[str] = None
    report_type: Optional[str] = None
    analysis_depth: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class StructureNodeImport(StructureNodeBase):
    children: List['StructureNodeImport'] = Field(default_factory=list)

class StructureImportRequest(BaseModel):
    nodes: List[StructureNodeImport]

class ReportStructureResponse(ReportStructureBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ReportStructureDetailResponse(ReportStructureResponse):
    nodes: List[StructureNodeResponse] = Field(default_factory=list)

class ReportStructureListResponse(ListResponse):
    data: dict = Field(default_factory=lambda: {
        "total": 0,
        "page": 1,
        "page_size": 20,
        "list": []
    })

StructureNodeResponse.model_rebuild()
StructureNodeImport.model_rebuild()
