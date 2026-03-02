「维度配置」与「大纲配置」合并设计方案

一、设计目标

将两个独立的概念合并为一个统一的「报告结构配置」

原概念	问题	新方案
维度配置	只关注第四章（问卷结果分析）	统一纳入大纲管理
大纲配置	只关注章节顺序	包含所有内容节点
合并后	结构混乱，配置分散	统一的树形节点配置
二、核心概念重新定义

2.1 报告 = 章节树 + 数据映射

报告结构（统一树形）
├── 前言（AI生成节点）
├── 项目背景（AI生成节点）
├── 项目开展情况（AI生成节点）
├── 问卷说明（固定内容节点）
├── 问卷结果分析（容器节点）◀── 原「维度配置」融入此处
│   ├── 4.1 用药基础信息（容器节点）◀── 原「大维度」
│   │   ├── 用药原因分析（叶子节点）◀── 原「小分析标题」
│   │   │   └── 数据表格（题1）
│   │   └── 药品获取途径分析（叶子节点）
│   │       └── 数据表格（题2）
│   └── 4.2 用药行为与习惯（容器节点）
│       └── ...
├── 调研结果（AI生成节点）
├── 建议（AI生成节点）
└── 附件（固定内容节点）
2.2 节点类型统一

所有配置项都是「节点」，只是类型不同：

节点类型	说明	对应原概念
ai_chapter	AI生成的章节	原大纲的前言/背景/结论等
fixed_content	固定内容章节	问卷说明、附件
container	容器节点（可包含子节点）	原「第四章」、原「大维度」
data_analysis	数据分析节点（叶子）	原「小分析标题」
三、数据模型设计

3.1 合并后的表结构

只保留一张核心配置表：

-- report_structures（报告结构配置表）
CREATE TABLE report_structures (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- 基本信息
    structure_name VARCHAR(100) NOT NULL COMMENT '结构名称（如：标准医生问卷）',
    report_type ENUM('doctor', 'patient') NOT NULL COMMENT '报告类型',
    
    -- 结构层级：1=单层, 2=两层, 3=三层
    -- 决定问卷结果分析部分的展示方式
    analysis_depth TINYINT NOT NULL DEFAULT 3 COMMENT '分析层级深度',
    
    description TEXT COMMENT '结构描述',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_report_type (report_type)
) ENGINE=InnoDB COMMENT='报告结构配置（合并原维度模板+大纲配置）';

