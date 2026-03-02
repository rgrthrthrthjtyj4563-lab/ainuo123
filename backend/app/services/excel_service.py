"""
Excel解析服务
"""
import pandas as pd
from fastapi import UploadFile
from typing import Dict, List, Any
import io


class ExcelService:
    """Excel解析服务"""
    
    async def parse_excel(self, file: UploadFile) -> Dict[str, Any]:
        """
        解析Excel文件
        期望格式：
        - 第一行：题号
        - 第二行：问题标题
        - 第三行及以后：选项数据（选项字母、选项文本、样本量、占比）
        """
        # 读取文件内容
        content = await file.read()
        
        # 使用pandas读取Excel
        df = pd.read_excel(io.BytesIO(content), header=None)
        
        # 解析数据结构
        parsed_data = self._parse_dataframe(df)
        
        return parsed_data
    
    def _parse_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """解析DataFrame"""
        questions = []
        
        # 获取题号行（第一行）
        question_numbers = df.iloc[0].tolist()
        
        # 获取问题标题行（第二行）
        question_titles = df.iloc[1].tolist()
        
        # 解析每个问题
        col_idx = 0
        while col_idx < len(df.columns):
            # 跳过空列
            if pd.isna(question_numbers[col_idx]):
                col_idx += 1
                continue
            
            # 获取题号
            q_number = self._extract_question_number(str(question_numbers[col_idx]))
            if q_number is None:
                col_idx += 1
                continue
            
            # 获取问题标题
            q_title = str(question_titles[col_idx]) if col_idx < len(question_titles) and not pd.isna(question_titles[col_idx]) else ""
            
            # 获取选项数据（从第3行开始）
            options = []
            for row_idx in range(2, len(df)):
                row_data = df.iloc[row_idx]
                
                # 检查是否是选项行
                if col_idx < len(row_data) and not pd.isna(row_data[col_idx]):
                    option_key = str(row_data[col_idx]).strip()
                    
                    # 选项文本
                    option_text = ""
                    if col_idx + 1 < len(row_data) and not pd.isna(row_data[col_idx + 1]):
                        option_text = str(row_data[col_idx + 1]).strip()
                    
                    # 样本量
                    count = 0
                    if col_idx + 2 < len(row_data) and not pd.isna(row_data[col_idx + 2]):
                        try:
                            count = int(float(row_data[col_idx + 2]))
                        except:
                            pass
                    
                    # 占比
                    percentage = "0%"
                    if col_idx + 3 < len(row_data) and not pd.isna(row_data[col_idx + 3]):
                        try:
                            pct_val = float(row_data[col_idx + 3])
                            percentage = f"{pct_val:.0f}%"
                        except:
                            percentage = str(row_data[col_idx + 3])
                    
                    options.append({
                        "key": option_key,
                        "text": option_text,
                        "count": count,
                        "percentage": percentage
                    })
            
            if options:
                questions.append({
                    "question_number": q_number,
                    "question_title": q_title,
                    "options": options
                })
            
            # 每个问题占4列（选项字母、文本、样本量、占比）
            col_idx += 4
        
        return {
            "question_count": len(questions),
            "questions": questions,
            "dimensions": []  # 维度分组在后续处理
        }
    
    def _extract_question_number(self, text: str) -> int:
        """从文本中提取题号"""
        import re
        # 匹配数字
        match = re.search(r'(\d+)', str(text))
        if match:
            return int(match.group(1))
        return None
