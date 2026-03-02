报告结构配置功能优化设计方案

文档信息

项目	内容
版本	v1.0
日期	2026-02-27
状态	终稿
适用范围	报告生成工具 v2.0
目录

项目概述
系统架构设计
核心功能设计
数据库设计
API接口设计
前端界面设计
实施计划
风险与应对
附录
一、项目概述

1.1 背景

当前报告结构配置功能需要用户完全手动创建节点树，存在以下问题：

配置成本高：每个结构需30分钟以上手工配置
重复劳动：相似报告需重复配置
题号映射易错：人工对照Excel容易出错
术语难理解："容器节点"概念不清晰
1.2 目标

构建 "Word模板 → AI提取 → 用户调整 → 保存复用" 的新工作流：

指标	当前	目标	提升
结构配置时间	30分钟	5分钟	83%↓
题号映射准确率	70%	95%	36%↑
配置门槛	高	低	显著降低
1.3 范围

包含：

Word文档结构智能提取
AI节点类型识别
可视化调整界面
模板复用机制
三种报告模板差异化处理
不包含：

图表配置化（暂不实施）
Excel结构提取（本次不采用）
二、系统架构设计

2.1 整体架构

┌─────────────────────────────────────────────────────────────────┐
│                         前端层                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ 模板上传页面  │  │ 结构预览界面  │  │ 节点编辑弹窗  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API网关层                                │
│                    FastAPI Router                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         服务层                                   │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │ WordStructure    │  │ AINodeClassifier │                    │
│  │ Extractor        │  │                  │                    │
│  │ (文档解析)        │  │ (AI识别)         │                    │
│  └──────────────────┘  └──────────────────┘                    │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │ TemplateStructure│  │ StructureService │                    │
│  │ Service          │  │ (节点管理)       │                    │
│  │ (流程编排)        │  │                  │                    │
│  └──────────────────┘  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         数据层                                   │
│  MySQL + Redis(缓存) + 文件存储                                  │
└─────────────────────────────────────────────────────────────────┘
2.2 核心流程

Step 1: Word模板上传
    │
    ▼
Step 2: 文档解析（python-docx）
    ├── 提取标题层级（Heading 1/2/3）
    ├── 提取内容预览
    └── 构建树形结构
    │
    ▼
Step 3: AI节点识别
    ├── 规则引擎快速分类（高置信度）
    ├── LLM辅助识别（低置信度）
    └── 生成节点类型推荐
    │
    ▼
Step 4: 可视化预览
    ├── 展示树形结构
    ├── 标注节点类型
    ├── 显示置信度
    └── 高亮待确认节点
    │
    ▼
Step 5: 用户调整
    ├── 修改节点标题
    ├── 调整节点类型
    ├── 配置题号映射
    └── 调整层级关系
    │
    ▼
Step 6: 保存复用
    ├── 保存为Structure配置
    ├── 记录提取历史
    └── 加入模板库
三、核心功能设计

3.1 Word文档解析服务

3.1.1 服务定位

负责从Word文档中提取章节结构，输出标准化的树形数据。

3.1.2 核心类设计

# backend/app/services/word_structure_extractor.py

from docx import Document
from typing import List, Dict, Any, Optional
import re
from dataclasses import dataclass

