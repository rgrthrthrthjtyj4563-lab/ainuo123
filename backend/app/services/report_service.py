"""
报告生成服务
"""
import os
import asyncio
import json
from sqlalchemy.orm import Session
from typing import Optional, AsyncGenerator, List
from datetime import datetime

from app.models.database import Report, DimensionTemplate, Dimension, QuestionAnalysisConfig, SessionLocal, ReportStructure, StructureNode
from app.models.schemas import ReportCreate, ReportUpdate
from app.services.structure_service import StructureService
from config import get_settings

settings = get_settings()


class ReportService:
    """报告服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_report(self, report_data: ReportCreate) -> dict:
        """创建报告"""
        db_report = Report(
            template_id=report_data.template_id,
            structure_id=report_data.structure_id,
            report_title=report_data.report_title,
            product_name=report_data.product_name,
            survey_region=report_data.survey_region,
            survey_time_range=report_data.survey_time_range,
            sample_count=report_data.sample_count,
            question_count=report_data.question_count,
            status='draft'
        )
        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)
        
        return self._report_to_dict(db_report)
    
    def list_reports(self, page: int, page_size: int, status: str = None) -> dict:
        """获取报告列表"""
        query = self.db.query(Report)
        
        if status:
            query = query.filter(Report.status == status)
        
        total = query.count()
        reports = query.order_by(Report.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "list": [self._report_to_dict(r) for r in reports]
        }
    
    def get_report(self, report_id: int) -> Optional[dict]:
        """获取报告详情"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            return None
        
        result = self._report_to_dict(report)
        
        # 获取模板维度配置
        template = self.db.query(DimensionTemplate).filter(
            DimensionTemplate.id == report.template_id
        ).first()
        
        if template:
            result['dimensions'] = []
            dimensions = self.db.query(Dimension).filter(
                Dimension.template_id == template.id
            ).order_by(Dimension.sort_order).all()
            
            for dim in dimensions:
                dim_dict = {
                    "dimension_number": dim.dimension_number,
                    "dimension_title": dim.dimension_title,
                    "questions": []
                }
                
                questions = self.db.query(QuestionAnalysisConfig).filter(
                    QuestionAnalysisConfig.dimension_id == dim.id
                ).order_by(QuestionAnalysisConfig.sort_order).all()
                
                for q in questions:
                    q_dict = {
                        "question_number": q.question_number,
                        "analysis_title": q.analysis_title
                    }
                    dim_dict['questions'].append(q_dict)
                
                result['dimensions'].append(dim_dict)
        
        # 解析generated_content
        if report.generated_content:
            result['generated_content'] = report.generated_content
        
        return result
    
    def update_report(self, report_id: int, report_data: ReportUpdate) -> Optional[dict]:
        """更新报告"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            return None
        
        if report_data.report_title is not None:
            report.report_title = report_data.report_title
        if report_data.product_name is not None:
            report.product_name = report_data.product_name
        if report_data.survey_region is not None:
            report.survey_region = report_data.survey_region
        if report_data.survey_time_range is not None:
            report.survey_time_range = report_data.survey_time_range
        if report_data.sample_count is not None:
            report.sample_count = report_data.sample_count
        if report_data.question_count is not None:
            report.question_count = report_data.question_count
        
        self.db.commit()
        self.db.refresh(report)
        
        return self._report_to_dict(report)
    
    def update_excel_data(self, report_id: int, excel_data: dict) -> Optional[dict]:
        """更新Excel数据"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            return None
        
        report.excel_data = excel_data
        self.db.commit()
        self.db.refresh(report)
        
        return self._report_to_dict(report)
    
    def start_generation(self, report_id: int, workflow_id: str = None) -> Optional[dict]:
        """开始生成报告"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            return None
        
        report.status = 'generating'
        self.db.commit()
        
        # TODO: 启动异步任务调用扣子API
        # 这里先模拟异步生成
        asyncio.create_task(self._generate_report_async(report_id))
        
        return {
            "report_id": report_id,
            "status": "generating",
            "progress": 0
        }
    
    async def _generate_report_async(self, report_id: int):
        """异步生成报告"""
        from app.services.coze_service import CozeService
        
        # 使用独立的 Session
        db = SessionLocal()
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                return

            coze_service = CozeService()
            
            if report.structure_id:
                await self._generate_report_structure(db, report, coze_service)
            else:
                await self._generate_report_legacy(db, report, coze_service)
                
        except Exception as e:
            print(f"Error generating report: {e}")
            import traceback
            traceback.print_exc()
            try:
                report = db.query(Report).filter(Report.id == report_id).first()
                if report:
                    report.status = 'failed'
                    report.error_message = str(e)
                    db.commit()
            except:
                pass
        finally:
            db.close()

    async def _generate_report_structure(self, db: Session, report: Report, coze_service):
        """基于新结构的报告生成"""
        service = StructureService(db)
        nodes = service.get_structure_nodes(report.structure_id)
        
        generated_data = await self._process_nodes(nodes, report, coze_service)
        
        report.generated_content = {"nodes": generated_data, "structure_version": "v2"}
        report.status = 'completed'
        db.commit()
        print(f"Report {report.id} generated successfully using structure {report.structure_id}")

    async def _process_nodes(self, nodes: List[StructureNode], report: Report, coze_service):
        results = []
        for node in nodes:
            item = {
                "id": node.id,
                "title": node.title,
                "type": node.node_type,
                "level": node.level,
                "content": "",
                "children": [],
                "data": None
            }
            
            # 优化：所有节点都支持关联数据和图表
            if node.question_number:
                q_data = self._get_excel_data_by_number(report.excel_data, node.question_number)
                item["data"] = q_data
                
                # 传递配置信息
                item["charts"] = node.charts
                item["show_data_table"] = node.show_data_table
                item["show_ai_interpretation"] = node.show_ai_interpretation
            
            # Recursively process children
            if node.children:
                item["children"] = await self._process_nodes(node.children, report, coze_service)
            
            # Generate content based on type
            if node.node_type == 'ai_chapter':
                system_prompt = "你是一个专业的医药调研分析师。请撰写一段专业的分析报告，风格客观、严谨。"
                user_prompt = f"请撰写关于 {report.product_name} 在 {report.survey_region} 的 {node.title} 章节。"
                
                # 如果关联了数据，将数据提供给AI
                if item.get("data"):
                    user_prompt += f"\n\n参考数据：{json.dumps(item['data'], ensure_ascii=False, indent=2)}\n"
                    user_prompt += "请结合上述数据进行分析。"
                
                try:
                    item["content"] = await coze_service.chat(system_prompt=system_prompt, user_prompt=user_prompt)
                except Exception as e:
                    item["content"] = f"生成失败: {str(e)}"
            
            elif node.node_type == 'fixed_content':
                item["content"] = node.fixed_content
            
            elif node.node_type == 'data_analysis':
                # 即使已经在上面处理了通用数据，这里仍保留特定的逻辑（如AI解读）
                if node.question_number and node.show_ai_interpretation:
                    system_prompt = "你是一个专业的医药调研分析师。请根据提供的数据，撰写一段专业的分析报告。"
                    user_prompt = f"分析主题：{node.title}\n"
                    if item.get("data"):
                        user_prompt += f"数据：{json.dumps(item['data'], ensure_ascii=False, indent=2)}\n"
                        user_prompt += "请对以上数据进行深入分析，指出关键趋势和洞察。"
                    else:
                        user_prompt += f"注意：未找到第 {node.question_number} 题的数据。\n请提供一般性的分析框架。"
                    
                    try:
                        item["content"] = await coze_service.chat(system_prompt=system_prompt, user_prompt=user_prompt)
                    except Exception as e:
                        item["content"] = f"生成失败: {str(e)}"
            
            results.append(item)
        return results

    def _get_excel_data_by_number(self, excel_data, question_number):
        if not excel_data or not isinstance(excel_data, dict):
            return None
            
        keys_to_try = [
            str(question_number),
            f"Q{question_number}",
            f"q{question_number}",
            f"第{question_number}题"
        ]
        
        for k in keys_to_try:
            if k in excel_data:
                return excel_data[k]
        return None

    async def _generate_report_legacy(self, db: Session, report: Report, coze_service):
        """异步生成报告 - 旧版逻辑"""
        # 1. 获取模板维度配置
        template = db.query(DimensionTemplate).filter(
            DimensionTemplate.id == report.template_id
        ).first()
        
        if not template:
            report.status = 'failed'
            report.error_message = "模板不存在"
            db.commit()
            return
        
        # 初始化生成内容
        generated_data = {
            "preface": f"关于 {report.product_name} 在 {report.survey_region} 的调研报告",
            "dimensions": []
        }
        
        # 2. 遍历维度
        dimensions = db.query(Dimension).filter(
            Dimension.template_id == template.id
        ).order_by(Dimension.sort_order).all()
        
        for dim in dimensions:
            dim_data = {
                "dimension_number": dim.dimension_number,
                "dimension_title": dim.dimension_title,
                "questions": []
            }
            
            # 获取该维度下的题目配置
            questions = db.query(QuestionAnalysisConfig).filter(
                QuestionAnalysisConfig.dimension_id == dim.id
            ).order_by(QuestionAnalysisConfig.sort_order).all()
            
            for q in questions:
                # 3. 根据配置的题号映射从Excel数据中获取原始数据
                q_data = None
                excel_question_key = None
                
                if report.excel_data and isinstance(report.excel_data, dict):
                    q_data = self._get_excel_data_by_number(report.excel_data, q.question_number)
                    if q_data:
                        # find key for logging
                        # logic duplicated from _get_excel_data_by_number but that returns value
                        pass

                # 4. 构建 Prompt
                system_prompt = "你是一个专业的医药调研分析师。\n请根据提供的维度信息、分析标题和Excel原始数据，撰写一段专业的分析报告。"
                
                user_prompt = f"""维度信息：