-- structure_nodes（结构节点表 - 统一配置所有层级）
CREATE TABLE structure_nodes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    structure_id BIGINT NOT NULL COMMENT '所属结构ID',
    
    -- 层级关系（树形结构）
    parent_id BIGINT COMMENT '父节点ID，NULL表示顶层章节',
    level TINYINT NOT NULL COMMENT '节点层级：1=章, 2=节, 3=小节',
    
    -- 基础信息
    node_type ENUM(
        'ai_chapter',      -- AI生成章节（前言、背景、结论等）
        'fixed_content',   -- 固定内容（问卷说明、附件）
        'container',       -- 容器节点（第四章、大维度）
        'data_analysis'    -- 数据分析节点（小分析、单题分析）
    ) NOT NULL COMMENT '节点类型',
    
    title VARCHAR(200) NOT NULL COMMENT '节点标题',
    sort_order INT DEFAULT 0 COMMENT '同级排序',
    
    -- 数据映射（仅data_analysis节点使用）
    question_number INT COMMENT '关联Excel题号（一题一分析）',
    
    -- 显示配置
    show_data_table BOOLEAN DEFAULT TRUE COMMENT '显示数据表格',
    show_ai_interpretation BOOLEAN DEFAULT FALSE COMMENT '显示AI解读',
    
    -- AI配置（仅ai_chapter和data_analysis使用）
    prompt_config_id BIGINT COMMENT '关联提示词配置ID',
    
    -- 固定内容（仅fixed_content使用）
    fixed_content TEXT COMMENT '固定内容文本',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (structure_id) REFERENCES report_structures(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES structure_nodes(id) ON DELETE CASCADE,
    INDEX idx_structure_level (structure_id, level, sort_order),
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB COMMENT='结构节点表（统一配置章节、维度、分析）';
3.2 废弃的原表

合并后以下表将不再使用（迁移数据后删除）：

dimension_templates
dimensions
question_analysis_configs
prompt_configs（合并到structure_nodes）
四、三种模板的具体配置示例

4.1 模板一：三层结构（原维度+小分析）

结构特点：

问卷结果分析 → 大维度（4.1/4.2）→ 小分析标题 → 数据表格
{
  "structure_name": "标准医生问卷-三层结构",
  "report_type": "doctor",
  "analysis_depth": 3,
  "nodes": [
    // 第一层：标准章节
    {"id": 1, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "前言", "sort_order": 1},
    {"id": 2, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "一、项目背景", "sort_order": 2},
    {"id": 3, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "二、项目开展情况", "sort_order": 3},
    {"id": 4, "parent_id": null, "level": 1, "type": "fixed_content", "title": "三、问卷说明", "sort_order": 4, "fixed_content": "..."},
    
    // 第二层：问卷结果分析（容器）
    {"id": 5, "parent_id": null, "level": 1, "type": "container", "title": "四、问卷结果分析", "sort_order": 5},
    
    // 第三层：大维度（容器）
    {"id": 6, "parent_id": 5, "level": 2, "type": "container", "title": "4.1 药品疗效", "sort_order": 1},
    {"id": 7, "parent_id": 5, "level": 2, "type": "container", "title": "4.2 用药安全性", "sort_order": 2},
    
    // 第四层：小分析（叶子节点）◀── 原「小分析标题」
    {"id": 8, "parent_id": 6, "level": 3, "type": "data_analysis", "title": "消化功能改善效果分析", "question_number": 1, "show_data_table": true, "show_ai_interpretation": false},
    {"id": 9, "parent_id": 6, "level": 3, "type": "data_analysis", "title": "中气下陷症状缓解分析", "question_number": 2, "show_data_table": true, "show_ai_interpretation": false},
    {"id": 10, "parent_id": 7, "level": 3, "type": "data_analysis", "title": "中西药联用安全性分析", "question_number": 5, "show_data_table": true, "show_ai_interpretation": false},
    
    // 结论章节
    {"id": 11, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "五、调研结果", "sort_order": 6},
    {"id": 12, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "六、建议", "sort_order": 7}
  ]
}
4.2 模板二：两层结构（仅维度，无小分析）

结构特点：

问卷结果分析 → 大维度（4.1/4.2）→ 直接数据表格
{
  "structure_name": "简化医生问卷-两层结构",
  "report_type": "doctor",
  "analysis_depth": 2,
  "nodes": [
    {"id": 1, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "前言"},
    {"id": 2, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "调研背景与核心目标"},
    {"id": 3, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "调研设计与样本特征"},
    
    // 问卷结果分析（容器）
    {"id": 4, "parent_id": null, "level": 1, "type": "container", "title": "调研数据深度解析", "sort_order": 4},
    
    // 大维度直接作为数据分析节点（叶子）◀── 没有小分析层
    {"id": 5, "parent_id": 4, "level": 2, "type": "data_analysis", "title": "疗效表现与临床获益：降压护器官，表现优异", "question_number": 2, "show_data_table": true, "show_ai_interpretation": true},
    {"id": 6, "parent_id": 4, "level": 2, "type": "data_analysis", "title": "降压时间特性：起效快且持续稳", "question_number": 3, "show_data_table": true, "show_ai_interpretation": true},
    {"id": 7, "parent_id": 4, "level": 2, "type": "data_analysis", "title": "患者用药依从性：单片剂型助力，仍有优化空间", "question_number": 4, "show_data_table": true, "show_ai_interpretation": true},
    
    {"id": 8, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "调研结果"},
    {"id": 9, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "建议"}
  ]
}
4.3 模板三：单层结构（无维度概念）

结构特点：

问卷结果分析 → 直接按题号/主题顺序排列
{
  "structure_name": "患者问卷-单层结构",
  "report_type": "patient",
  "analysis_depth": 1,
  "nodes": [
    {"id": 1, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "调研背景与核心目标"},
    {"id": 2, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "调研设计与样本特征"},
    {"id": 3, "parent_id": null, "level": 1, "type": "fixed_content", "title": "调研结果一览表"},
    
    // 问卷结果分析（容器）
    {"id": 4, "parent_id": null, "level": 1, "type": "container", "title": "调研数据深度解析"},
    
    // 直接作为数据分析节点，平铺排列 ◀── 无维度分组
    {"id": 5, "parent_id": 4, "level": 2, "type": "data_analysis", "title": "用药诉求与适应症分析（题 1）", "question_number": 1, "show_data_table": true, "show_ai_interpretation": true},
    {"id": 6, "parent_id": 4, "level": 2, "type": "data_analysis", "title": "药品获取渠道分析（题 2）", "question_number": 2, "show_data_table": true, "show_ai_interpretation": true},
    {"id": 7, "parent_id": 4, "level": 2, "type": "data_analysis", "title": "用药周期特征分析（题 3）", "question_number": 3, "show_data_table": true, "show_ai_interpretation": false},
    
    {"id": 8, "parent_id": null, "level": 1, "type": "ai_chapter", "title": "调研结果"}
  ]
}
五、系统架构变化

5.1 数据流变化

合并前（分散）：

用户配置维度 ──► dimensions表 ──┐
                                ├──► Word生成（需要同时查两套配置）
用户配置大纲 ──► outline表 ────┘
合并后（统一）：

用户配置结构 ──► structure_nodes表 ──► Word生成（一张表搞定）
5.2 Word生成逻辑变化

合并前（硬编码+动态查询）：

def generate_report(report_data):
    # 硬编码大纲
    add_chapter("前言")
    add_chapter("项目背景")
    ...
    
    # 动态查询维度
    dimensions = query_dimensions(report_data.template_id)
    for dim in dimensions:
        add_heading(dim.title)
        for analysis in dim.analyses:
            add_sub_heading(analysis.title)
            add_table(analysis.question_number)
合并后（统一遍历树）：

def generate_report(report_data):
    structure = get_structure(report_data.structure_id)
    nodes = build_tree(structure.nodes)  # 构建树形
    
    def traverse(node, level):
        if node.type == 'ai_chapter':
            add_ai_content(node, level)
        elif node.type == 'fixed_content':
            add_fixed_content(node, level)
        elif node.type == 'container':
            add_heading(node.title, level)
            for child in node.children:
                traverse(child, level + 1)
        elif node.type == 'data_analysis':
            add_analysis(node, level)  # 根据配置显示表格/AI解读
    
    for root_node in nodes:
        traverse(root_node, level=1)
六、前端界面设计

6.1 统一的结构配置界面

┌──────────────────────────────────────────────────────────────────┐
│  报告结构配置                                     [保存] [预览]   │
├──────────────────────────────────────────────────────────────────┤
│  结构名称：[标准医生问卷-补中益气口服液              ]            │
│  报告类型：[医生问卷 ▼]                                          │
│  分析层级：[三层（维度+小分析）▼] ○ 两层 ○ 单层                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📋 节点树（可拖拽调整顺序和层级）                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ☰ 前言                                    [类型:AI] [✏️]   │ │
│  │ ☰ 一、项目背景                            [类型:AI] [✏️]   │ │
│  │ ☰ 二、项目开展情况                        [类型:AI] [✏️]   │ │
│  │ ☰ 三、问卷说明                            [类型:固定] [✏️] │ │
│  │                                                               │ │
│  │ ▼ 四、问卷结果分析（容器）                                    │ │
│  │   │                                                             │ │
│  │   ├─ ▼ 4.1 药品疗效（容器）                                   │ │
│  │   │   ├─ ☰ 消化功能改善效果分析          [题1] [表格☑] [AI☐] │ │
│  │   │   └─ ☰ 中气下陷症状缓解分析          [题2] [表格☑] [AI☐] │ │
│  │   │                                                             │ │
│  │   └─ ▼ 4.2 用药安全性（容器）                                 │ │
│  │       └─ ☰ 中西药联用安全性分析          [题5] [表格☑] [AI☐] │ │
│  │                                                               │ │
│  │ ☰ 五、调研结果                            [类型:AI] [✏️]   │ │
│  │ ☰ 六、建议                                [类型:AI] [✏️]   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  [+ 添加节点]  [批量导入题号]  [从参考报告AI分析]                 │
└────────────────────────────────────────────────────────────────────┘
6.2 节点编辑弹窗

┌──────────────────────────────────────────┐
│  编辑节点                    [X]         │
├──────────────────────────────────────────┤
│  节点类型：[数据分析节点 ▼]              │
│  节点标题：[消化功能改善效果分析        ] │
│                                           │
│  关联题号：[1 ▼]                          │
│                                           │
│  显示设置：                                │
│  ☑ 显示数据表格                           │
│  ☐ 显示AI解读                             │
│                                           │
│  当勾选AI解读时显示：                      │
│  AI提示词：[选择提示词 ▼] [编辑]          │
│                                           │
│          [取消]  [保存]                   │
└────────────────────────────────────────────┘
七、实施建议

7.1 迁移策略

步骤1：双轨运行（过渡期）

保留旧表，只读
新表写入
兼容旧报告导出
步骤2：数据迁移脚本

# 将原维度配置转为新结构
def migrate_dimension_to_structure(old_template_id):
    # 创建新structure
    structure = create_structure(
        name=old_template.template_name,
        report_type=old_template.report_type,
        analysis_depth=3  # 原维度都是三层
    )
    
    # 创建"问卷结果分析"容器节点
    container = create_node(structure.id, None, 1, 'container', '四、问卷结果分析')
    
    # 迁移维度
    for dim in old_template.dimensions:
        # 创建大维度容器节点
        dim_node = create_node(structure.id, container.id, 2, 'container', 
                              f"{dim.dimension_number} {dim.dimension_title}")
        
        # 迁移小分析
        for analysis in dim.analyses:
            create_node(structure.id, dim_node.id, 3, 'data_analysis',
                       analysis.analysis_title,
                       question_number=analysis.question_number,
                       show_data_table=True,
                       show_ai_interpretation=False)
步骤3：完全切换

停用旧表写入
删除旧表（可选）
7.2 性能考虑

索引优化：structure_id + level + sort_order 复合索引
缓存策略：结构配置读多写少，可Redis缓存
树形查询：使用CTE递归查询或应用层组装
7.3 扩展性预留

支持第4种结构：只需新增 analysis_depth = 4
支持新节点类型：扩展 node_type 枚举
支持多语言：增加 title_en, title_cn 等字段
八、关键设计决策总结

决策点	选择	理由
表合并	合并为 structure_nodes	统一配置，简化逻辑
树形深度	支持无限层级（实际用3层）	未来可扩展
题号映射	一题一分析（1:1）	简化数据模型
AI解读	每个节点独立开关	灵活控制
标题格式	用户完整输入	满足不同报告风格
