"""
豆包(Doubao) AI 服务
使用火山引擎的Doubao-Seed-2.0-Pro模型识别文档大纲结构
"""
import httpx
import json
import asyncio
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Global client for reuse
_client: Optional[httpx.AsyncClient] = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
        _client = httpx.AsyncClient(limits=limits, timeout=120.0)
    return _client

class DoubaoService:
    """豆包AI服务 - 用于文档大纲识别"""
    
    def __init__(self):
        self.api_key = "9aa1e166-8c13-41a2-bead-0980f01bf2f8"
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self.model = "doubao-seed-2-0-pro-260215"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Semaphore to limit concurrency
        self._sem = asyncio.Semaphore(10)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout, httpx.PoolTimeout))
    )
    async def chat(self, user_content: str, temperature: float = 0.3) -> str:
        """
        调用豆包AI进行对话
        
        Args:
            user_content: 用户输入内容
            temperature: 温度参数，默认0.3以获得更确定的输出
            
        Returns:
            AI返回的文本内容
        """
        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": user_content
                        }
                    ]
                }
            ]
        }
        
        async with self._sem:
            client = get_client()
            try:
                response = await client.post(
                    f"{self.base_url}/responses",
                    headers=self.headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    if response.status_code == 429:
                        # Raise specific error for retry
                        raise httpx.ConnectError(f"Rate limited: {response.text}")
                    raise Exception(f"豆包API错误: {response.status_code} - {response.text}")
                
                result = response.json()
                
                # 解析响应
                if "output" in result and len(result["output"]) > 0:
                    for item in result["output"]:
                        if item.get("role") == "assistant" and "content" in item:
                            for content_item in item["content"]:
                                if content_item.get("type") == "output_text":
                                    return content_item.get("text", "")
                
                # 如果没有找到内容，返回原始响应
                return json.dumps(result, ensure_ascii=False)
                
            except Exception as e:
                print(f"调用豆包API失败: {e}")
                raise e
    
    async def recognize_document_structure(self, paragraphs_text: str) -> str:
        """
        识别文档结构
        
        Args:
            paragraphs_text: 文档段落文本（包含格式信息）
            
        Returns:
            JSON格式的文档结构
        """
        prompt = self._build_structure_prompt(paragraphs_text)
        return await self.chat(prompt, temperature=0.2)
    
    def _build_structure_prompt(self, paragraphs_text: str) -> str:
        """
        构建文档结构识别提示词
        """
        return f"""你作为资深的文档整理专家，具备极强的文本结构识别、标题提炼和逻辑梳理能力，现需为我分析指定文章 / 文档的1-3 级标题大纲，请严格按照以下全部规则执行，且必须按照指定 JSON 格式输出结果，无任何其他额外内容： 
 分析依据：完全基于我提供的文章 / 文档完整内容，优先参考原文目录（若有），同时结合正文实际章节逐段核对，确保大纲与原文的结构、层级、逻辑完全一致，不偏离原文核心框架； 
 层级提取：精准提取 1 级、2 级、3 级标题，严格遵循原文的层级划分；无明确三级标题的二级标题，其三级标题数组为空；无明确二级标题的一级标题，其二级标题数组为空；绝不凭空编造任何层级的标题，也不擅自删减、合并原文已有标题； 
 标题表述：严格沿用原文的标题措辞、核心关键词、标点符号及格式形式（如带编号、带括号、带序号等），不做任何改写、简化、新增或修改，保证标题与原文完全一致； 
 内容筛选：剔除原文中的费用结算表、落款信息、水印、纯数据表格、图片注释、免责申明纯条款、附件内的非标题内容、问卷原题、页码标注等非正文章节的辅助信息，仅保留文档 / 文章主体的标题结构； 
 排序要求：JSON 数组内的各级标题，严格按照其在原文中出现的先后顺序排列，不打乱原文的章节逻辑； 
 输出要求：仅输出 JSON 内容，无任何额外文字、标点、注释、说明等内容，JSON 结构严格遵循下方指定的嵌套格式，无格式错误、无冗余字段。 
 强制遵循的 JSON 输出格式 
 json 
 {{ 
   "document_outline": [ 
     {{ 
       "level1_name": "一级标题名称", 
       "level2": [ 
         {{ 
           "level2_name": "二级标题名称", 
           "level3": [ 
             {{ 
               "level3_name": "三级标题名称" 
             }} 
           ] 
         }} 
       ] 
     }} 
   ] 
 }}

【待分析的文档段落】
{paragraphs_text}

请直接返回JSON对象，不要包含任何其他文字、解释或markdown标记。"""