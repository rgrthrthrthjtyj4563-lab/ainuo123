"""
基于豆包AI的Word文档结构提取器
使用豆包Seed 2.0 Pro模型智能识别文档大纲结构
"""
import hashlib
import json
import re
from typing import List, Dict, Any, Optional
from docx import Document
from io import BytesIO
from app.services.doubao_service import DoubaoService


class AIWordStructureExtractor:
    """
    豆包AI驱动的Word文档结构提取器
    利用大模型智能识别文档大纲，支持各种复杂的文档格式
    """
    
    def __init__(self):
        self.node_id_counter = 0
        self.doubao_service = DoubaoService()
    
    async def extract(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        从Word文件提取结构
        
        Args:
            file_content: Word文件二进制内容
            filename: 文件名
            
        Returns:
            包含文件信息和提取结构的字典
        """
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        try:
            doc = Document(BytesIO(file_content))
        except Exception as e:
            raise ValueError(f"无法解析Word文件: {str(e)}")
        
        # 提取所有段落文本
        paragraphs = self._extract_paragraphs(doc)
        
        if not paragraphs:
            return {
                "file_name": filename,
                "file_hash": file_hash,
                "structure": [],
                "stats": {
                    "total_paragraphs": 0,
                    "recognized_headings": 0,
                    "by_level": {1: 0, 2: 0, 3: 0},
                    "ignored_paragraphs": 0
                }
            }
        
        # 使用AI识别大纲结构
        structure = await self._ai_recognize_structure(paragraphs)
        
        # 计算统计信息
        stats = self._calculate_stats(structure, paragraphs)
        
        return {
            "file_name": filename,
            "file_hash": file_hash,
            "structure": structure,
            "stats": stats
        }
    
    def _extract_paragraphs(self, doc) -> List[Dict[str, Any]]:
        """
        提取文档中的所有段落及其格式信息
        
        Returns:
            段落列表，每个段落包含文本和格式信息
        """
        paragraphs = []
        
        for idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue
            
            # 提取段落格式信息
            style_name = getattr(para.style, 'name', '')
            style_id = getattr(para.style, 'style_id', '')
            
            # 提取字体信息
            font_size = None
            is_bold = False
            
            if para.runs:
                for run in para.runs:
                    if run.font.size:
                        font_size = run.font.size.pt
                    if run.bold:
                        is_bold = True
            
            # 提取大纲级别
            outline_level = None
            try:
                if hasattr(para.paragraph_format, 'outline_level'):
                    outline_level = para.paragraph_format.outline_level
            except:
                pass
            
            paragraphs.append({
                "index": idx,
                "text": text,
                "style_name": style_name,
                "style_id": style_id,
                "font_size": font_size,
                "is_bold": is_bold,
                "outline_level": outline_level
            })
        
        return paragraphs
    
    async def _ai_recognize_structure(self, paragraphs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        使用豆包AI识别文档结构
        
        Args:
            paragraphs: 段落列表
            
        Returns:
            树形结构列表
        """
        # 构建段落文本（包含格式信息）
        para_texts = []
        for para in paragraphs[:80]:  # 限制最多80个段落，避免token超限
            format_info = []
            if para['style_name']:
                format_info.append(f"style:{para['style_name']}")
            if para['font_size']:
                format_info.append(f"size:{para['font_size']}pt")
            if para['is_bold']:
                format_info.append("bold")
            if para['outline_level'] is not None:
                format_info.append(f"outline:{para['outline_level']}")
            
            format_str = f" [{', '.join(format_info)}]" if format_info else ""
            para_texts.append(f"[{para['index']:03d}] {para['text']}{format_str}")
        
        paragraphs_str = '\n'.join(para_texts)
        
        try:
            # 调用豆包AI服务
            response = await self.doubao_service.recognize_document_structure(paragraphs_str)
            
            # 解析AI返回的JSON
            structure = self._parse_ai_response(response)
            
            # 验证和修复结构
            structure = self._validate_and_fix_structure(structure)
            
            # 添加节点类型和置信度
            structure = self._enrich_structure(structure)
            
            return structure
            
        except Exception as e:
            print(f"豆包AI识别失败: {e}")
            # 如果AI识别失败，返回空结构
            return []
    
    def _parse_ai_response(self, response: str) -> List[Dict[str, Any]]:
        """
        解析AI返回的响应
        
        Args:
            response: AI返回的文本
            
        Returns:
            解析后的结构列表
        """
        # 清理响应文本
        response = response.strip()
        
        # 尝试提取JSON部分
        # 1. 尝试匹配markdown代码块
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 2. 尝试直接解析整个响应
            json_str = response
            # 如果包含其他文字，尝试提取JSON数组
            if not json_str.startswith('['):
                json_match = re.search(r'(\[.*?\])', json_str, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
        
        try:
            structure = json.loads(json_str)
            if not isinstance(structure, list):
                if isinstance(structure, dict):
                    structure = [structure]
                else:
                    structure = []
            return structure
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"AI返回内容: {response[:500]}...")
            return []
    
    def _validate_and_fix_structure(self, structure: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        验证和修复结构
        
        Args:
            structure: AI返回的结构
            
        Returns:
            修复后的结构
        """
        def validate_node(node: Dict, expected_level: int = 1) -> bool:
            # 检查必需字段
            if 'level' not in node:
                node['level'] = expected_level
            if 'title' not in node or not node['title']:
                return False
            if 'children' not in node:
                node['children'] = []
            if 'numbering' not in node:
                node['numbering'] = ''
            
            # 确保level在1-3范围内
            try:
                node['level'] = max(1, min(3, int(node['level'])))
            except (ValueError, TypeError):
                node['level'] = expected_level
            
            # 确保children是列表
            if not isinstance(node['children'], list):
                node['children'] = []
            
            # 递归验证子节点
            valid_children = []
            for child in node['children']:
                if validate_node(child, node['level'] + 1):
                    valid_children.append(child)
            node['children'] = valid_children
            
            return True
        
        # 过滤无效的节点
        valid_structure = []
        for node in structure:
            if validate_node(node):
                valid_structure.append(node)
        
        return valid_structure
    
    def _enrich_structure(self, structure: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        为结构添加额外信息（节点类型、ID等）
        """
        def enrich_node(node: Dict) -> Dict:
            self.node_id_counter += 1
            
            # 确定节点类型
            node_type = self._classify_node_type(node.get('title', ''))
            
            # 添加额外字段
            node['temp_id'] = self.node_id_counter
            node['node_type'] = node_type
            node['confidence_score'] = 0.95  # AI识别的置信度较高
            node['ai_reasoning'] = "通过豆包AI模型智能识别"
            node['is_ai_generated'] = True
            node['show_data_table'] = node_type == 'data_analysis'
            node['show_ai_interpretation'] = False
            node['question_number'] = None
            node['sort_order'] = 0
            node['charts'] = []
            node['content_blocks'] = []
            node['fixed_content'] = None
            node['prompt_config_id'] = None
            
            # 递归处理子节点
            if 'children' in node and node['children']:
                node['children'] = [enrich_node(child) for child in node['children']]
            
            return node
        
        return [enrich_node(node) for node in structure]
    
    def _classify_node_type(self, title: str) -> str:
        """
        根据标题内容对节点进行分类
        """
        title_lower = title.lower()
        
        # 固定内容关键词
        fixed_keywords = ['声明', '版权', '附件', '参考文献', '致谢', '附则']
        if any(kw in title_lower for kw in fixed_keywords):
            return 'fixed_content'
        
        # AI生成章节关键词
        ai_keywords = ['前言', '背景', '摘要', '综述', '引言', '概述', '绪论', '结论', '建议', '总结', '展望', '结语']
        if any(kw in title_lower for kw in ai_keywords):
            return 'ai_chapter'
        
        # 数据分析类
        data_keywords = ['分析', '数据', '统计', '结果', '调研', '情况', '满意度', '分布', '占比', '趋势']
        if any(kw in title_lower for kw in data_keywords):
            return 'data_analysis'
        
        # 问卷题号匹配
        if re.search(r'Q\d+|第\d+题', title, re.IGNORECASE):
            return 'data_analysis'
        
        # 默认分类
        return 'container'
    
    def _calculate_stats(self, structure: List[Dict[str, Any]], paragraphs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算统计信息
        """
        def count_nodes(nodes: List[Dict], level: int = None) -> int:
            count = 0
            for node in nodes:
                if level is None or node.get('level') == level:
                    count += 1
                count += count_nodes(node.get('children', []), level)
            return count
        
        total_headings = count_nodes(structure)
        
        return {
            "total_paragraphs": len(paragraphs),
            "recognized_headings": total_headings,
            "by_level": {
                1: count_nodes(structure, 1),
                2: count_nodes(structure, 2),
                3: count_nodes(structure, 3)
            },
            "ignored_paragraphs": len(paragraphs) - total_headings
        }