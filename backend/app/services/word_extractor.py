import hashlib
import re
from typing import List, Dict, Any, Optional
from docx import Document
from io import BytesIO

class WordStructureExtractor:
    def __init__(self):
        self.node_id_counter = 0

    def extract(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract structure from a Word file content.
        Returns a dict containing file info and the extracted structure tree.
        """
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        try:
            doc = Document(BytesIO(file_content))
        except Exception as e:
            raise ValueError(f"无法解析Word文件: {str(e)}")

        nodes = []
        stack = []  # Stack of (node, level)

        for para in doc.paragraphs:
            if not para.text.strip():
                continue
            
            style_name = para.style.name
            level = self._get_heading_level(style_name)
            
            if level is not None:
                node = self._create_node(para.text.strip(), level)
                
                # Find parent
                while stack and stack[-1]['level'] >= level:
                    stack.pop()
                
                if stack:
                    parent = stack[-1]['node']
                    parent['children'].append(node)
                    # Parent is likely a container if it has children
                    if parent['node_type'] == 'ai_chapter': 
                         # If previously guessed AI chapter but now has children, maybe it's a container?
                         # Or maybe it's a chapter with sub-sections.
                         # Let's keep it simple for now.
                         pass
                else:
                    nodes.append(node)
                
                stack.append({'node': node, 'level': level})

        return {
            "file_name": filename,
            "file_hash": file_hash,
            "structure": nodes
        }

    def _get_heading_level(self, style_name: str) -> Optional[int]:
        """Map style name to level (1, 2, 3). Returns None if not a heading."""
        match = re.search(r'Heading\s*(\d)', style_name, re.IGNORECASE)
        if match:
            level = int(match.group(1))
            if 1 <= level <= 3:
                return level
        # Chinese Word might use "标题 1"
        match_cn = re.search(r'标题\s*(\d)', style_name)
        if match_cn:
            level = int(match_cn.group(1))
            if 1 <= level <= 3:
                return level
        return None

    def _create_node(self, title: str, level: int) -> Dict[str, Any]:
        """Create a node dict with AI classification."""
        node_type, confidence, reason = self._classify_node(title)
        
        self.node_id_counter += 1
        return {
            "temp_id": self.node_id_counter, # Temporary ID for frontend
            "title": title,
            "level": level,
            "node_type": node_type,
            "confidence_score": confidence,
            "ai_reasoning": reason,
            "is_ai_generated": True,
            "children": [],
            "show_data_table": True if node_type == 'data_analysis' else False,
            "show_ai_interpretation": False
        }

    def _classify_node(self, title: str) -> (str, float, str):
        """
        Classify node type based on title keywords.
        Returns (node_type, confidence, reasoning)
        """
        title_lower = title.lower()
        
        # Rule 1: Fixed Content
        if any(kw in title_lower for kw in ['声明', '版权', '附件', '参考文献', '致谢']):
            return 'fixed_content', 0.9, "标题包含固定内容关键词"
            
        # Rule 2: AI Chapter (Introduction, Conclusion, etc.)
        if any(kw in title_lower for kw in ['前言', '背景', '摘要', '综述', '结论', '建议', '总结']):
            return 'ai_chapter', 0.85, "标题包含AI生成章节关键词"
            
        # Rule 3: Data Analysis
        if any(kw in title_lower for kw in ['分析', '数据', '统计', '结果', '调研', '情况', '满意度']):
            return 'data_analysis', 0.8, "标题包含数据分析关键词"
            
        # Rule 4: Question matching (e.g., "Q1", "第1题")
        if re.search(r'Q\d+|第\d+题', title, re.IGNORECASE):
            return 'data_analysis', 0.9, "标题包含明确题号标识"

        # Default fallback
        return 'container', 0.5, "未匹配到特定规则，默认为容器/通用章节"
