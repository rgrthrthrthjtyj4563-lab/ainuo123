from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update
from app.models.database import OutlineChapter, DimensionTemplate, Dimension
from app.models.schemas import OutlineChapterCreate, OutlineChapterUpdate, OutlineReorderRequest
from fastapi import HTTPException

class OutlineService:
    def __init__(self, db: Session):
        self.db = db

    def get_outline(self, template_id: int):
        # 获取所有一级章节，ORM 会自动加载 children 并排序
        stmt = select(OutlineChapter).where(
            OutlineChapter.template_id == template_id,
            OutlineChapter.parent_id == None
        ).order_by(OutlineChapter.sort_order)
        
        chapters = self.db.execute(stmt).scalars().all()
        
        # 如果没有章节，自动创建默认大纲
        if not chapters:
            return self.create_default_outline(template_id)
            
        return chapters

    def create_default_outline(self, template_id: int):
        # 检查是否已存在大纲
        # existing = self.get_outline(template_id) # 避免递归
        stmt = select(OutlineChapter).where(OutlineChapter.template_id == template_id).limit(1)
        existing = self.db.execute(stmt).scalar_one_or_none()
        
        if existing:
            # 如果存在部分章节，应该重置吗？这里假设只在完全为空时创建
            return self.get_outline(template_id)

        # 默认大纲配置
        default_chapters = [
            {"chapter_type": "preface", "chapter_title": "前言", "sort_order": 1, "level": 1},
            {"chapter_type": "background", "chapter_title": "项目背景", "sort_order": 2, "level": 1},
            {"chapter_type": "project_info", "chapter_title": "项目开展情况", "sort_order": 3, "level": 1},
            {"chapter_type": "survey_description", "chapter_title": "问卷说明", "sort_order": 4, "level": 1},
            {"chapter_type": "dimension_analysis", "chapter_title": "问卷结果分析", "sort_order": 5, "level": 1},
            {"chapter_type": "conclusion", "chapter_title": "调研结果", "sort_order": 6, "level": 1},
            {"chapter_type": "suggestions", "chapter_title": "建议", "sort_order": 7, "level": 1},
            {"chapter_type": "question_original", "chapter_title": "附件1：问卷原文", "sort_order": 8, "level": 1},
            {"chapter_type": "disclaimer", "chapter_title": "附件2：免责声明", "sort_order": 9, "level": 1},
        ]
        
        created_chapters = []
        for data in default_chapters:
            chapter = OutlineChapter(template_id=template_id, **data)
            self.db.add(chapter)
            self.db.flush() # 获取 ID
            created_chapters.append(chapter)
            
            # 特殊处理：问卷结果分析章节
            if chapter.chapter_type == 'dimension_analysis':
                self._create_dimension_subchapters(template_id, chapter.id)
        
        self.db.commit()
        
        # 重新获取完整大纲
        stmt = select(OutlineChapter).where(
            OutlineChapter.template_id == template_id,
            OutlineChapter.parent_id == None
        ).order_by(OutlineChapter.sort_order)
        return self.db.execute(stmt).scalars().all()

    def _create_dimension_subchapters(self, template_id: int, parent_id: int):
        # 获取模板的所有维度
        stmt = select(Dimension).where(Dimension.template_id == template_id).order_by(Dimension.sort_order)
        dimensions = self.db.execute(stmt).scalars().all()
        
        for dim in dimensions:
            sub_chapter = OutlineChapter(
                template_id=template_id,
                chapter_type='dimension_analysis_sub',
                chapter_title=f"{dim.dimension_number} {dim.dimension_title}",
                sort_order=dim.sort_order,
                level=2,
                parent_id=parent_id,
                generation_type='data' # 维度分析通常基于数据
            )
            self.db.add(sub_chapter)
            self.db.flush()

    def reset_outline(self, template_id: int):
        # 删除现有大纲
        stmt = delete(OutlineChapter).where(OutlineChapter.template_id == template_id)
        self.db.execute(stmt)
        self.db.commit()
        
        # 重新创建默认大纲
        return self.create_default_outline(template_id)

    def update_chapter(self, chapter_id: int, data: OutlineChapterUpdate):
        stmt = select(OutlineChapter).where(OutlineChapter.id == chapter_id)
        chapter = self.db.execute(stmt).scalar_one_or_none()
        if not chapter:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(chapter, key, value)
            
        self.db.commit()
        self.db.refresh(chapter)
        return chapter

    def reorder_chapters(self, data: OutlineReorderRequest):
        for item in data.items:
            stmt = update(OutlineChapter).where(OutlineChapter.id == item.id).values(
                sort_order=item.sort_order,
                parent_id=item.parent_id
            )
            self.db.execute(stmt)
        self.db.commit()
        return True
        
    def add_custom_chapter(self, data: OutlineChapterCreate):
        chapter = OutlineChapter(**data.model_dump())
        self.db.add(chapter)
        self.db.commit()
        self.db.refresh(chapter)
        return chapter

    def delete_chapter(self, chapter_id: int):
        stmt = select(OutlineChapter).where(OutlineChapter.id == chapter_id)
        chapter = self.db.execute(stmt).scalar_one_or_none()
        if not chapter:
            return False
            
        self.db.delete(chapter)
        self.db.commit()
        return True
