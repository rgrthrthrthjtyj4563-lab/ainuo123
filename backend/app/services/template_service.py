"""
模板管理服务
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.models.database import DimensionTemplate, Dimension, QuestionAnalysisConfig
from app.models.schemas import (
    TemplateCreate, TemplateUpdate, DimensionCreate, 
    DimensionUpdate, QuestionCreate, QuestionUpdate
)


class TemplateService:
    """维度模板服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_template(self, template_data: TemplateCreate) -> dict:
        """创建模板"""
        # 创建模板
        db_template = DimensionTemplate(
            template_name=template_data.template_name,
            report_type=template_data.report_type,
            description=template_data.description
        )
        self.db.add(db_template)
        self.db.flush()
        
        # 创建维度
        for dim_data in template_data.dimensions:
            db_dimension = Dimension(
                template_id=db_template.id,
                dimension_number=dim_data.dimension_number,
                dimension_title=dim_data.dimension_title,
                sort_order=dim_data.sort_order
            )
            self.db.add(db_dimension)
            self.db.flush()
            
            # 创建问题
            for q_data in dim_data.questions:
                db_question = QuestionAnalysisConfig(
                    dimension_id=db_dimension.id,
                    question_number=q_data.question_number,
                    analysis_title=q_data.analysis_title,
                    sort_order=q_data.sort_order
                )
                self.db.add(db_question)
        
        self.db.commit()
        self.db.refresh(db_template)
        
        return self._template_to_dict(db_template)
    
    def list_templates(self, page: int, page_size: int, report_type: str = None) -> dict:
        """获取模板列表"""
        query = self.db.query(DimensionTemplate)
        
        if report_type:
            query = query.filter(DimensionTemplate.report_type == report_type)
        
        total = query.count()
        templates = query.offset((page - 1) * page_size).limit(page_size).all()
        
        # 获取每个模板的维度数量
        result = []
        for template in templates:
            dim_count = self.db.query(func.count(Dimension.id)).filter(
                Dimension.template_id == template.id
            ).scalar()
            
            template_dict = self._template_to_dict(template)
            template_dict['dimension_count'] = dim_count
            result.append(template_dict)
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "list": result
        }
    
    def get_template(self, template_id: int) -> Optional[dict]:
        """获取模板详情"""
        template = self.db.query(DimensionTemplate).filter(
            DimensionTemplate.id == template_id
        ).first()
        
        if not template:
            return None
        
        result = self._template_to_dict(template)
        
        # 获取维度列表
        dimensions = self.db.query(Dimension).filter(
            Dimension.template_id == template_id
        ).order_by(Dimension.sort_order).all()
        
        result['dimensions'] = []
        for dim in dimensions:
            dim_dict = self._dimension_to_dict(dim)
            
            # 获取问题列表
            questions = self.db.query(QuestionAnalysisConfig).filter(
                QuestionAnalysisConfig.dimension_id == dim.id
            ).order_by(QuestionAnalysisConfig.sort_order).all()
            
            dim_dict['questions'] = [self._question_to_dict(q) for q in questions]
            result['dimensions'].append(dim_dict)
        
        return result
    
    def update_template(self, template_id: int, template_data: TemplateUpdate) -> Optional[dict]:
        """更新模板"""
        template = self.db.query(DimensionTemplate).filter(
            DimensionTemplate.id == template_id
        ).first()
        
        if not template:
            return None
        
        if template_data.template_name is not None:
            template.template_name = template_data.template_name
        if template_data.description is not None:
            template.description = template_data.description
        if template_data.is_active is not None:
            template.is_active = template_data.is_active
        
        self.db.commit()
        self.db.refresh(template)
        
        return self._template_to_dict(template)
    
    def delete_template(self, template_id: int) -> bool:
        """删除模板"""
        template = self.db.query(DimensionTemplate).filter(
            DimensionTemplate.id == template_id
        ).first()
        
        if not template:
            return False
        
        self.db.delete(template)
        self.db.commit()
        
        return True
    
    def create_dimension(self, template_id: int, dimension_data: DimensionCreate) -> Optional[dict]:
        """添加维度"""
        template = self.db.query(DimensionTemplate).filter(
            DimensionTemplate.id == template_id
        ).first()
        
        if not template:
            return None
        
        # 创建维度
        db_dimension = Dimension(
            template_id=template_id,
            dimension_number=dimension_data.dimension_number,
            dimension_title=dimension_data.dimension_title,
            sort_order=dimension_data.sort_order
        )
        self.db.add(db_dimension)
        self.db.commit()
        self.db.refresh(db_dimension)

        if dimension_data.question_number is not None and dimension_data.analysis_title is not None:
            new_question = QuestionAnalysisConfig(
                dimension_id=db_dimension.id,
                question_number=dimension_data.question_number,
                analysis_title=dimension_data.analysis_title,
                sort_order=0
            )
            self.db.add(new_question)
            self.db.commit()

        result = self._dimension_to_dict(db_dimension)
        questions = self.db.query(QuestionAnalysisConfig).filter(
            QuestionAnalysisConfig.dimension_id == db_dimension.id
        ).order_by(QuestionAnalysisConfig.sort_order).all()
        result['questions'] = [self._question_to_dict(q) for q in questions]
        return result
    
    def update_dimension(self, dimension_id: int, dimension_data: DimensionUpdate) -> Optional[dict]:
        """更新维度（包含关联题目）"""
        dimension = self.db.query(Dimension).filter(
            Dimension.id == dimension_id
        ).first()
        
        if not dimension:
            return None
        
        # 更新维度基本信息
        if dimension_data.dimension_number is not None:
            dimension.dimension_number = dimension_data.dimension_number
        if dimension_data.dimension_title is not None:
            dimension.dimension_title = dimension_data.dimension_title
        if dimension_data.sort_order is not None:
            dimension.sort_order = dimension_data.sort_order
        
        # 更新或创建关联题目
        if dimension_data.question_number is not None and dimension_data.analysis_title is not None:
            # 查找是否已有题目
            existing_question = self.db.query(QuestionAnalysisConfig).filter(
                QuestionAnalysisConfig.dimension_id == dimension_id
            ).first()
            
            if existing_question:
                # 更新现有题目
                existing_question.question_number = dimension_data.question_number
                existing_question.analysis_title = dimension_data.analysis_title
            else:
                # 创建新题目
                new_question = QuestionAnalysisConfig(
                    dimension_id=dimension_id,
                    question_number=dimension_data.question_number,
                    analysis_title=dimension_data.analysis_title,
                    sort_order=0
                )
                self.db.add(new_question)
        
        self.db.commit()
        self.db.refresh(dimension)
        
        result = self._dimension_to_dict(dimension)
        
        # 查询并返回关联的题目
        questions = self.db.query(QuestionAnalysisConfig).filter(
            QuestionAnalysisConfig.dimension_id == dimension.id
        ).order_by(QuestionAnalysisConfig.sort_order).all()
        result['questions'] = [self._question_to_dict(q) for q in questions]
        
        return result
    
    def delete_dimension(self, dimension_id: int) -> bool:
        """删除维度"""
        dimension = self.db.query(Dimension).filter(
            Dimension.id == dimension_id
        ).first()
        
        if not dimension:
            return False
        
        self.db.delete(dimension)
        self.db.commit()
        
        return True
    
    def create_question(self, dimension_id: int, question_data: QuestionCreate) -> Optional[dict]:
        """添加问题"""
        dimension = self.db.query(Dimension).filter(
            Dimension.id == dimension_id
        ).first()
        
        if not dimension:
            return None
        
        db_question = QuestionAnalysisConfig(
            dimension_id=dimension_id,
            question_number=question_data.question_number,
            analysis_title=question_data.analysis_title,
            sort_order=question_data.sort_order
        )
        self.db.add(db_question)
        self.db.commit()
        self.db.refresh(db_question)
        
        return self._question_to_dict(db_question)
    
    def update_question(self, question_id: int, question_data: QuestionUpdate) -> Optional[dict]:
        """更新问题"""
        question = self.db.query(QuestionAnalysisConfig).filter(
            QuestionAnalysisConfig.id == question_id
        ).first()
        
        if not question:
            return None
        
        if question_data.question_number is not None:
            question.question_number = question_data.question_number
        if question_data.analysis_title is not None:
            question.analysis_title = question_data.analysis_title
        if question_data.sort_order is not None:
            question.sort_order = question_data.sort_order
        
        self.db.commit()
        self.db.refresh(question)
        
        return self._question_to_dict(question)
    
    def delete_question(self, question_id: int) -> bool:
        """删除问题"""
        question = self.db.query(QuestionAnalysisConfig).filter(
            QuestionAnalysisConfig.id == question_id
        ).first()
        
        if not question:
            return False
        
        self.db.delete(question)
        self.db.commit()
        
        return True
    
    def list_dimensions(self, template_id: int) -> List[dict]:
        """获取模板下的所有维度"""
        dimensions = self.db.query(Dimension).filter(
            Dimension.template_id == template_id
        ).order_by(Dimension.sort_order).all()
        
        result = []
        for dim in dimensions:
            dim_dict = self._dimension_to_dict(dim)
            
            # 获取问题列表
            questions = self.db.query(QuestionAnalysisConfig).filter(
                QuestionAnalysisConfig.dimension_id == dim.id
            ).order_by(QuestionAnalysisConfig.sort_order).all()
            
            dim_dict['questions'] = [self._question_to_dict(q) for q in questions]
            result.append(dim_dict)
        
        return result

    def _template_to_dict(self, template: DimensionTemplate) -> dict:
        """模板转字典"""
        return {
            "id": template.id,
            "template_name": template.template_name,
            "report_type": template.report_type,
            "description": template.description,
            "is_active": template.is_active,
            "created_at": template.created_at.isoformat() if template.created_at else None,
            "updated_at": template.updated_at.isoformat() if template.updated_at else None
        }
    
    def _dimension_to_dict(self, dimension: Dimension) -> dict:
        """维度转字典"""
        return {
            "id": dimension.id,
            "template_id": dimension.template_id,
            "dimension_number": dimension.dimension_number,
            "dimension_title": dimension.dimension_title,
            "sort_order": dimension.sort_order,
            "created_at": dimension.created_at.isoformat() if dimension.created_at else None
        }
    
    def _question_to_dict(self, question: QuestionAnalysisConfig) -> dict:
        """问题转字典"""
        return {
            "id": question.id,
            "dimension_id": question.dimension_id,
            "question_number": question.question_number,
            "analysis_title": question.analysis_title,
            "sort_order": question.sort_order,
            "created_at": question.created_at.isoformat() if question.created_at else None
        }