@dataclass
class HeadingNode:
    """标题节点"""
    title: str
    level: int  # 1=一级标题, 2=二级标题, etc.
    style_name: str
    content_preview: str
    children: List['HeadingNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

class WordStructureExtractor:
    """
    Word报告模板结构提取器
    
    功能：
    1. 解析Word文档中的标题层级
    2. 提取各章节内容预览
    3. 构建树形结构
    4. 识别特殊节点（如数据分析章节）
    """
    
    def __init__(self):
        self.heading_patterns = [
            r'^Heading\s*(\d+)$',  # Heading 1, Heading 2
            r'^标题\s*(\d+)$',      # 标题 1, 标题 2
            r'^目录\s*(\d+)$',      # 目录 1, 目录 2
        ]
    
    def extract_structure(self, file_path: str) -> List[Dict[str, Any]]:
        """
        主入口：提取Word文档结构
        
        Args:
            file_path: Word文档路径
            
        Returns:
            树形结构的JSON表示
        """
        try:
            doc = Document(file_path)
            headings = self._extract_all_headings(doc)
            tree = self._build_tree(headings)
            return self._to_dict_list(tree)
        except Exception as e:
            raise StructureExtractionError(f"文档解析失败: {str(e)}")
    
    def _extract_all_headings(self, doc: Document) -> List[HeadingNode]:
        """提取文档中所有标题"""
        headings = []
        
        for para in doc.paragraphs:
            level = self._get_heading_level(para)
            if level:
                content_preview = self._extract_content_preview(doc, para)
                node = HeadingNode(
                    title=para.text.strip(),
                    level=level,
                    style_name=para.style.name,
                    content_preview=content_preview
                )
                headings.append(node)
        
        return headings
    
    def _get_heading_level(self, para) -> Optional[int]:
        """判断段落是否为标题，返回层级"""
        style_name = para.style.name
        
        # 匹配标准Heading样式
        for pattern in self.heading_patterns:
            match = re.match(pattern, style_name, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        # 备选：通过大纲级别判断
        if hasattr(para, '_p') and para._p.pPr is not None:
            outline_lvl = para._p.pPr.find(qn('w:outlineLvl'))
            if outline_lvl is not None:
                val = outline_lvl.get(qn('w:val'))
                if val is not None:
                    return int(val) + 1
        
        # 启发式判断：通过字体大小和加粗
        if self._is_heading_by_format(para):
            return self._estimate_level_by_format(para)
        
        return None
    
    def _is_heading_by_format(self, para) -> bool:
        """通过格式特征判断是否为标题"""
        if not para.runs:
            return False
        
        run = para.runs[0]
        # 加粗且字体较大
        if run.bold and run.font.size and run.font.size.pt > 12:
            return True
        
        return False
    
    def _estimate_level_by_format(self, para) -> int:
        """通过字体大小估计层级"""
        if not para.runs:
            return 1
        
        size = para.runs[0].font.size
        if size:
            pt = size.pt
            if pt >= 16:
                return 1
            elif pt >= 14:
                return 2
            elif pt >= 12:
                return 3
        
        return 1
    
    def _extract_content_preview(self, doc: Document, heading_para, max_length: int = 300) -> str:
        """
        提取标题后的内容预览
        
        Args:
            doc: 文档对象
            heading_para: 标题段落
            max_length: 最大预览长度
            
        Returns:
            内容预览文本
        """
        content_parts = []
        found_heading = False
        char_count = 0
        
        for para in doc.paragraphs:
            if para == heading_para:
                found_heading = True
                continue
            
            if found_heading:
                # 遇到下一个标题就停止
                if self._get_heading_level(para):
                    break
                
                text = para.text.strip()
                if text:
                    content_parts.append(text)
                    char_count += len(text)
                    
                    if char_count >= max_length:
                        break
        
        preview = ' '.join(content_parts)
        return preview[:max_length]
    
    def _build_tree(self, headings: List[HeadingNode]) -> List[HeadingNode]:
        """
        将扁平的标题列表构建为树形结构
        
        算法：使用栈维护当前路径
        """
        if not headings:
            return []
        
        root = []
        stack = []
        
        for heading in headings:
            # 弹出栈中层级大于等于当前节点的
            while stack and stack[-1].level >= heading.level:
                stack.pop()
            
            # 当前节点入栈
            if stack:
                # 有父节点，添加到父节点的children
                stack[-1].children.append(heading)
            else:
                # 根节点
                root.append(heading)
            
            stack.append(heading)
        
        return root
    
    def _to_dict_list(self, nodes: List[HeadingNode]) -> List[Dict[str, Any]]:
        """转换为字典列表"""
        result = []
        for node in nodes:
            item = {
                'title': node.title,
                'level': node.level,
                'style_name': node.style_name,
                'content_preview': node.content_preview,
                'children': self._to_dict_list(node.children)
            }
            result.append(item)
        return result


class StructureExtractionError(Exception):
    """结构提取异常"""
    pass
3.1.3 关键特性

特性	说明
多级样式支持	支持Heading 1/2/3、标题1/2/3、目录1/2/3等
格式启发式	无样式标记时通过字体大小/加粗识别
内容预览	自动提取标题后300字内容用于AI分析
容错处理	格式不规范的文档也能尽可能提取
3.2 AI节点分类服务

3.2.1 服务定位

根据标题和内容自动识别节点类型，决定每个章节是AI生成、数据分析还是固定内容。

3.2.2 分类策略

采用 规则引擎 + AI辅助 的混合策略：

输入: 标题 + 内容预览 + 层级
    │
    ├──▶ 规则引擎（快速路径）
    │       ├── 固定内容关键词匹配 → 高置信度直接返回
    │       ├── 数据分析关键词匹配 → 中高置信度返回
    │       └── 容器节点特征匹配 → 中置信度返回
    │   
    └──▶ AI分类（慢速路径，规则置信度<0.85时触发）
            └── 调用LLM进行语义分析
3.2.3 核心类设计

# backend/app/services/ai_node_classifier.py

from typing import Dict, Any, List, Optional
from enum import Enum
import re

class NodeType(str, Enum):
    """节点类型枚举"""
    AI_CHAPTER = "ai_chapter"          # AI生成章节
    FIXED_CONTENT = "fixed_content"    # 固定内容
    CONTAINER = "container"            # 章节分组（原容器节点）
    DATA_ANALYSIS = "data_analysis"    # 数据分析

class ClassificationResult:
    """分类结果"""
    def __init__(self, node_type: NodeType, confidence: float, reasoning: str, 
                 suggested_settings: Dict[str, Any] = None):
        self.node_type = node_type
        self.confidence = confidence
        self.reasoning = reasoning
        self.suggested_settings = suggested_settings or {}

class AINodeClassifier:
    """
    AI节点分类器
    
    功能：
    1. 基于规则快速分类（高置信度场景）
    2. 基于LLM智能分类（复杂场景）
    3. 提供分类置信度和理由
    """
    
    # 规则库配置
    RULES = {
        'fixed_content': {
            'keywords': ['说明', '免责', '声明', '附件', '附录', '注'],
            'title_patterns': [r'.*说明$', r'.*声明$', r'附件\s*\d*', r'附录\s*\d*'],
            'confidence': 0.95,
            'settings': {'fixed_content': ''}
        },
        'data_analysis': {
            'keywords': ['分析', '统计', '结果', '满意度', '评价', '反馈', '调研结果', 
                        '用药', '疗效', '体验', '认知', '分布'],
            'title_patterns': [
                r'\d+\.\d+',  # 4.1, 4.2 等维度编号
                r'.*分析$',
                r'.*统计$'
            ],
            'min_level': 2,  # 通常是二级标题
            'confidence': 0.85,
            'settings': {
                'show_data_table': True,
                'show_ai_interpretation': False,
                'question_number': None
            }
        },
        'ai_chapter': {
            'keywords': ['前言', '背景', '结论', '建议', '总结', '概述', '介绍'],
            'title_patterns': [r'前言', r'.*背景', r'.*结论', r'.*建议', r'总结'],
            'confidence': 0.80,
            'settings': {}
        }
    }
    
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
    
    async def classify(self, title: str, content_preview: str, level: int) -> ClassificationResult:
        """
        分类主入口
        
        策略：
        1. 先使用规则引擎
        2. 规则置信度>=0.85直接返回
        3. 否则使用AI辅助
        """
        # 1. 规则引擎
        rule_result = self._classify_by_rules(title, content_preview, level)
        if rule_result.confidence >= 0.85:
            return rule_result
        
        # 2. AI辅助（如果可用）
        if self.llm_service:
            ai_result = await self._classify_by_llm(title, content_preview, level)
            # 如果AI置信度更高，使用AI结果
            if ai_result.confidence > rule_result.confidence:
                return ai_result
        
        # 3. 默认返回规则结果
        return rule_result
    
    def _classify_by_rules(self, title: str, content_preview: str, level: int) -> ClassificationResult:
        """基于规则的分类"""
        title_lower = title.lower()
        
        # 1. 检查固定内容（最高优先级）
        fixed_match = self._match_rules(title, content_preview, self.RULES['fixed_content'])
        if fixed_match:
            return ClassificationResult(
                node_type=NodeType.FIXED_CONTENT,
                confidence=fixed_match['confidence'],
                reasoning=f"标题匹配固定内容规则: {fixed_match['matched']}",
                suggested_settings=self.RULES['fixed_content']['settings']
            )
        
        # 2. 检查数据分析（通常是二级及以下标题）
        if level >= self.RULES['data_analysis']['min_level']:
            data_match = self._match_rules(title, content_preview, self.RULES['data_analysis'])
            if data_match:
                settings = self.RULES['data_analysis']['settings'].copy()
                # 尝试提取维度编号
                dimension_num = self._extract_dimension_number(title)
                if dimension_num:
                    settings['dimension_number'] = dimension_num
                    
                return ClassificationResult(
                    node_type=NodeType.DATA_ANALYSIS,
                    confidence=data_match['confidence'],
                    reasoning=f"标题匹配数据分析规则: {data_match['matched']}",
                    suggested_settings=settings
                )
        
        # 3. 检查AI章节
        ai_match = self._match_rules(title, content_preview, self.RULES['ai_chapter'])
        if ai_match:
            return ClassificationResult(
                node_type=NodeType.AI_CHAPTER,
                confidence=ai_match['confidence'],
                reasoning=f"标题匹配AI章节规则: {ai_match['matched']}",
                suggested_settings=self.RULES['ai_chapter']['settings']
            )
        
        # 4. 容器节点判断（一级标题且包含编号）
        if level == 1 and re.search(r'^[一二三四五六七八九十\d]+[、.．]', title):
            return ClassificationResult(
                node_type=NodeType.CONTAINER,
                confidence=0.75,
                reasoning="一级标题，包含章节编号，判定为章节分组",
                suggested_settings={}
            )
        
        # 5. 默认：AI章节
        return ClassificationResult(
            node_type=NodeType.AI_CHAPTER,
            confidence=0.60,
            reasoning="未匹配到明确规则，默认归类为AI生成章节",
            suggested_settings={}
        )
    
    def _match_rules(self, title: str, content: str, rule_config: Dict) -> Optional[Dict]:
        """匹配规则"""
        title_lower = title.lower()
        
        # 检查关键词
        for keyword in rule_config['keywords']:
            if keyword in title_lower:
                return {
                    'matched': f"关键词'{keyword}'",
                    'confidence': rule_config['confidence']
                }
        
        # 检查正则模式
        for pattern in rule_config.get('title_patterns', []):
            if re.search(pattern, title):
                return {
                    'matched': f"模式'{pattern}'",
                    'confidence': rule_config['confidence']
                }
        
        return None
    
    def _extract_dimension_number(self, title: str) -> Optional[str]:
        """从标题中提取维度编号（如4.1）"""
        match = re.search(r'(\d+\.\d+)', title)
        if match:
            return match.group(1)
        return None
    
    async def _classify_by_llm(self, title: str, content_preview: str, level: int) -> ClassificationResult:
        """使用LLM进行分类"""
        
        prompt = f"""
请分析以下报告章节，判断其最合适的节点类型。

【章节信息】
标题：{title}
层级：Level {level}
内容预览：{content_preview[:200]}

【可选节点类型】
1. ai_chapter - AI生成章节：需要AI撰写文字内容的章节，如前言、背景、结论、建议
2. fixed_content - 固定内容：固定不变的文本，如说明、免责声明、附件
3. container - 章节分组：仅作为容器组织子章节，本身无内容，如"四、问卷结果分析"
4. data_analysis - 数据分析：展示数据表格和分析的章节，如"4.1 用药基础信息"

【输出格式】
请返回JSON格式：
{{
    "node_type": "ai_chapter|fixed_content|container|data_analysis",
    "confidence": 0.0-1.0,
    "reasoning": "判断理由（中文）",
    "suggested_settings": {{
        "show_data_table": true/false,  // 仅data_analysis类型
        "show_ai_interpretation": true/false  // 是否显示AI解读
    }}
}}
"""
        
        # 调用LLM服务
        response = await self.llm_service.complete(prompt)
        
        # 解析结果
        try:
            result = json.loads(response)
            return ClassificationResult(
                node_type=NodeType(result['node_type']),
                confidence=result['confidence'],
                reasoning=result['reasoning'],
                suggested_settings=result.get('suggested_settings', {})
            )
        except Exception as e:
            # 解析失败，返回默认结果
            return ClassificationResult(
                node_type=NodeType.AI_CHAPTER,
                confidence=0.50,
                reasoning=f"LLM解析失败，使用默认值: {str(e)}",
                suggested_settings={}
            )


# 模板类型特定的分类器
class DoctorTemplateClassifier(AINodeClassifier):
    """医生问卷模板专用分类器"""
    
    RULES = {
        **AINodeClassifier.RULES,
        'data_analysis': {
            **AINodeClassifier.RULES['data_analysis'],
            'keywords': AINodeClassifier.RULES['data_analysis']['keywords'] + [
                '满意度', '评价', '认知度', '知晓率', '处方', '推荐'
            ]
        }
    }

class PatientTemplateClassifier(AINodeClassifier):
    """患者问卷模板专用分类器"""
    
    RULES = {
        **AINodeClassifier.RULES,
        'data_analysis': {
            **AINodeClassifier.RULES['data_analysis'],
            'keywords': AINodeClassifier.RULES['data_analysis']['keywords'] + [
                '用药', '疗效', '体验', '症状', '改善', '服用'
            ]
        }
    }
3.2.4 分类规则详解

节点类型	识别规则	置信度	典型示例
fixed_content	标题包含：说明、免责、声明、附件	0.95	"三、问卷说明"、"附件2：免责声明"
data_analysis	标题包含：分析、统计、满意度、评价，或匹配X.X格式	0.85	"4.1 用药基础信息"、"满意度分析"
ai_chapter	标题包含：前言、背景、结论、建议	0.80	"前言"、"五、调研结论"
container	一级标题且包含章节编号（一、二、1.、2.）	0.75	"四、问卷结果分析"
3.3 模板结构提取服务

3.3.1 服务定位

整合Word解析和AI分类，提供完整的模板提取流程。

3.3.2 核心类设计

# backend/app/services/template_structure_service.py

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib
import json

@dataclass
class ExtractedNode:
    """提取的节点"""
    title: str
    level: int
    node_type: str
    confidence: float
    reasoning: str
    children: List['ExtractedNode'] = None
    settings: Dict[str, Any] = None
    ai_recommended: bool = True
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.settings is None:
            self.settings = {}

@dataclass
class ExtractionResult:
    """提取结果"""
    extraction_id: int
    template_type: str
    structure_tree: List[Dict[str, Any]]
    overall_confidence: float
    low_confidence_nodes: List[Dict[str, Any]]
    source_file_hash: str

class TemplateStructureService:
    """
    模板结构提取服务（主服务）
    
    职责：
    1. 协调Word解析和AI分类
    2. 管理提取流程
    3. 保存提取历史
    4. 提供模板复用
    """
    
    def __init__(self, db_session, llm_service=None):
        self.db = db_session
        self.word_extractor = WordStructureExtractor()
        self.llm_service = llm_service
    
    async def extract_from_word(
        self,
        file_path: str,
        template_type: str,  # 'doctor' | 'patient'
        original_filename: str
    ) -> ExtractionResult:
        """
        从Word文档提取结构（主入口）
        
        流程：
        1. 计算文件哈希（用于缓存）
        2. 检查是否已有缓存的提取结果
        3. 解析Word文档
        4. AI分类每个节点
        5. 计算整体置信度
        6. 保存提取记录
        7. 返回结果
        """
        # 1. 计算文件哈希
        file_hash = self._calculate_file_hash(file_path)
        
        # 2. 检查缓存
        cached = self._get_cached_extraction(file_hash)
        if cached:
            return cached
        
        # 3. 解析Word
        raw_structure = self.word_extractor.extract_structure(file_path)
        
        # 4. 获取对应的分类器
        classifier = self._get_classifier(template_type)
        
        # 5. 递归分类
        classified_tree = await self._classify_tree(raw_structure, classifier)
        
        # 6. 计算整体置信度
        overall_confidence = self._calculate_overall_confidence(classified_tree)
        
        # 7. 识别低置信度节点
        low_confidence_nodes = self._find_low_confidence_nodes(classified_tree)
        
        # 8. 保存到数据库
        extraction_record = TemplateExtraction(
            original_filename=original_filename,
            file_hash=file_hash,
            template_type=template_type,
            extracted_structure=classified_tree,
            confidence_scores=self._extract_confidences(classified_tree)
        )
        self.db.add(extraction_record)
        self.db.commit()
        
        return ExtractionResult(
            extraction_id=extraction_record.id,
            template_type=template_type,
            structure_tree=classified_tree,
            overall_confidence=overall_confidence,
            low_confidence_nodes=low_confidence_nodes,
            source_file_hash=file_hash
        )
    
    async def _classify_tree(
        self,
        nodes: List[Dict[str, Any]],
        classifier: AINodeClassifier,
        parent_type: Optional[str] = None
    ) -> List[ExtractedNode]:
        """递归分类节点树"""
        result = []
        
        for node in nodes:
            # 分类当前节点
            classification = await classifier.classify(
                title=node['title'],
                content_preview=node.get('content_preview', ''),
                level=node['level']
            )
            
            # 容器节点的子节点默认为data_analysis
            if classification.node_type == NodeType.CONTAINER:
                child_classifier = DataAnalysisDefaultClassifier()
            else:
                child_classifier = classifier
            
            # 递归处理子节点
            children = []
            if node.get('children'):
                children = await self._classify_tree(
                    node['children'], 
                    child_classifier,
                    classification.node_type.value
                )
            
            extracted = ExtractedNode(
                title=node['title'],
                level=node['level'],
                node_type=classification.node_type.value,
                confidence=classification.confidence,
                reasoning=classification.reasoning,
                children=children,
                settings=classification.suggested_settings
            )
            
            result.append(extracted)
        
        return result
    
    def _get_classifier(self, template_type: str) -> AINodeClassifier:
        """根据模板类型获取分类器"""
        classifiers = {
            'doctor': DoctorTemplateClassifier(self.llm_service),
            'patient': PatientTemplateClassifier(self.llm_service)
        }
        return classifiers.get(template_type, AINodeClassifier(self.llm_service))
    
    def _calculate_overall_confidence(self, nodes: List[ExtractedNode]) -> float:
        """计算整体置信度（加权平均）"""
        if not nodes:
            return 1.0
        
        total_confidence = 0
        total_weight = 0
        
        def calc_weighted(node: ExtractedNode, weight: float = 1.0):
            nonlocal total_confidence, total_weight
            total_confidence += node.confidence * weight
            total_weight += weight
            
            for child in node.children:
                calc_weighted(child, weight * 0.8)  # 子节点权重递减
        
        for node in nodes:
            calc_weighted(node)
        
        return round(total_confidence / total_weight, 2) if total_weight > 0 else 0
    
    def _find_low_confidence_nodes(
        self,
        nodes: List[ExtractedNode],
        threshold: float = 0.75
    ) -> List[Dict[str, Any]]:
        """找出低置信度节点"""
        result = []
        
        def find_recursive(node: ExtractedNode, path: str = ""):
            current_path = f"{path}/{node.title}" if path else node.title
            
            if node.confidence < threshold:
                result.append({
                    'path': current_path,
                    'title': node.title,
                    'current_type': node.node_type,
                    'confidence': node.confidence,
                    'reasoning': node.reasoning
                })
            
            for child in node.children:
                find_recursive(child, current_path)
        
        for node in nodes:
            find_recursive(node)
        
        return result
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件MD5哈希"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _get_cached_extraction(self, file_hash: str) -> Optional[ExtractionResult]:
        """获取缓存的提取结果"""
        record = self.db.query(TemplateExtraction).filter(
            TemplateExtraction.file_hash == file_hash
        ).first()
        
        if record:
            return ExtractionResult(
                extraction_id=record.id,
                template_type=record.template_type,
                structure_tree=record.extracted_structure,
                overall_confidence=record.overall_confidence,
                low_confidence_nodes=[],  # 缓存时不再计算
                source_file_hash=record.file_hash
            )
        return None
    
    def confirm_and_save_structure(
        self,
        extraction_id: int,
        structure_name: str,
        user_modifications: List[Dict[str, Any]]
    ) -> int:
        """
        用户确认后保存为正式结构
        
        Args:
            extraction_id: 提取记录ID
            structure_name: 用户指定的结构名称
            user_modifications: 用户的修改记录
            
        Returns:
            structure_id: 创建的结构ID
        """
        # 1. 获取提取记录
        extraction = self.db.query(TemplateExtraction).get(extraction_id)
        if not extraction:
            raise ValueError("提取记录不存在")
        
        # 2. 应用用户修改
        final_structure = self._apply_modifications(
            extraction.extracted_structure,
            user_modifications
        )
        
        # 3. 创建ReportStructure
        report_structure = ReportStructure(
            structure_name=structure_name,
            report_type=extraction.template_type,
            is_active=True
        )
        self.db.add(report_structure)
        self.db.flush()
        
        # 4. 创建StructureNode
        self._create_structure_nodes(
            report_structure.id,
            final_structure
        )
        
        # 5. 更新提取记录
        extraction.final_structure_id = report_structure.id
        extraction.user_modifications = user_modifications
        extraction.is_reusable = True
        
        self.db.commit()
        
        return report_structure.id
    
    def _apply_modifications(
        self,
        original_structure: List[Dict[str, Any]],
        modifications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """应用用户修改到结构"""
        # 实现修改逻辑
        # ...
        return original_structure
    
    def _create_structure_nodes(
        self,
        structure_id: int,
        nodes: List[Dict[str, Any]],
        parent_id: Optional[int] = None
    ):
        """递归创建StructureNode记录"""
        for i, node_data in enumerate(nodes):
            node = StructureNode(
                structure_id=structure_id,
                parent_id=parent_id,
                level=node_data['level'],
                node_type=node_data['node_type'],
                title=node_data['title'],
                sort_order=i,
                ai_recommended=node_data.get('ai_recommended', False),
                confidence_score=node_data.get('confidence'),
                recommendation_reason=node_data.get('reasoning'),
                modified_by_user=node_data.get('modified', False)
            )
            
            # 应用特定类型的设置
            if node.node_type == 'data_analysis':
                node.show_data_table = node_data.get('settings', {}).get('show_data_table', True)
                node.show_ai_interpretation = node_data.get('settings', {}).get('show_ai_interpretation', False)
            
            if node.node_type == 'fixed_content':
                node.fixed_content = node_data.get('settings', {}).get('fixed_content', '')
            
            self.db.add(node)
            self.db.flush()
            
            # 递归创建子节点
            if node_data.get('children'):
                self._create_structure_nodes(structure_id, node_data['children'], node.id)


# 特殊分类器：容器节点下的子节点默认为数据分析
class DataAnalysisDefaultClassifier(AINodeClassifier):
    """默认将子节点分类为数据分析"""
    
    async def classify(self, title: str, content_preview: str, level: int) -> ClassificationResult:
        # 先尝试正常分类
        result = await super().classify(title, content_preview, level)
        
        # 如果置信度不高，默认为数据分析
        if result.confidence < 0.7 and level >= 2:
            return ClassificationResult(
                node_type=NodeType.DATA_ANALYSIS,
                confidence=0.75,
                reasoning="作为章节分组的子节点，默认归类为数据分析",
                suggested_settings={
                    'show_data_table': True,
                    'show_ai_interpretation': False
                }
            )
        
        return result
3.4 术语优化

将"容器节点"改为更易理解的名称：

旧名称	新名称	代码值	说明
容器节点	章节分组	container	用于组织子章节的父级节点
-	AI生成章节	ai_chapter	内容由AI生成的章节
-	固定内容	fixed_content	固定不变的文本内容
-	数据分析	data_analysis	展示数据表格的章节
前端显示映射：

const nodeTypeLabels = {
    'ai_chapter': 'AI生成章节',
    'fixed_content': '固定内容',
    'container': '章节分组',  // 改为更易理解的名称
    'data_analysis': '数据分析'
};
四、数据库设计

4.1 新增表

4.1.1 模板提取记录表

-- template_extractions
CREATE TABLE template_extractions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- 源文件信息
    original_filename VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_hash VARCHAR(64) NOT NULL UNIQUE COMMENT '文件MD5哈希',
    file_size INT COMMENT '文件大小(字节)',
    template_type ENUM('doctor', 'patient') NOT NULL COMMENT '模板类型',
    
    -- 提取结果
    extracted_structure JSON NOT NULL COMMENT '提取的节点树JSON',
    confidence_scores JSON COMMENT '各节点置信度',
    overall_confidence DECIMAL(3,2) COMMENT '整体置信度',
    
    -- 处理状态
    status ENUM('processing', 'completed', 'failed') DEFAULT 'processing' COMMENT '处理状态',
    error_message TEXT COMMENT '错误信息(失败时)',
    
    -- 用户确认后的关联
    final_structure_id BIGINT COMMENT '确认后创建的structure_id',
    user_modifications JSON COMMENT '用户修改记录',
    
    -- 统计
    is_reusable BOOLEAN DEFAULT TRUE COMMENT '是否可作为模板复用',
    use_count INT DEFAULT 0 COMMENT '被使用次数',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_file_hash (file_hash),
    INDEX idx_template_type (template_type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Word模板提取记录表';
4.1.2 扩展现有表

-- structure_nodes 表扩展
ALTER TABLE structure_nodes ADD COLUMN (
    ai_recommended BOOLEAN DEFAULT FALSE COMMENT '是否AI推荐',
    confidence_score DECIMAL(3,2) COMMENT 'AI置信度',
    recommendation_reason TEXT COMMENT '推荐理由',
    modified_by_user BOOLEAN DEFAULT FALSE COMMENT '是否被用户修改',
    original_title VARCHAR(200) COMMENT 'AI推荐的原标题'
);
4.2 实体关系图

TemplateExtraction (1) ────────► (N) ReportStructure
        │                              │
        │                              │
        └────────► extracted_structure  │
                   (JSON存储节点树)      │
                                      │
                                      ▼
                              StructureNode (N)
                                      │
                                      ├─► ai_chapter
                                      ├─► fixed_content
                                      ├─► container (章节分组)
                                      └─► data_analysis
五、API接口设计

5.1 模板提取接口

# POST /api/v1/templates/extract
# 上传Word模板并提取结构

Request:
  Content-Type: multipart/form-data
  
  Fields:
    - template_type: string (required) ["doctor", "patient"]
    - word_file: file (required) [.docx]

Response:
  Success (200):
    {
      "code": 200,
      "message": "success",
      "data": {
        "extraction_id": 123,
        "template_type": "doctor",
        "overall_confidence": 0.88,
        "structure_tree": [
          {
            "title": "前言",
            "level": 1,
            "node_type": "ai_chapter",
            "confidence": 0.92,
            "reasoning": "标题匹配AI章节规则",
            "settings": {},
            "children": []
          },
          {
            "title": "四、问卷结果分析",
            "level": 1,
            "node_type": "container",
            "confidence": 0.85,
            "reasoning": "一级标题，包含章节编号",
            "settings": {},
            "children": [
              {
                "title": "4.1 用药基础信息",
                "level": 2,
                "node_type": "data_analysis",
                "confidence": 0.90,
                "reasoning": "标题匹配数据分析规则: 模式'4.1'",
                "settings": {
                  "show_data_table": true,
                  "show_ai_interpretation": false,
                  "dimension_number": "4.1"
                },
                "children": []
              }
            ]
          }
        ],
        "low_confidence_nodes": [
          {
            "path": "/六、建议",
            "title": "建议",
            "current_type": "ai_chapter",
            "confidence": 0.65,
            "reasoning": "未匹配到明确规则，默认归类为AI生成章节"
          }
        ]
      }
    }
  
  Error (400/500):
    {
      "code": 400,
      "message": "文档解析失败: 无效的Word格式",
      "data": null
    }
5.2 确认并保存结构接口

# POST /api/v1/templates/extractions/{extraction_id}/confirm
# 确认提取结果并保存为正式结构

Request:
  Content-Type: application/json
  
  Body:
    {
      "structure_name": "医生问卷标准结构",
      "modified_nodes": [
        {
          "path": "/六、建议",
          "changes": {
            "node_type": "ai_chapter",
            "title": "六、结论与建议"
          }
        }
      ],
      "question_mappings": [
        {
          "node_path": "/四、问卷结果分析/4.1 用药基础信息",
          "question_numbers": [1, 2, 3]
        }
      ]
    }

Response:
  Success (200):
    {
      "code": 200,
      "message": "success",
      "data": {
        "structure_id": 456,
        "structure_name": "医生问卷标准结构",
        "node_count": 15,
        "created_at": "2026-02-27T10:30:00Z"
      }
    }
5.3 获取可复用模板列表

# GET /api/v1/templates/reusable
# 获取可复用的提取模板列表

Query Parameters:
  - template_type: string (optional) ["doctor", "patient"]
  - page: int (optional, default=1)
  - page_size: int (optional, default=20)

Response:
  {
    "code": 200,
    "message": "success",
    "data": {
      "total": 10,
      "page": 1,
      "page_size": 20,
      "list": [
        {
          "extraction_id": 123,
          "original_filename": "医生问卷模板-湖南省.docx",
          "template_type": "doctor",
          "overall_confidence": 0.88,
          "use_count": 5,
          "created_at": "2026-02-20T08:00:00Z"
        }
      ]
    }
  }
5.4 基于模板创建新结构

# POST /api/v1/templates/{extraction_id}/clone
# 基于已有模板创建新的结构（复制并修改）

Request:
  {
    "structure_name": "医生问卷结构-四川省版",
    "modifications": {
      // 可选的修改
    }
  }

Response:
  {
    "code": 200,
    "message": "success",
    "data": {
      "structure_id": 789,
      "extraction_id": 123
    }
  }
六、前端界面设计

6.1 页面结构

template-extract.html (模板提取页面)
├── 步骤指示器 (Step 1/2/3)
├── 文件上传区域
│   ├── 模板类型选择 (医生/患者)
│   ├── 文件拖拽/选择
│   └── 上传按钮
├── 解析进度展示 (解析中)
│   └── 进度条 + 步骤提示
└── 结果预览区域 (解析完成)
    ├── 整体置信度展示
    ├── 低置信度警告
    ├── 树形结构预览
    │   ├── 节点卡片 (可折叠)
    │   ├── 节点类型标签
    │   ├── 置信度指示
    │   └── 编辑按钮
    ├── 题号映射配置
    └── 操作按钮组
        ├── 保存为结构
        ├── 进入详细调整
        └── 重新解析
6.2 关键组件

6.2.1 文件上传组件

<!-- 文件上传区域 -->
<div class="upload-section">
  <h3>第一步：上传Word模板</h3>
  
  <div class="template-type-selector">
    <label>选择模板类型：</label>
    <select id="template-type" class="form-select">
      <option value="doctor">医生问卷模板</option>
      <option value="patient">患者问卷模板</option>
    </select>
    <p class="hint">不同类型的模板会有不同的AI识别规则</p>
  </div>
  
  <div class="file-upload-area" id="drop-zone">
    <input type="file" id="word-file" accept=".docx" hidden>
    <div class="upload-placeholder">
      <i class="fas fa-cloud-upload-alt fa-3x"></i>
      <p>拖拽Word文件到此处，或 <span class="clickable">点击选择</span></p>
      <p class="file-types">支持 .docx 格式</p>
    </div>
  </div>
  
  <div class="selected-file hidden" id="selected-file">
    <span class="filename"></span>
    <button class="btn-remove" onclick="clearFile()">×</button>
  </div>
  
  <button class="btn-primary btn-upload" onclick="startExtraction()" disabled>
    开始智能提取
  </button>
</div>
6.2.2 解析进度组件

<!-- 解析进度展示 -->
<div class="parsing-status hidden" id="parsing-status">
  <div class="progress-header">
    <div class="spinner"></div>
    <h4>AI正在分析报告结构...</h4>
  </div>
  
  <div class="progress-steps">
    <div class="step active" data-step="1">
      <div class="step-icon"><i class="fas fa-file-word"></i></div>
      <div class="step-text">解析文档</div>
    </div>
    <div class="step" data-step="2">
      <div class="step-icon"><i class="fas fa-sitemap"></i></div>
      <div class="step-text">识别层级</div>
    </div>
    <div class="step" data-step="3">
      <div class="step-icon"><i class="fas fa-brain"></i></div>
      <div class="step-text">AI分类</div>
    </div>
    <div class="step" data-step="4">
      <div class="step-icon"><i class="fas fa-check"></i></div>
      <div class="step-text">完成</div>
    </div>
  </div>
  
  <div class="progress-bar">
    <div class="progress-fill" style="width: 0%"></div>
  </div>
  
  <p class="current-task">正在提取标题层级...</p>
</div>
6.2.3 结构树预览组件

<!-- 结构树预览 -->
<div class="preview-section hidden" id="preview-section">
  <div class="preview-header">
    <h3>提取的报告结构</h3>
    <div class="confidence-badge" id="overall-confidence">
      整体置信度: <span class="score">88%</span>
      <i class="fas fa-info-circle" title="基于AI对每个节点的识别置信度计算"></i>
    </div>
  </div>
  
  <!-- 低置信度警告 -->
  <div class="alert alert-warning hidden" id="low-confidence-alert">
    <i class="fas fa-exclamation-triangle"></i>
    <span>发现 <strong id="low-count">2</strong> 个低置信度节点，建议检查并调整</span>
    <button class="btn-link" onclick="scrollToLowConfidence()">查看</button>
  </div>
  
  <!-- 树形结构 -->
  <div class="structure-tree" id="structure-tree">
    <!-- 递归渲染树节点 -->
  </div>
  
  <!-- 操作按钮 -->
  <div class="preview-actions">
    <button class="btn-secondary" onclick="reparse()">
      <i class="fas fa-redo"></i> 重新解析
    </button>
    <button class="btn-secondary" onclick="enterDetailedEdit()">
      <i class="fas fa-edit"></i> 详细调整
    </button>
    <button class="btn-primary" onclick="saveStructure()">
      <i class="fas fa-save"></i> 保存为结构配置
    </button>
  </div>
</div>
6.2.4 树节点组件

// Vue/React 组件伪代码
function TreeNode({ node, path = "" }) {
  const currentPath = path ? `${path} / ${node.title}` : node.title;
  const isLowConfidence = node.confidence < 0.75;
  const nodeTypeConfig = {
    'ai_chapter': { label: 'AI生成章节', color: 'blue' },
    'fixed_content': { label: '固定内容', color: 'gray' },
    'container': { label: '章节分组', color: 'purple' },
    'data_analysis': { label: '数据分析', color: 'green' }
  };
  
  return (
    <div class={`tree-node ${isLowConfidence ? 'low-confidence' : ''}`} 
         data-path={currentPath}>
      <div class="node-header" onclick="toggleExpand()">
        <div class="node-info">
          {node.children.length > 0 && (
            <i class={`fas fa-chevron-${expanded ? 'down' : 'right'}`}></i>
          )}
          <span class="level-badge">L{node.level}</span>
          <span class="node-title">{node.title}</span>
          <span class={`type-tag ${nodeTypeConfig[node.node_type].color}`}>
            {nodeTypeConfig[node.node_type].label}
          </span>
          {isLowConfidence && (
            <span class="confidence-warning" title={node.reasoning}>
              置信度: {(node.confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>
        <div class="node-actions">
          <button onclick="editNode(currentPath)" class="btn-icon" title="编辑">
            <i class="fas fa-edit"></i>
          </button>
          {node.node_type === 'data_analysis' && (
            <button onclick="configQuestions(currentPath)" class="btn-icon" title="配置题号">
              <i class="fas fa-list-ol"></i>
            </button>
          )}
        </div>
      </div>
      
      {/* 数据分析节点的题号映射 */}
      {node.node_type === 'data_analysis' && (
        <div class="question-mapping">
          <label>关联题号:</label>
          <input type="text" 
                 placeholder="如: 1,2,3" 
                 value={node.settings.question_numbers?.join(',')}
                 onchange="updateQuestionNumbers(currentPath, this.value)">
          <span class="hint">对应Excel中的题号</span>
        </div>
      )}
      
      {/* 子节点 */}
      {expanded && node.children.length > 0 && (
        <div class="children-container">
          {node.children.map(child => (
            <TreeNode node={child} path={currentPath} />
          ))}
        </div>
      )}
    </div>
  );
}
6.2.5 节点编辑弹窗

<!-- 节点编辑模态框 -->
<div class="modal" id="node-edit-modal">
  <div class="modal-content">
    <div class="modal-header">
      <h3>编辑节点</h3>
      <button class="btn-close" onclick="closeModal()">×</button>
    </div>
    
    <div class="modal-body">
      <div class="form-group">
        <label>节点标题</label>
        <input type="text" id="edit-title" class="form-control">
        <span class="original-title" id="original-title"></span>
      </div>
      
      <div class="form-group">
        <label>节点类型</label>
        <select id="edit-node-type" class="form-control">
          <option value="ai_chapter">AI生成章节</option>
          <option value="fixed_content">固定内容</option>
          <option value="container">章节分组</option>
          <option value="data_analysis">数据分析</option>
        </select>
        <p class="ai-reason" id="ai-reason"></p>
      </div>
      
      <!-- 动态配置区域 -->
      <div id="dynamic-config">
        <!-- 数据分析配置 -->
        <div class="config-section" data-type="data_analysis">
          <div class="form-group">
            <label>
              <input type="checkbox" id="show-data-table" checked>
              显示数据表格
            </label>
          </div>
          <div class="form-group">
            <label>
              <input type="checkbox" id="show-ai-interpretation">
              显示AI解读
            </label>
          </div>
        </div>
        
        <!-- 固定内容配置 -->
        <div class="config-section hidden" data-type="fixed_content">
          <div class="form-group">
            <label>固定内容文本</label>
            <textarea id="fixed-content" rows="5" class="form-control"></textarea>
          </div>
        </div>
      </div>
    </div>
    
    <div class="modal-footer">
      <button class="btn-secondary" onclick="closeModal()">取消</button>
      <button class="btn-primary" onclick="saveNodeChanges()">保存修改</button>
    </div>
  </div>
</div>
七、实施计划

7.1 开发阶段划分

阶段	任务	工期	依赖
Phase 1	基础架构搭建	3天	-
- Word解析服务		
- AI分类服务（规则引擎）		
- 数据库表创建		
Phase 2	后端API开发	4天	Phase 1
- 模板提取API		
- 确认保存API		
- 缓存机制		
Phase 3	前端界面开发	4天	Phase 2
- 上传与解析页面		
- 树形结构预览		
- 节点编辑功能		
Phase 4	集成与优化	3天	Phase 3
- 前后端联调		
- LLM集成（可选）		
- 性能优化		
Phase 5	测试与部署	2天	Phase 4
- 单元测试		
- 集成测试		
- 文档编写		
总计		16天	
7.2 关键里程碑

Week 1:
  Day 1-3:  [M1] Word解析 + AI分类服务完成
  Day 4-5:  [M2] 后端API完成，可独立测试

Week 2:
  Day 6-9:  [M3] 前端界面完成
  Day 10:   [M4] 前后端集成完成

Week 3:
  Day 11-13: [M5] 优化与测试完成
  Day 14-16: [M6] 文档与部署完成
7.3 风险评估

风险	概率	影响	应对措施
Word格式不标准导致解析失败	中	高	1. 提供格式规范文档 2. 增强容错处理 3. 提供手动调整入口
AI分类准确率低	低	中	1. 优化规则库 2. 允许用户快速修正 3. 收集反馈迭代
大文档解析性能问题	低	中	1. 异步处理 2. 分页加载 3. 缓存机制
LLM服务不稳定	中	低	1. 规则引擎保底 2. 离线模式支持
八、风险与应对

8.1 技术风险

风险	描述	应对策略
Word格式多样性	不同用户创建的Word文档格式差异大	1. 支持多种标题样式识别
2. 提供格式规范指南
3. 增强异常处理
AI分类准确率	复杂章节可能识别错误	1. 规则引擎保底
2. 置信度可视化
3. 快速修正机制
性能瓶颈	大文档解析可能耗时较长	1. 异步处理
2. 进度实时反馈
3. 结果缓存
8.2 业务风险

风险	描述	应对策略
用户不接受	用户习惯于手动配置	1. 保留手动配置入口
2. 提供对比演示
3. 渐进式推广
模板标准不统一	三种模板格式差异大	1. 差异化分类器
2. 模板规范化引导
3. 持续优化规则
九、附录

9.1 名词解释

术语	解释
章节分组	原"容器节点"，用于组织子章节的父级节点，本身不生成内容
AI生成章节	内容由AI大模型生成的章节，如前言、结论
数据分析节点	展示Excel数据表格的章节，可配置是否显示AI解读
固定内容	固定不变的文本章节，如免责声明
置信度	AI对节点类型识别结果的确定程度（0-1）


# 新增优化点
📋 「图表生成」功能完整设计方案

一、变更范围总览

文件	变更类型	变更内容
report_structure.py	新增字段	charts, content_order
structure-config.html	新增UI	图表多选配置区域
word_service.py	新增方法	_generate_charts(), 修改 _add_dimension_analysis()
数据库	新增字段	structure_nodes.charts, content_order
二、数据结构（后端）

# backend/app/schemas/report_structure.py

# 在现有 StructureNodeBase 中新增字段（约第14行后）
class StructureNodeBase(BaseModel):
    # ... 现有字段保持不变 ...
    show_data_table: bool = Field(default=True, description="显示数据表格")
    show_ai_interpretation: bool = Field(default=False, description="显示AI解读")
    
    # === 新增字段 ===
    charts: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="图表配置列表 [{chart_type, sort_order, config}]"
    )
    content_order: List[str] = Field(
        default_factory=lambda: ["chart", "table", "interpretation"],
        description="内容展示顺序"
    )
    
    # ... 其他字段不变 ...
Chart配置示例：

{
  "charts": [
    {
      "chart_type": "pie",
      "sort_order": 1,
      "config": {
        "show_percentage": true,
        "color_scheme": "blue"
      }
    }
  ],
  "content_order": ["chart", "table", "interpretation"]
}
三、API接口（无需变更）

复用现有的节点CRUD接口：

POST /structures/nodes - 创建节点（包含charts字段）
PUT /structures/nodes/{id} - 更新节点（包含charts字段）
GET /structures/{id} - 获取结构（返回charts字段）
四、前端界面（structure-config.html）

在现有Node Modal中新增图表配置区域（约第239行后）：

<!-- 在 field-display-options 后新增 -->
<div id="field-charts-config" class="hidden space-y-4 mt-4 border-t border-gray-200 pt-4">
    
    <!-- 图表类型多选 -->
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">关联图表</label>
        <div class="grid grid-cols-2 gap-2">
            <label class="flex items-center space-x-2 p-2 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <input type="checkbox" name="chart_type" value="pie" class="rounded text-[#6366F1]">
                <span class="text-sm">饼图</span>
            </label>
            <label class="flex items-center space-x-2 p-2 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <input type="checkbox" name="chart_type" value="bar" class="rounded text-[#6366F1]">
                <span class="text-sm">柱状图</span>
            </label>
            <label class="flex items-center space-x-2 p-2 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <input type="checkbox" name="chart_type" value="horizontal_bar" class="rounded text-[#6366F1]">
                <span class="text-sm">条形图</span>
            </label>
            <label class="flex items-center space-x-2 p-2 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <input type="checkbox" name="chart_type" value="radar" class="rounded text-[#6366F1]">
                <span class="text-sm">雷达图</span>
            </label>
        </div>
    </div>
    
    <!-- 内容顺序 -->
    <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">展示顺序</label>
        <select name="content_order" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
            <option value="chart,table,interpretation">图表 → 表格 → AI解读</option>
            <option value="table,chart,interpretation">表格 → 图表 → AI解读</option>
            <option value="interpretation,chart,table">AI解读 → 图表 → 表格</option>
            <option value="chart,interpretation,table">图表 → AI解读 → 表格</option>
        </select>
    </div>
</div>
JavaScript调整：

// 在 handleNodeTypeChange 函数中显示/隐藏图表配置
function handleNodeTypeChange() {
    const type = document.getElementById('node-type').value;
    // ... 现有代码 ...
    
    // 新增：图表配置显示控制
    const chartsField = document.getElementById('field-charts-config');
    if (type === 'data_analysis') {
        chartsField.classList.remove('hidden');
    } else {
        chartsField.classList.add('hidden');
    }
}

// 在 saveNode 函数中收集图表数据
async function saveNode(event) {
    // ... 现有代码 ...
    
    // 新增：收集图表配置
    if (data.node_type === 'data_analysis') {
        const chartCheckboxes = form.querySelectorAll('input[name="chart_type"]:checked');
        data.charts = Array.from(chartCheckboxes).map((cb, index) => ({
            chart_type: cb.value,
            sort_order: index + 1,
            config: {}
        }));
        
        // 内容顺序
        const orderSelect = form.querySelector('select[name="content_order"]');
        data.content_order = orderSelect.value.split(',');
    }
    
    // ... 现有代码 ...
}
五、Word生成服务（word_service.py）

1. 新增图表生成方法：

def _generate_chart(self, question_data: Dict[str, Any], chart_config: Dict[str, Any]) -> Optional[str]:
    """
    生成图表图片，返回临时文件路径
    """
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
    matplotlib.rcParams['axes.unicode_minus'] = False
    
    options = question_data.get('options', [])
    if not options:
        return None
    
    chart_type = chart_config.get('chart_type', 'bar')
    
    # 准备数据
    labels = [opt['text'][:15] for opt in options]  # 截短标签
    values = [int(opt['percentage'].rstrip('%')) for opt in options]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(8, 5))
    
    if chart_type == 'pie':
        colors = plt.cm.Set3(range(len(labels)))
        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors)
        ax.set_title(question_data.get('question_title', ''), fontsize=12, pad=20)
        
    elif chart_type == 'bar':
        bars = ax.bar(labels, values, color='#6366F1')
        ax.set_ylabel('占比 (%)', fontsize=10)
        ax.set_title(question_data.get('question_title', ''), fontsize=12, pad=20)
        plt.xticks(rotation=15, ha='right')
        # 在柱子上显示数值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}%', ha='center', va='bottom', fontsize=9)
                   
    elif chart_type == 'horizontal_bar':
        ax.barh(labels, values, color='#6366F1')
        ax.set_xlabel('占比 (%)', fontsize=10)
        ax.set_title(question_data.get('question_title', ''), fontsize=12, pad=20)
        for i, v in enumerate(values):
            ax.text(v + 1, i, f'{v}%', va='center', fontsize=9)
    
    plt.tight_layout()
    
    # 保存到临时文件
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    plt.savefig(temp_file.name, dpi=150, bbox_inches='tight')
    plt.close()
    
    return temp_file.name
2. 修改维度分析方法：

def _add_dimension_analysis(self, doc: Document, report_data: Dict[str, Any]):
    """添加维度分析 - 支持多图表和自定义顺序"""
    heading = doc.add_heading('四、问卷结果分析', level=1)
    self._set_heading_style(heading, Pt(16))
    
    dimensions = report_data.get('dimensions', [])
    excel_data = report_data.get('excel_data', {})
    questions_data = excel_data.get('questions', [])
    question_map = {q['question_number']: q for q in questions_data}
    
    for dim in dimensions:
        dim_heading = doc.add_heading(
            f"{dim['dimension_number']} {dim['dimension_title']}", 
            level=2
        )
        self._set_heading_style(dim_heading, Pt(14))
        
        for q_config in dim.get('questions', []):
            q_number = q_config['question_number']
            q_heading = doc.add_heading(q_config['analysis_title'], level=3)
            self._set_heading_style(q_heading, Pt(12))
            
            q_data = question_map.get(q_number)
            if not q_data:
                continue
            
            # 获取内容展示顺序
            content_order = q_config.get('content_order', ['table'])  # 默认只显示表格
            
            # 按顺序插入内容
            for content_type in content_order:
                if content_type == 'chart':
                    # 生成并插入图表
                    charts = q_config.get('charts', [])
                    for chart_item in sorted(charts, key=lambda x: x.get('sort_order', 0)):
                        chart_path = self._generate_chart(q_data, chart_item)
                        if chart_path:
                            doc.add_picture(chart_path, width=Inches(5.5))
                            doc.add_paragraph()  # 空行
                            # 清理临时文件
                            import os
                            os.unlink(chart_path)
                            
                elif content_type == 'table':
                    # 显示数据表格
                    if q_config.get('show_data_table', True):
                        self._add_question_table(doc, q_data)
                        
                elif content_type == 'interpretation':
                    # AI解读（预留）
                    if q_config.get('show_ai_interpretation', False):
                        pass  # AI解读内容通过其他方式插入
六、数据库迁移脚本

-- migration: add_chart_support.sql

-- 1. 新增charts字段（JSON类型，存储图表配置数组）
ALTER TABLE structure_nodes 
ADD COLUMN charts JSON DEFAULT '[]';

-- 2. 新增content_order字段（存储内容展示顺序）
ALTER TABLE structure_nodes 
ADD COLUMN content_order JSON DEFAULT '["table"]';

-- 3. 创建索引（如果节点数量很大）
CREATE INDEX idx_structure_nodes_charts ON structure_nodes((CAST(charts AS CHAR(255))));
七、图表类型枚举定义

# backend/app/models/schemas.py 或单独文件

CHART_TYPES = {
    "pie": {
        "name": "饼图",
        "description": "适合展示占比分布，选项≤5个时效果最佳",
        "icon": "chart-pie"
    },
    "bar": {
        "name": "柱状图",
        "description": "适合横向对比，选项≥3个时使用",
        "icon": "chart-bar"
    },
    "horizontal_bar": {
        "name": "条形图",
        "description": "适合标签较长的选项，纵向展示",
        "icon": "chart-bar horizontal"
    },
    "radar": {
        "name": "雷达图",
        "description": "适合多维度综合评价展示",
        "icon": "chart-radar"
    }
}
八、使用示例

场景1：单图表配置

{
  "node_type": "data_analysis",
  "charts": [{"chart_type": "pie", "sort_order": 1, "config": {}}],
  "content_order": ["chart", "table"]
}
效果：饼图 → 数据表格

场景2：多图表配置

{
  "charts": [
    {"chart_type": "pie", "sort_order": 1},
    {"chart_type": "bar", "sort_order": 2}
  ],
  "content_order": ["chart", "table", "interpretation"]
}
效果：饼图 → 柱状图 → 数据表格 → AI解读

场景3：不显示图表（默认行为）

{
  "charts": [],
  "content_order": ["table"]
}
效果：仅显示数据表格（与现有行为一致）

