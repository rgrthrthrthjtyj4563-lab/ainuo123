"""
Pydantic 数据模型
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# ============================================
# 基础响应模型
# ============================================
class ResponseBase(BaseModel):
    code: int = 200
    message: str = "success"


class DataResponse(ResponseBase):
    data: Optional[Any] = None


class ListResponse(ResponseBase):
    data: dict = Field(default_factory=dict)


# ============================================
# 维度模板模型
# ============================================
class QuestionConfig(BaseModel):
    """问题配置"""
    id: Optional[int] = None
    question_number: int = Field(..., ge=1, description="问题编号")
    analysis_title: str = Field(..., min_length=1, max_length=200, description="分析标题")
    sort_order: int = Field(default=0, description="排序序号")


class DimensionConfig(BaseModel):
    """维度配置"""
    id: Optional[int] = None
    dimension_number: str = Field(..., min_length=1, max_length=10, description="维度编号（如：4.1）")
    dimension_title: str = Field(..., min_length=1, max_length=100, description="维度标题")
    sort_order: int = Field(default=0, description="排序序号")
    questions: List[QuestionConfig] = Field(default_factory=list, description="问题列表")


class TemplateBase(BaseModel):
    """模板基础信息"""
    template_name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    report_type: str = Field(..., pattern="^(doctor|patient)$", description="报告类型")
    description: Optional[str] = Field(default=None, max_length=500, description="模板描述")


class TemplateCreate(TemplateBase):
    """创建模板请求"""
    dimensions: List[DimensionConfig] = Field(default_factory=list, description="维度列表")


class TemplateUpdate(BaseModel):
    """更新模板请求"""
    template_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """模板响应"""
    id: int
    is_active: bool
    dimension_count: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TemplateDetailResponse(TemplateResponse):
    """模板详情响应"""
    dimensions: List[DimensionConfig] = Field(default_factory=list)


class TemplateListResponse(ListResponse):
    """模板列表响应"""
    data: dict = Field(default_factory=lambda: {
        "total": 0,
        "page": 1,
        "page_size": 20,
        "list": []
    })


# ============================================
# 维度管理模型
# ============================================
class DimensionCreate(BaseModel):
    """创建维度请求"""
    dimension_number: str = Field(..., min_length=1, max_length=10, description="维度编号（如：4.1）")
    dimension_title: str = Field(..., min_length=1, max_length=100, description="维度名称")
    sort_order: int = Field(default=0, description="排序序号")
    question_number: Optional[int] = Field(default=None, ge=1, description="关联题号")
    analysis_title: Optional[str] = Field(default=None, max_length=200, description="小分析标题")


class DimensionUpdate(BaseModel):
    """更新维度请求"""
    dimension_number: Optional[str] = Field(default=None, min_length=1, max_length=10)
    dimension_title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    sort_order: Optional[int] = None
    question_number: Optional[int] = Field(default=None, ge=1, description="关联题号")
    analysis_title: Optional[str] = Field(default=None, max_length=200, description="小分析标题")


class DimensionResponse(BaseModel):
    """维度响应"""
    id: int
    template_id: int
    dimension_number: str
    dimension_title: str
    sort_order: int
    created_at: datetime


# ============================================
# 问题配置模型
# ============================================
class QuestionCreate(BaseModel):
    """创建问题请求"""
    question_number: int = Field(..., ge=1)
    analysis_title: str = Field(..., min_length=1, max_length=200)
    sort_order: int = Field(default=0)


class QuestionUpdate(BaseModel):
    """更新问题请求"""
    question_number: Optional[int] = Field(default=None, ge=1)
    analysis_title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    sort_order: Optional[int] = None


class QuestionResponse(BaseModel):
    """问题响应"""
    id: int
    dimension_id: int
    question_number: int
    analysis_title: str
    sort_order: int
    created_at: datetime


# ============================================
# 报告生成模型
# ============================================
class ReportBase(BaseModel):
    """报告基础信息"""
    report_title: str = Field(..., min_length=1, max_length=200)
    product_name: str = Field(..., min_length=1, max_length=100)
    survey_region: str = Field(..., min_length=1, max_length=100)
    survey_time_range: str = Field(..., min_length=1, max_length=100)
    sample_count: int = Field(..., ge=1)
    question_count: int = Field(default=0, ge=0)


class ReportCreate(BaseModel):
    """创建报告请求"""
    template_id: Optional[int] = Field(default=None, description="兼容旧版模板ID")
    structure_id: Optional[int] = Field(default=None, description="新版结构ID")
    report_title: str = Field(..., min_length=1, max_length=200)
    product_name: str = Field(..., min_length=1, max_length=100)
    survey_region: str = Field(..., min_length=1, max_length=100)
    survey_time_range: str = Field(..., min_length=1, max_length=100)
    sample_count: int = Field(..., ge=1)
    question_count: int = Field(default=0, ge=0)


class ReportUpdate(BaseModel):
    """更新报告请求"""
    report_title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    product_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    survey_region: Optional[str] = Field(default=None, min_length=1, max_length=100)
    survey_time_range: Optional[str] = Field(default=None, min_length=1, max_length=100)
    sample_count: Optional[int] = Field(default=None, ge=1)
    question_count: Optional[int] = Field(default=None, ge=0)


class GeneratedContent(BaseModel):
    """生成的内容"""
    preface: Optional[str] = None
    background: Optional[str] = None
    project_info: Optional[str] = None
    conclusion: Optional[str] = None
    suggestions: Optional[str] = None


class ReportResponse(ReportBase):
    """报告响应"""
    id: int
    template_id: int
    status: str
    error_message: Optional[str] = None
    word_file_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReportDetailResponse(ReportResponse):
    """报告详情响应"""
    generated_content: Optional[GeneratedContent] = None
    dimensions: List[DimensionConfig] = Field(default_factory=list)


class ReportListResponse(ListResponse):
    """报告列表响应"""
    data: dict = Field(default_factory=lambda: {
        "total": 0,
        "page": 1,
        "page_size": 20,
        "list": []
    })


class ExcelUploadResponse(DataResponse):
    """Excel上传响应"""
    data: dict = Field(default_factory=lambda: {
        "parsed_data": {}
    })


class GenerateReportRequest(BaseModel):
    """生成报告请求"""
    coze_workflow_id: Optional[str] = None


class GenerateProgress(BaseModel):
    """生成进度"""
    section: str
    progress: int
    status: str  # processing, completed, failed
    message: Optional[str] = None


# ============================================
# Excel数据结构
# ============================================
class OptionData(BaseModel):
    """选项数据"""
    key: str
    text: str
    count: int
    percentage: str


class QuestionData(BaseModel):
    """问题数据"""
    question_number: int
    question_title: str
    options: List[OptionData]


class DimensionData(BaseModel):
    """维度数据"""
    dimension_number: str
    dimension_title: str
    questions: List[QuestionData]


class ExcelParsedData(BaseModel):
    """解析后的Excel数据"""
    question_count: int
    questions: List[QuestionData]
    dimensions: List[DimensionData]


# ============================================
# 大纲配置模型
# ============================================
class OutlineChapterBase(BaseModel):
    """大纲章节基础信息"""
    chapter_type: str = Field(..., description="章节类型")
    chapter_title: str = Field(..., min_length=1, max_length=200, description="显示标题")
    sort_order: int = Field(default=0, description="排序序号")
    is_enabled: bool = Field(default=True, description="是否启用")
    level: int = Field(default=1, ge=1, le=2, description="层级")
    parent_id: Optional[int] = Field(default=None, description="父章节ID")
    generation_type: str = Field(default="fixed", pattern="^(ai|fixed|data)$", description="生成方式")
    prompt_config_id: Optional[int] = Field(default=None, description="关联提示词配置")
    fixed_content: Optional[str] = Field(default=None, description="固定内容")


class OutlineChapterCreate(OutlineChapterBase):
    """创建大纲章节请求"""
    template_id: int = Field(..., description="关联模板ID")


class OutlineChapterUpdate(BaseModel):
    """更新大纲章节请求"""
    chapter_title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    sort_order: Optional[int] = None
    is_enabled: Optional[bool] = None
    generation_type: Optional[str] = Field(default=None, pattern="^(ai|fixed|data)$")
    prompt_config_id: Optional[int] = None
    fixed_content: Optional[str] = None
    parent_id: Optional[int] = None


class OutlineChapterResponse(OutlineChapterBase):
    """大纲章节响应"""
    id: int
    template_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    children: List['OutlineChapterResponse'] = Field(default_factory=list)

    class Config:
        from_attributes = True

# 解决递归引用
OutlineChapterResponse.model_rebuild()


class OutlineReorderItem(BaseModel):
    id: int
    sort_order: int
    parent_id: Optional[int] = None


class OutlineReorderRequest(BaseModel):
    items: List[OutlineReorderItem]
