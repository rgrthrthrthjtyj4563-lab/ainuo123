"""
数据库连接与模型定义
"""
from sqlalchemy import create_engine, Column, BigInteger, String, Text, Enum, Boolean, Integer, JSON, TIMESTAMP, ForeignKey, Index, DECIMAL, event, select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import get_settings

settings = get_settings()

# 创建引擎
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型
Base = declarative_base()


def _bigint():
    return BigInteger().with_variant(Integer, "sqlite")


def _assign_sqlite_id(mapper, connection, target, table):
    if settings.DATABASE_URL.startswith("sqlite") and target.id is None:
        max_id = connection.execute(select(func.max(table.c.id))).scalar()
        target.id = (max_id or 0) + 1


class DimensionTemplate(Base):
    """维度模板表"""
    __tablename__ = "dimension_templates"
    
    id = Column(_bigint(), primary_key=True, autoincrement=True)
    template_name = Column(String(100), nullable=False, comment="模板名称")
    report_type = Column(Enum('doctor', 'patient'), nullable=False, comment="报告类型")
    description = Column(Text, comment="模板描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    dimensions = relationship("Dimension", back_populates="template", cascade="all, delete-orphan")
    outline_chapters = relationship("OutlineChapter", back_populates="template", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_report_type', 'report_type'),
        {'comment': '维度模板表'}
    )


class Dimension(Base):
    """维度表"""
    __tablename__ = "dimensions"
    
    id = Column(_bigint(), primary_key=True, autoincrement=True)
    template_id = Column(_bigint(), ForeignKey("dimension_templates.id", ondelete="CASCADE"), nullable=False, comment="所属模板ID")
    dimension_number = Column(String(10), nullable=False, comment="维度编号（如：4.1）")
    dimension_title = Column(String(100), nullable=False, comment="维度标题")
    sort_order = Column(Integer, default=0, comment="排序序号")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")
    
    # 关系
    template = relationship("DimensionTemplate", back_populates="dimensions")
    questions = relationship("QuestionAnalysisConfig", back_populates="dimension", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_template_sort', 'template_id', 'sort_order'),
        {'comment': '维度表'}
    )


class QuestionAnalysisConfig(Base):
    """问题分析配置表"""
    __tablename__ = "question_analysis_configs"
    
    id = Column(_bigint(), primary_key=True, autoincrement=True)
    dimension_id = Column(_bigint(), ForeignKey("dimensions.id", ondelete="CASCADE"), nullable=False, comment="所属维度ID")
    question_number = Column(Integer, nullable=False, comment="问题编号（如：1）")
    analysis_title = Column(String(200), nullable=False, comment="分析标题")
    sort_order = Column(Integer, default=0, comment="排序序号")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")
    
    # 关系
    dimension = relationship("Dimension", back_populates="questions")
    
    __table_args__ = (
        Index('idx_dimension_sort', 'dimension_id', 'sort_order'),
        Index('uk_dimension_question', 'dimension_id', 'question_number', unique=True),
        {'comment': '问题分析配置表'}
    )


class PromptConfig(Base):
    """提示词配置表"""
    __tablename__ = "prompt_configs"
    
    id = Column(_bigint(), primary_key=True, autoincrement=True)
    config_name = Column(String(100), nullable=False, comment="配置名称")
    report_type = Column(Enum('doctor', 'patient'), nullable=False, comment="报告类型")
    section_type = Column(Enum('preface', 'background', 'project_info', 'conclusion', 'suggestions'), nullable=False, comment="章节类型")
    system_prompt = Column(Text, nullable=False, comment="系统提示词")
    user_prompt_template = Column(Text, nullable=False, comment="用户提示词模板")
    temperature = Column(DECIMAL(3, 2), default=0.7, comment="温度参数")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")
    
    __table_args__ = (
        Index('uk_type_section', 'report_type', 'section_type', unique=True),
        {'comment': '提示词配置表'}
    )


class OutlineChapter(Base):
    """大纲章节表"""
    __tablename__ = "outline_chapters"
    
    id = Column(_bigint(), primary_key=True, autoincrement=True)
    template_id = Column(_bigint(), ForeignKey("dimension_templates.id", ondelete="CASCADE"), nullable=False, comment="关联维度模板")
    chapter_type = Column(String(50), nullable=False, comment="章节类型标识")
    chapter_title = Column(String(200), nullable=False, comment="显示标题")
    sort_order = Column(Integer, default=0, comment="排序序号")
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    level = Column(Integer, default=1, comment="层级（1=一级，2=二级）")
    parent_id = Column(_bigint(), ForeignKey("outline_chapters.id", ondelete="CASCADE"), nullable=True, comment="父章节ID")
    generation_type = Column(Enum('ai', 'fixed', 'data'), default='fixed', comment="生成方式")
    prompt_config_id = Column(_bigint(), ForeignKey("prompt_configs.id", ondelete="SET NULL"), nullable=True, comment="关联提示词配置")
    fixed_content = Column(Text, nullable=True, comment="固定内容")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    template = relationship("DimensionTemplate", back_populates="outline_chapters")
    children = relationship("OutlineChapter", 
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="OutlineChapter.sort_order"
    )
    parent = relationship("OutlineChapter", 
        remote_side=[id], 
        back_populates="children"
    )
    prompt_config = relationship("PromptConfig")
    
    __table_args__ = (
        Index('idx_template_outline_sort', 'template_id', 'sort_order'),
        {'comment': '大纲章节表'}
    )


class Report(Base):
    """报告表"""
    __tablename__ = "reports"
    
    id = Column(_bigint(), primary_key=True, autoincrement=True)
    template_id = Column(_bigint(), ForeignKey("dimension_templates.id"), nullable=True, comment="使用的维度模板ID")
    structure_id = Column(_bigint(), ForeignKey("report_structures.id"), nullable=True, comment="使用的报告结构ID")
    report_title = Column(String(200), nullable=False, comment="报告标题")
    product_name = Column(String(100), nullable=False, comment="产品名称")
    survey_region = Column(String(100), nullable=False, comment="调研区域")
    survey_time_range = Column(String(100), nullable=False, comment="调研时间范围")
    sample_count = Column(Integer, nullable=False, comment="样本数量")
    question_count = Column(Integer, default=0, comment="问题数量")
    excel_data = Column(JSON, comment="解析后的Excel数据")
    generated_content = Column(JSON, comment="扣子生成的各章节内容")
    status = Column(Enum('draft', 'generating', 'completed', 'failed'), default='draft', comment="状态")
    error_message = Column(Text, comment="错误信息")
    word_file_path = Column(String(500), comment="Word文件路径")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    template = relationship("DimensionTemplate")
    
    __table_args__ = (
        Index('idx_status', 'status'),
        Index('idx_created_at', 'created_at'),
        {'comment': '报告表'}
    )


class ReportStructure(Base):
    """报告结构配置表（合并原维度模板+大纲配置）"""
    __tablename__ = "report_structures"
    
    id = Column(_bigint(), primary_key=True, autoincrement=True)
    structure_name = Column(String(100), nullable=False, comment="结构名称")
    report_type = Column(Enum('doctor', 'patient'), nullable=False, comment="报告类型")
    analysis_depth = Column(Integer, default=3, nullable=False, comment="分析层级深度：1=单层, 2=两层, 3=三层")
    description = Column(Text, comment="结构描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    nodes = relationship("StructureNode", back_populates="structure", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_rs_report_type', 'report_type'),
        {'comment': '报告结构配置表'}
    )


class StructureNode(Base):
    """结构节点表（统一配置章节、维度、分析）"""
    __tablename__ = "structure_nodes"
    
    id = Column(_bigint(), primary_key=True, autoincrement=True)
    structure_id = Column(_bigint(), ForeignKey("report_structures.id", ondelete="CASCADE"), nullable=False, comment="所属结构ID")
    
    # 层级关系
    parent_id = Column(_bigint(), ForeignKey("structure_nodes.id", ondelete="CASCADE"), nullable=True, comment="父节点ID")
    level = Column(Integer, nullable=False, comment="节点层级：1=章, 2=节, 3=小节")
    
    # 基础信息
    node_type = Column(Enum('ai_chapter', 'fixed_content', 'container', 'data_analysis'), nullable=False, comment="节点类型")
    title = Column(String(200), nullable=False, comment="节点标题")
    sort_order = Column(Integer, default=0, comment="同级排序")
    
    # 数据映射（仅data_analysis节点使用）
    question_number = Column(Integer, nullable=True, comment="关联Excel题号")
    
    # 显示配置
    show_data_table = Column(Boolean, default=True, comment="显示数据表格")
    show_ai_interpretation = Column(Boolean, default=False, comment="显示AI解读")
    
    # 图表配置 (v2.1新增)
    charts = Column(JSON, default=[], comment="图表配置列表")
    
    # 内容块配置 (v3.0新增 - PRD5)
    content_blocks = Column(JSON, default=[], comment="内容块配置列表")
    
    # AI配置
    prompt_config_id = Column(_bigint(), ForeignKey("prompt_configs.id", ondelete="SET NULL"), nullable=True, comment="关联提示词配置")
    
    # AI提取信息 (v2.0新增)
    confidence_score = Column(DECIMAL(3, 2), nullable=True, comment="AI置信度(0-1)")
    ai_reasoning = Column(Text, nullable=True, comment="AI推荐理由")
    is_ai_generated = Column(Boolean, default=False, comment="是否AI生成")
    
    # 固定内容
    fixed_content = Column(Text, nullable=True, comment="固定内容文本")
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")
    
    # 关系
    structure = relationship("ReportStructure", back_populates="nodes")
    children = relationship("StructureNode", 
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="StructureNode.sort_order"
    )
    parent = relationship("StructureNode", 
        remote_side=[id], 
        back_populates="children"
    )
    prompt_config = relationship("PromptConfig")
    
    __table_args__ = (
        Index('idx_structure_level', 'structure_id', 'level', 'sort_order'),
        Index('idx_parent', 'parent_id'),
        {'comment': '结构节点表'}
    )


class TemplateExtraction(Base):
    """Word模板提取记录表"""
    __tablename__ = "template_extractions"
    
    id = Column(_bigint(), primary_key=True, autoincrement=True)
    file_name = Column(String(200), nullable=False, comment="原始文件名")
    file_hash = Column(String(64), nullable=False, comment="文件哈希(SHA256)")
    extracted_structure = Column(JSON, nullable=False, comment="提取的结构JSON")
    status = Column(Enum('pending', 'completed', 'failed'), default='pending', comment="提取状态")
    error_message = Column(Text, comment="错误信息")
    created_at = Column(TIMESTAMP, default=datetime.utcnow, comment="创建时间")
    
    __table_args__ = (
        Index('idx_file_hash', 'file_hash'),
        {'comment': 'Word模板提取记录表'}
    )


# ============================================
# 数据库依赖
# ============================================
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @event.listens_for(DimensionTemplate, "before_insert")
# def _before_insert_dimension_template(mapper, connection, target):
#     _assign_sqlite_id(mapper, connection, target, DimensionTemplate.__table__)


# @event.listens_for(Dimension, "before_insert")
# def _before_insert_dimension(mapper, connection, target):
#     _assign_sqlite_id(mapper, connection, target, Dimension.__table__)


# @event.listens_for(QuestionAnalysisConfig, "before_insert")
# def _before_insert_question(mapper, connection, target):
#     _assign_sqlite_id(mapper, connection, target, QuestionAnalysisConfig.__table__)


# @event.listens_for(PromptConfig, "before_insert")
# def _before_insert_prompt(mapper, connection, target):
#     _assign_sqlite_id(mapper, connection, target, PromptConfig.__table__)


# @event.listens_for(Report, "before_insert")
# def _before_insert_report(mapper, connection, target):
#     _assign_sqlite_id(mapper, connection, target, Report.__table__)


# @event.listens_for(OutlineChapter, "before_insert")
# def _before_insert_outline_chapter(mapper, connection, target):
#     _assign_sqlite_id(mapper, connection, target, OutlineChapter.__table__)


# @event.listens_for(ReportStructure, "before_insert")
# def _before_insert_report_structure(mapper, connection, target):
#     _assign_sqlite_id(mapper, connection, target, ReportStructure.__table__)


# @event.listens_for(StructureNode, "before_insert")
# def _before_insert_structure_node(mapper, connection, target):
#     _assign_sqlite_id(mapper, connection, target, StructureNode.__table__)


# @event.listens_for(TemplateExtraction, "before_insert")
# def _before_insert_template_extraction(mapper, connection, target):
#     _assign_sqlite_id(mapper, connection, target, TemplateExtraction.__table__)
