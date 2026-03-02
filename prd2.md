📋 大纲配置功能清单

一、数据模型层

1.1 大纲章节表 (outline_chapters)

字段	类型	说明
id	bigint	主键
template_id	bigint	关联维度模板
chapter_type	varchar(50)	章节类型标识
chapter_title	varchar(200)	显示标题（可自定义）
sort_order	int	排序序号
is_enabled	boolean	是否启用
level	int	层级（1=一级，2=二级）
parent_id	bigint	父章节ID（支持嵌套）
generation_type	enum	生成方式：ai/固定模板/数据源
prompt_config_id	bigint	关联提示词配置（AI章节）
fixed_content	text	固定内容（固定模板章节）
1.2 章节类型枚举

ChapterType = {
    'preface': '前言',
    'background': '项目背景', 
    'project_info': '项目开展情况',
    'survey_description': '问卷说明',
    'dimension_analysis': '问卷结果分析',  # 第四章特殊类型
    'conclusion': '调研结果',
    'suggestions': '建议',
    'question_original': '问卷原文',
    'disclaimer': '免责声明',
    'custom': '自定义章节'
}
二、核心功能模块

2.1 章节基础配置

✅ 启用/禁用控制：每个章节可独立开关
✅ 标题自定义：修改显示标题，不影响章节类型
✅ 排序调整：拖拽调整章节顺序
✅ 动态编号：根据顺序自动生成"一、二、三"或"1. 2. 3."
✅ 层级设置：支持一级/二级标题切换
2.2 第四章特殊配置（问卷结果分析）

✅ 维度顺序：继承现有sort_order
✅ 三级标题显隐：控制是否显示analysis_title
✅ 数据表格样式：可选择横向/纵向表格
✅ 数据解读开关：是否生成AI数据解读（预留功能）
2.3 差异化配置

✅ 报告类型维度：医生报告/患者报告使用不同大纲
✅ 模板级配置：每个维度模板可绑定独立大纲
✅ 继承机制：新模板可继承默认大纲后修改
2.4 生成配置

✅ AI章节：关联提示词配置
✅ 固定模板章节：编辑固定文本内容
✅ 数据源章节：配置Excel数据映射规则
三、API接口层

3.1 大纲管理API

GET    /api/v1/templates/{id}/outline          # 获取模板大纲
PUT    /api/v1/templates/{id}/outline          # 更新大纲配置
POST   /api/v1/templates/{id}/outline/reset    # 重置为默认大纲
POST   /api/v1/outline/chapters/{id}/move      # 移动章节位置
POST   /api/v1/outline/chapters/{id}/toggle    # 启用/禁用切换
3.2 报告生成适配

报告生成时读取模板绑定的大纲配置
根据大纲顺序调用扣子API
按大纲结构组装Word文档
四、前端界面功能

4.1 大纲配置页面

┌──────────────────────────────────────────────────────────────┐
│  报告生成工具 / 维度模板 / 大纲配置                             │
├──────────────────────────────────────────────────────────────┤
│  模板：患者问卷模板                              [预览] [重置]  │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ☰  前言                                    [编辑] [开关✓]    │
│  ☰  一、项目背景                             [编辑] [开关✓]    │
│  ☰  二、项目开展情况                          [编辑] [开关✓]    │
│  ☰  三、问卷说明                              [编辑] [开关✓]    │
│  ☰  ▼ 四、问卷结果分析                        [编辑] [开关✓]    │
│       ├── 4.1 用药基础信息                                    │
│       ├── 4.2 用药行为与习惯                                   │
│       └── ...                                                 │
│  ☰  五、调研结果                             [编辑] [开关✓]    │
│  ☰  六、建议                                [编辑] [开关✓]     │
│  ☰  附件1：问卷原文                          [编辑] [开关✓]    │
│  ☰  附件2：免责声明                          [编辑] [开关✓]    │
│                                                                │
│  [+ 添加自定义章节]                                            │
│                                                                │
│  [保存大纲配置]                                                │
└──────────────────────────────────────────────────────────────┘
4.2 交互功能

拖拽排序：上下拖拽调整章节顺序
实时预览：右侧显示大纲结构预览
快速编辑：点击编辑修改标题和配置
一键重置：恢复默认大纲结构
章节搜索：快速定位章节
五、与现有系统集成

5.1 Word生成服务改造

# 改造前（硬编码）
def generate_report(self, report_data, outline_config):
    # 根据大纲配置动态生成
    for chapter in outline_config.chapters:
        if not chapter.is_enabled:
            continue
            
        if chapter.level == 1:
            self._add_chapter(doc, chapter, report_data)
        elif chapter.level == 2:
            self._add_sub_chapter(doc, chapter, report_data)
5.2 扣子服务调用改造

# 按大纲顺序调用扣子
async def generate_by_outline(self, outline_config, report_data):
    for chapter in outline_config.get_enabled_chapters():
        if chapter.generation_type == 'ai':
            await self.generate_ai_chapter(chapter, report_data)
5.3 数据迁移

存量模板自动创建默认大纲配置
默认大纲与当前硬编码结构一致
支持一键同步更新
六、扩展功能（可选）

6.1 版本管理

大纲配置版本历史
对比不同版本差异
一键回滚到历史版本
6.2 导入导出

导出大纲配置为JSON/YAML
从文件导入大纲配置
大纲配置模板库
6.3 智能推荐

根据报告类型推荐大纲结构
分析用户历史报告推荐优化建议