- 维度编号：{dim.dimension_number}
- 维度名称：{dim.dimension_title}
- 分析标题：{q.analysis_title}
- 关联题号：Q{q.question_number}

"""
                
                if q_data:
                    user_prompt += f"原始数据（Excel第{q.question_number}题）：\n{json.dumps(q_data, ensure_ascii=False, indent=2)}\n\n"
                    user_prompt += f"请基于以上数据，撰写一段关于「{q.analysis_title}」的专业分析："
                else:
                    user_prompt += f"【注意】未在Excel数据中找到第{q.question_number}题的数据。\n"
                    user_prompt += f"请根据「{q.analysis_title}」这个主题进行一般性分析框架说明。"
                
                # 5. 调用 Coze API
                content = "生成中..."
                try:
                    content = await coze_service.chat(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt
                    )
                except Exception as e:
                    content = f"生成失败: {str(e)}"
                    print(f"Coze API error: {e}")

                dim_data["questions"].append({
                    "question_number": q.question_number,
                    "analysis_title": q.analysis_title,
                    "content": content
                })
            
            generated_data["dimensions"].append(dim_data)
        
        # 7. 更新报告
        report.generated_content = generated_data
        report.status = 'completed'
        db.commit()
        print(f"Report {report.id} generated successfully (legacy)")
    
    async def get_generation_progress(self, report_id: int) -> AsyncGenerator[dict, None]:
        """获取生成进度（SSE）"""
        sections = ['preface', 'background', 'project_info', 'conclusion', 'suggestions']
        
        for i, section in enumerate(sections):
            progress = (i + 1) * 20
            
            yield {
                "event": "progress",
                "data": {
                    "section": section,
                    "progress": progress,
                    "status": "processing"
                }
            }
            
            await asyncio.sleep(0.5)
        
        yield {
            "event": "complete",
            "data": {
                "progress": 100,
                "status": "completed"
            }
        }
    
    def export_word(self, report_id: int) -> Optional[str]:
        """导出Word报告"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        
        if not report or report.status != 'completed':
            return None
        
        # TODO: 调用Word生成服务
        # 这里返回模拟的文件路径
        return report.word_file_path
    
    def delete_report(self, report_id: int) -> bool:
        """删除报告"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            return False
        
        # 删除关联的文件
        if report.word_file_path and os.path.exists(report.word_file_path):
            os.remove(report.word_file_path)
        
        self.db.delete(report)
        self.db.commit()
        
        return True
    
    def _report_to_dict(self, report: Report) -> dict:
        """报告转字典"""
        return {
            "id": report.id,
            "template_id": report.template_id,
            "structure_id": report.structure_id,
            "report_title": report.report_title,
            "product_name": report.product_name,
            "survey_region": report.survey_region,
            "survey_time_range": report.survey_time_range,
            "sample_count": report.sample_count,
            "question_count": report.question_count,
            "status": report.status,
            "error_message": report.error_message,
            "word_file_path": report.word_file_path,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "updated_at": report.updated_at.isoformat() if report.updated_at else None
        }
