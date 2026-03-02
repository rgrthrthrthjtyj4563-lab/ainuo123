"""
扣子(Coze) API服务
"""
import httpx
import json
from typing import Dict, Any, Optional, AsyncGenerator
from config import get_settings

settings = get_settings()


class CozeService:
    """扣子API服务"""
    
    def __init__(self):
        self.api_key = settings.COZE_API_KEY
        self.base_url = settings.COZE_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        通用对话接口
        """
        payload = {
            "model": "coze",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "stream": False
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Coze API error: {response.text}")
                
                result = response.json()
                return result['choices'][0]['message']['content']
            except Exception as e:
                print(f"Call Coze API failed: {e}")
                # Fallback for dev/test if API fails
                return f"（模拟生成内容）针对该问题的分析：\n基于提供的数据，我们可以看到..."

    async def generate_section(
        self, 
        section_type: str,
        report_data: Dict[str, Any],
        template_data: Dict[str, Any],
        prompt_config: Dict[str, str]
    ) -> str:
        """
        生成单个章节内容
        
        Args:
            section_type: 章节类型 (preface, background, project_info, conclusion, suggestions)
            report_data: 报告基本信息
            template_data: 模板维度数据
            prompt_config: 提示词配置
        
        Returns:
            生成的文本内容
        """
        # 构建提示词
        system_prompt = prompt_config.get('system_prompt', '')
        user_prompt = self._build_user_prompt(
            prompt_config.get('user_prompt_template', ''),
            report_data,
            template_data
        )
        
        # 构建请求体
        payload = {
            "model": "coze",  # 根据实际模型调整
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": float(prompt_config.get('temperature', 0.7)),
            "stream": False
        }
        
        # 发送请求
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Coze API error: {response.text}")
            
            result = response.json()
            return result['choices'][0]['message']['content']
    
    async def generate_section_stream(
        self,
        section_type: str,
        report_data: Dict[str, Any],
        template_data: Dict[str, Any],
        prompt_config: Dict[str, str]
    ) -> AsyncGenerator[str, None]:
        """
        流式生成单个章节内容
        """
        system_prompt = prompt_config.get('system_prompt', '')
        user_prompt = self._build_user_prompt(
            prompt_config.get('user_prompt_template', ''),
            report_data,
            template_data
        )
        
        payload = {
            "model": "coze",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": float(prompt_config.get('temperature', 0.7)),
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60.0
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk['choices'][0]['delta'].get('content', '')
                            if content:
                                yield content
                        except:
                            pass
    
    async def generate_full_report(
        self,
        report_data: Dict[str, Any],
        template_data: Dict[str, Any],
        prompt_configs: Dict[str, Dict[str, str]]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        生成完整报告，流式返回进度
        
        Yields:
            {'section': str, 'content': str, 'progress': int, 'status': str}
        """
        sections = ['preface', 'background', 'project_info', 'conclusion', 'suggestions']
        
        for i, section_type in enumerate(sections):
            progress = int((i / len(sections)) * 100)
            
            # 发送进度
            yield {
                'section': section_type,
                'content': '',
                'progress': progress,
                'status': 'processing'
            }
            
            # 获取提示词配置
            prompt_config = prompt_configs.get(section_type, {})
            
            try:
                # 生成章节内容
                content = await self.generate_section(
                    section_type,
                    report_data,
                    template_data,
                    prompt_config
                )
                
                yield {
                    'section': section_type,
                    'content': content,
                    'progress': int(((i + 1) / len(sections)) * 100),
                    'status': 'completed'
                }
                
            except Exception as e:
                yield {
                    'section': section_type,
                    'content': '',
                    'progress': progress,
                    'status': 'failed',
                    'error': str(e)
                }
                return
        
        # 完成
        yield {
            'section': 'complete',
            'content': '',
            'progress': 100,
            'status': 'completed'
        }
    
    def _build_user_prompt(
        self, 
        template: str, 
        report_data: Dict[str, Any],
        template_data: Dict[str, Any]
    ) -> str:
        """构建用户提示词 - 支持维度映射关系"""
        prompt = template
        
        # 替换基本变量
        replacements = {
            '{{product_name}}': report_data.get('product_name', ''),
            '{{survey_region}}': report_data.get('survey_region', ''),
            '{{survey_time_range}}': report_data.get('survey_time_range', ''),
            '{{sample_count}}': str(report_data.get('sample_count', 0)),
            '{{question_count}}': str(report_data.get('question_count', 0)),
        }
        
        for key, value in replacements.items():
            prompt = prompt.replace(key, value)
        
        # 【关键修复】构建包含维度映射关系的数据文本
        dimensions_text = self._build_dimensions_text(template_data.get('dimensions', []))
        prompt = prompt.replace('{{dimensions_data}}', dimensions_text)
        
        # 构建关键发现
        key_findings = self._build_key_findings(template_data.get('dimensions', []))
        prompt = prompt.replace('{{key_findings}}', key_findings)
        
        # 【新增】构建维度映射表，便于报告模板替换
        dimension_mapping = self._build_dimension_mapping(template_data.get('dimensions', []))
        prompt = prompt.replace('{{dimension_mapping}}', dimension_mapping)
        
        return prompt
    
    def _build_dimensions_text(self, dimensions: list) -> str:
        """构建维度数据文本"""
        text_parts = []
        
        for dim in dimensions:
            dim_text = f"{dim.get('dimension_title', '')}:\n"
            
            for q in dim.get('questions', []):
                options = q.get('options', [])
                if options:
                    max_opt = max(options, key=lambda x: x.get('count', 0))
                    dim_text += f"- {q.get('question_title', '')}: 最高占比 {max_opt.get('percentage', '0%')}\n"
            
            text_parts.append(dim_text)
        
        return '\n'.join(text_parts)
    
    def _build_key_findings(self, dimensions: list) -> str:
        """构建关键发现文本"""
        text_parts = []

        for dim in dimensions:
            dim_text = f"{dim.get('dimension_title', '')}关键数据：\n"

            for q in dim.get('questions', []):
                options = q.get('options', [])
                if options:
                    max_opt = max(options, key=lambda x: x.get('count', 0))
                    dim_text += f"- {q.get('question_title', '')}: {max_opt.get('text', '')} ({max_opt.get('percentage', '0%')})\n"

            text_parts.append(dim_text)

        return '\n'.join(text_parts)

    def _build_dimension_mapping(self, dimensions: list) -> str:
        """构建维度映射表文本 - 用于动态替换报告字段

        格式：
        维度编号 | 维度名称 | 关联题号 | 分析标题
        4.1 | 用药基础信息 | Q1 | 目前正在服用的药物
        """
        text_parts = ["维度映射表："]
        text_parts.append("维度编号 | 维度名称 | 关联题号 | 分析标题")
        text_parts.append("-" * 50)

        for dim in dimensions:
            dim_number = dim.get('dimension_number', '')
            dim_title = dim.get('dimension_title', '')

            questions = dim.get('questions', [])
            if questions:
                for q in questions:
                    q_number = q.get('question_number', '')
                    q_title = q.get('analysis_title', '')
                    text_parts.append(f"{dim_number} | {dim_title} | Q{q_number} | {q_title}")
            else:
                text_parts.append(f"{dim_number} | {dim_title} | - | -")

        return '\n'.join(text_parts)
