import hashlib
import re
from typing import Dict, Any, Optional
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
            
            level = self._get_heading_level(para)
            
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

    def _get_heading_level(self, para) -> Optional[int]:
        style_name = ""
        if getattr(para, "style", None) is not None:
            style_name = getattr(para.style, "name", "") or ""

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

        try:
            p_pr = para._p.pPr
            if p_pr is not None and p_pr.outlineLvl is not None and p_pr.outlineLvl.val is not None:
                level = int(p_pr.outlineLvl.val) + 1
                if 1 <= level <= 3:
                    return level
        except Exception:
            pass

        text = (getattr(para, "text", "") or "").strip()
        if not text:
            return None
        if len(text) > 120:
            return None
        if re.search(r"[。！？.!?]$", text):
            return None

        numeric = re.match(r"^(?P<num>\d+(?:\.\d+){0,5})(?:[.、\s]|$)", text)
        if numeric:
            parts = numeric.group("num").split(".")
            inferred_level = min(len(parts), 3)
            if inferred_level == 1:
                if len(text) > 40:
                    return None
                if "：" in text or ":" in text or "；" in text or ";" in text:
                    return None
            return inferred_level

        if re.match(r"^\d+\s+", text):
            if len(text) > 40:
                return None
            if "：" in text or ":" in text or "；" in text or ";" in text:
                return None
            return 1

        if re.match(r"^[一二三四五六七八九十]+、", text):
            if len(text) > 40:
                return None
            if "：" in text or ":" in text or "；" in text or ";" in text:
                return None
            return 1
        if re.match(r"^（[一二三四五六七八九十]+）", text):
            return 2
        if re.match(r"^[（(]\d+[)）]", text):
            return 2

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
