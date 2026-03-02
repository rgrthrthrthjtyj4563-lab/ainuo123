# 报告生成工具 - 设计文档

## 一、系统概述

### 1.1 系统名称
**报告生成工具**

### 1.2 功能模块
| 菜单 | 功能 | 使用者 |
|------|------|--------|
| **维度配置** | 创建/编辑维度模板（大标题+问题分析标题+题号映射） | 管理员 |
| **报告生成** | 选择维度模板 → 上传Excel → 生成Word报告 | 用户 |

### 1.3 核心流程

```
┌─────────────────────────────────────────────────────────────────┐
│                         维度配置（管理员）                        │
│  创建模板 → 添加维度（4.1、4.2...）→ 添加问题（题号+分析标题）     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         报告生成（用户）                          │
│  选择维度模板 → 填写报告信息 → 上传Excel → 生成Word → 导出        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、数据库设计

### 2.1 表结构

```sql
-- 1. 维度模板表
CREATE TABLE dimension_templates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    template_name VARCHAR(100) NOT NULL COMMENT '模板名称（如：患者问卷模板）',
    report_type ENUM('doctor', 'patient') NOT NULL COMMENT '报告类型',
    description TEXT COMMENT '模板描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. 维度表（大维度）
CREATE TABLE dimensions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    template_id BIGINT NOT NULL COMMENT '所属模板ID',
    dimension_number VARCHAR(10) NOT NULL COMMENT '维度编号（如：4.1）',
    dimension_title VARCHAR(100) NOT NULL COMMENT '维度标题（如：用药基础信息）',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES dimension_templates(id) ON DELETE CASCADE
);

-- 3. 问题分析配置表（小分析标题）
CREATE TABLE question_analysis_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    dimension_id BIGINT NOT NULL COMMENT '所属维度ID',
    question_number INT NOT NULL COMMENT '问题编号（如：1）',
    analysis_title VARCHAR(200) NOT NULL COMMENT '分析标题（如：用药原因分析）',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dimension_id) REFERENCES dimensions(id) ON DELETE CASCADE,
    UNIQUE KEY uk_dimension_question (dimension_id, question_number)
);

-- 4. 提示词配置表
CREATE TABLE prompt_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    config_name VARCHAR(100) NOT NULL COMMENT '配置名称',
    report_type ENUM('doctor', 'patient') NOT NULL,
    section_type ENUM('preface', 'background', 'project_info', 'conclusion', 'suggestions') NOT NULL COMMENT '章节类型',
    system_prompt TEXT NOT NULL COMMENT '系统提示词',
    user_prompt_template TEXT NOT NULL COMMENT '用户提示词模板',
    temperature DECIMAL(3,2) DEFAULT 0.7,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 报告表
CREATE TABLE reports (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    template_id BIGINT NOT NULL COMMENT '使用的维度模板ID',
    report_title VARCHAR(200) NOT NULL COMMENT '报告标题',
    product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
    survey_region VARCHAR(100) NOT NULL COMMENT '调研区域',
    survey_time_range VARCHAR(100) NOT NULL COMMENT '调研时间范围',
    sample_count INT NOT NULL COMMENT '样本数量',
    excel_data JSON COMMENT '解析后的Excel数据',
    generated_content JSON COMMENT '扣子生成的各章节内容',
    status ENUM('draft', 'generated') DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 2.2 数据示例

```sql
-- 维度模板
INSERT INTO dimension_templates (id, template_name, report_type) VALUES
(1, '患者问卷模板', 'patient');

-- 维度（大标题）
INSERT INTO dimensions (id, template_id, dimension_number, dimension_title, sort_order) VALUES
(1, 1, '4.1', '用药基础信息', 1),
(2, 1, '4.2', '用药行为与习惯', 2),
(3, 1, '4.3', '药品使用体验', 3),
(4, 1, '4.4', '用药安全性', 4),
(5, 1, '4.5', '疗效评价', 5),
(6, 1, '4.6', '药品改进需求', 6),
(7, 1, '4.7', '临床价值延伸', 7);

-- 问题分析配置（小标题+题号）
INSERT INTO question_analysis_configs (dimension_id, question_number, analysis_title, sort_order) VALUES
(1, 1, '用药原因分析', 1),           -- 4.1维度下的问题1
(1, 2, '药品获取途径分析', 2),       -- 4.1维度下的问题2
(1, 3, '用药时长分析', 3),           -- 4.1维度下的问题3
(2, 4, '服用剂量规范性分析', 1),     -- 4.2维度下的问题4
(2, 10, '联合调理方式分析', 2),      -- 4.2维度下的问题10
(3, 5, '药品口味接受度分析', 1),     -- 4.3维度下的问题5
(3, 7, '包装设计满意度分析', 2);     -- 4.3维度下的问题7
```

---

## 三、维度配置界面设计

### 3.1 界面结构

```
┌─────────────────────────────────────────────────────────────────┐
│  报告生成工具 > 维度配置                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────────────────────────────────┐   │
│  │             │  │                                         │   │
│  │  模板列表    │  │           维度配置详情                   │   │
│  │             │  │                                         │   │
│  │  [+] 新建   │  │  模板名称：患者问卷模板                   │   │
│  │             │  │  报告类型：患者问卷                       │   │
│  │  ● 患者问卷 │  │                                         │   │
│  │  ○ 医生问卷 │  │  ┌─────────────────────────────────┐   │   │
│  │             │  │  │  维度 4.1：用药基础信息           │   │   │
│  │             │  │  │                                 │   │   │
│  │             │  │  │  题号 │ 分析标题                  │   │   │
│  │             │  │  │  ──── │ ──────────────────────── │   │   │
│  │             │  │  │   1   │ 用药原因分析              │   │   │
│  │             │  │  │   2   │ 药品获取途径分析          │   │   │
│  │             │  │  │   3   │ 用药时长分析              │   │   │
│  │             │  │  │  [+ 添加问题]                    │   │   │
│  │             │  │  └─────────────────────────────────┘   │   │
│  │             │  │                                         │   │
│  │             │  │  [+ 添加维度]                            │   │
│  │             │  │                                         │   │
│  │             │  │  [保存模板]                              │   │
│  │             │  │                                         │   │
│  └─────────────┘  └─────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 核心交互

| 操作 | 功能 |
|------|------|
| 新建模板 | 创建空白维度模板 |
| 添加维度 | 输入维度编号（4.1）和维度标题 |
| 添加问题 | 输入题号和对应的分析标题 |
| 删除/编辑 | 修改维度或问题配置 |
| 保存模板 | 保存到数据库 |

---

## 四、报告生成流程

### 4.1 完整流程图

```
用户操作                              后端处理
─────────                            ─────────
  │                                      │
  ▼                                      ▼
┌─────────────┐                    ┌─────────────┐
│ 选择维度模板 │ ─────────────────→ │ 查询模板配置 │
│ (下拉选择)   │                    │ (维度+问题)  │
└─────────────┘                    └─────────────┘
  │                                      │
  ▼                                      ▼
┌─────────────┐                    ┌─────────────┐
│ 填写报告信息 │ ─────────────────→ │ 暂存报告记录 │
│ (标题/产品等)│                    │ (status=draft)│
└─────────────┘                    └─────────────┘
  │                                      │
  ▼                                      ▼
┌─────────────┐                    ┌─────────────┐
│ 上传Excel   │ ─────────────────→ │ 解析Excel   │
│             │                    │ (pandas)    │
└─────────────┘                    └─────────────┘
  │                                      │
  ▼                                      ▼
┌─────────────┐                    ┌─────────────┐
│ 点击生成    │ ─────────────────→ │ 组装数据    │
│             │                    │             │
└─────────────┘                    │ 1. 报告基本信息
                                   │ 2. 维度配置（大标题+小标题）
                                   │ 3. Excel数据（按维度分组）
                                   └─────────────┘
                                          │
                                          ▼
                                   ┌─────────────┐
                                   │ 调用扣子API │
                                   │ (5个LLM节点)│
                                   │             │
                                   │ • 前言      │
                                   │ • 项目背景  │
                                   │ • 项目开展  │
                                   │ • 调研结果  │
                                   │ • 建议      │
                                   └─────────────┘
                                          │
                                          ▼
                                   ┌─────────────┐
                                   │ 拼接完整报告 │
                                   │             │
                                   │ 前言        │ ← 扣子生成
                                   │ 项目背景    │ ← 扣子生成
                                   │ 项目开展    │ ← 扣子生成
                                   │ 问卷说明    │ ← 固定模板
                                   │ 维度分析    │ ← 配置+Excel表格
                                   │ 调研结果    │ ← 扣子生成
                                   │ 建议        │ ← 扣子生成
                                   │ 附件        │ ← 固定模板
                                   └─────────────┘
                                          │
                                          ▼
                                   ┌─────────────┐
                                   │ 生成Word    │
                                   │ (python-docx)│
                                   └─────────────┘
                                          │
                                          ▼
┌─────────────┐                    ┌─────────────┐
│ 在线编辑    │ ←──────────────── │ 返回Word链接 │
│ 导出下载    │                    │             │
└─────────────┘                    └─────────────┘
```

### 4.2 数据组装格式

```json
{
  "report_info": {
    "product_name": "补中益气口服液",
    "survey_region": "海南省",
    "survey_time_range": "2025年10月1日-10月31日",
    "sample_count": 707,
    "question_count": 12
  },
  
  "dimensions": [
    {
      "dimension_number": "4.1",
      "dimension_title": "用药基础信息",
      "questions": [
        {
          "question_number": 1,
          "question_title": "您当时是因何种症状服用...",
          "analysis_title": "用药原因分析",
          "options": [
            {"key": "A", "text": "脾胃虚弱...", "count": 162, "percentage": "23%"},
            {"key": "B", "text": "体倦乏力...", "count": 169, "percentage": "24%"},
            {"key": "C", "text": "中气下陷...", "count": 226, "percentage": "32%"},
            {"key": "D", "text": "气虚所致...", "count": 150, "percentage": "21%"}
          ]
        }
      ]
    }
  ]
}
```

---

## 五、扣子工作流配置

### 5.1 工作流结构（5个LLM节点）

```
开始节点
  │ 输入：report_info + dimensions
  ▼
┌─────────────────┐
│ 生成前言（LLM） │
│ 节点1           │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ 生成项目背景（LLM）│
│ 节点2           │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ 生成项目开展（LLM）│
│ 节点3           │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ 生成调研结果（LLM）│
│ 节点4           │
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ 生成建议（LLM） │
│ 节点5           │
└─────────────────┘
  │
  ▼
组装输出节点
  │
  ▼
结束节点
```

### 5.2 开始节点输入参数

```json
{
  "product_name": "String - 产品名称",
  "survey_region": "String - 调研区域",
  "survey_time_range": "String - 调研时间",
  "sample_count": "Integer - 样本数量",
  "question_count": "Integer - 问题数量",
  "dimensions": "Array - 维度数据（用于调研结果分析）"
}
```

### 5.3 各节点提示词

#### 节点1：生成前言

**系统提示词：**
```
你是一位资深的医药市场研究报告撰写专家，擅长撰写专业、严谨、有洞察力的调研报告前言。

写作风格要求：
1. 语言正式、专业，体现行业权威性
2. 逻辑清晰，层层递进
3. 既有宏观背景，又有具体调研目的
4. 避免空洞套话，要有实质性内容
5. 适当引用行业术语，体现专业性

字数要求：400-500字
```

**用户提示词：**
```
请为以下产品生成调研报告的前言部分。

【产品信息】
产品名称：{{start.product_name}}
调研区域：{{start.survey_region}}
调研时间：{{start.survey_time_range}}
样本数量：{{start.sample_count}}份

【前言结构要求】
1. 第一段（150-200字）：
   - 介绍产品所属领域的市场背景
   - 说明产品的功效定位和市场地位
   - 引用行业发展趋势

2. 第二段（200-250字）：
   - 说明本次调研的目的和意义
   - 阐述调研将解决的核心问题
   - 说明调研结果的应用价值

【输出格式】
直接输出前言正文，不需要标题。使用专业、客观的语言风格。
```

---

#### 节点2：生成项目背景

**系统提示词：**
```
你是一位专业的医药市场分析师，擅长从行业政策和市场需求角度分析项目背景。

写作风格要求：
1. 结合国家政策和行业趋势
2. 突出调研的必要性和紧迫性
3. 体现区域特色和差异化需求
4. 语言简洁有力，逻辑严密
5. 数据和事实支撑观点

字数要求：300-400字
```

**用户提示词：**
```
请为以下调研项目生成"项目背景"章节内容。

【产品信息】
产品名称：{{start.product_name}}
调研区域：{{start.survey_region}}

【项目背景结构要求】
1. 第一段（150-200字）- 政策与行业背景：
   - 介绍中医药产业发展政策支持
   - 说明补益类中成药的市场趋势
   - 阐述患者用药体验的重要性

2. 第二段（150-200字）- 区域与需求背景：
   - 分析{{start.survey_region}}的区域特点
   - 说明该区域的市场需求特征
   - 阐述专项调研的必要性

【输出格式】
直接输出项目背景正文，不需要标题。分两段，每段一个核心观点。
```

---

#### 节点3：生成项目开展

**系统提示词：**
```
你是一位专业的调研项目管理人员，擅长撰写项目执行情况说明。

写作风格要求：
1. 信息准确、客观
2. 格式规范、清晰
3. 数据精确、可追溯
4. 语言简洁、不冗余

字数要求：100-150字
```

**用户提示词：**
```
请生成"项目开展情况"章节内容。

【项目信息】
产品名称：{{start.product_name}}
调研区域：{{start.survey_region}}
调研时间：{{start.survey_time_range}}
样本数量：{{start.sample_count}}份
问题数量：{{start.question_count}}道

【输出格式要求】
严格按照以下格式输出：

项目工具：调查问卷，{{start.question_count}}道选择题，其内容涵盖多个维度，全面覆盖患者用药全流程关键节点。

样本采集范围：{{start.survey_region}}

样本采集数量：本次共收集筛选到有效问卷{{start.sample_count}}份。

样本采集时间：{{start.survey_time_range}}
```

---

#### 节点4：生成调研结果

**系统提示词：**
```
你是一位资深的医药市场研究专家，擅长从调研数据中提炼核心发现并形成结构化结论。

写作风格要求：
1. 分点陈述，逻辑清晰
2. 每个观点有数据支撑
3. 结论明确、可执行
4. 语言简洁有力
5. 体现专业性和权威性

字数要求：500-600字
```

**用户提示词：**
```
请根据以下维度数据，生成"调研结果"章节内容。

【产品信息】
产品名称：{{start.product_name}}
样本数量：{{start.sample_count}}

【维度汇总数据】
{{#each start.dimensions}}
{{dimension_title}}:
{{#each questions}}
- {{question_title}}: 最高占比 {{max_percentage_option.percentage}}
{{/each}}

{{/each}}

【分析要求】
请生成两部分内容：

### 5.1 问卷重点问题分析（300-400字）
选择2-3个最有代表性的问题进行深度分析：
- 分析问题的内在关联性
- 挖掘数据背后的深层原因
- 体现产品特点和市场定位

### 5.2 调研结果分析（200-250字）
分点总结核心发现（4点）：
1. 用药场景精准，功效定位契合需求
2. 疗效与安全性表现优异
3. 用药行为规范，产品体验良好
4. 综合价值凸显，市场竞争力稳固

【输出格式】
### 5.1 问卷重点问题分析
[深度分析内容]

### 5.2 调研结果分析
**1. 用药场景精准，功效定位契合需求**
[核心发现]

**2. 疗效与安全性表现优异**
[核心发现]

**3. 用药行为规范，产品体验良好**
[核心发现]

**4. 综合价值凸显，市场竞争力稳固**
[核心发现]
```

---

#### 节点5：生成建议

**系统提示词：**
```
你是一位资深的医药市场策略顾问，擅长基于调研数据提出可执行的建议。

写作风格要求：
1. 建议具体、可执行
2. 针对性强，直击问题核心
3. 分层次提出建议（产品、推广、服务等）
4. 语言简洁，避免空话
5. 体现专业性和前瞻性

字数要求：300-400字
```

**用户提示词：**
```
请根据以下调研结果，生成"建议"内容。

【产品信息】
产品名称：{{start.product_name}}
调研区域：{{start.survey_region}}

【关键发现】
{{#each start.dimensions}}
{{dimension_title}}关键数据：
{{#each questions}}
- {{question_title}}: {{max_percentage_option.text}} ({{max_percentage_option.percentage}})
{{/each}}

{{/each}}

【建议要求】
请从以下方面提出3点建议：

1. 强化临床推广与用药指导
   - 依托专业医疗渠道
   - 加强医生/患者教育

2. 聚焦产品细节优化升级
   - 基于患者反馈改进
   - 配方、包装、剂型优化

3. 拓展市场传播与患者教育
   - 差异化市场传播
   - 中医药知识普及

【输出格式】
### 5.3 建议

**1. 强化临床推广与用药指导**
[具体建议，100字左右]

**2. 聚焦产品细节优化升级**
[具体建议，100字左右]

**3. 拓展市场传播与患者教育**
[具体建议，100字左右]
```

---

## 六、Word生成方案

### 6.1 报告结构

```
问卷调研分析报告
├── 前言（扣子生成）
├── 一、项目背景（扣子生成）
├── 二、项目开展情况（扣子生成）
├── 三、问卷说明（固定模板）
├── 四、问卷结果分析（配置+Excel数据）
│   ├── 4.1 用药基础信息（维度配置的大标题）
│   │   ├── 用药原因分析（配置的小标题）
│   │   │   ├── 数据表格（Excel解析）
│   │   │   └── 数据解读（AI生成 - 预留扩展）
│   │   ├── 药品获取途径分析
│   │   │   ├── 数据表格
│   │   │   └── 数据解读
│   │   └── ...
│   ├── 4.2 用药行为与习惯
│   └── ...
├── 五、调研结果（扣子生成）
│   ├── 5.1 问卷重点问题分析
│   ├── 5.2 调研结果分析
│   └── 5.3 建议
├── 附件1：问卷原文（Excel问题列表）
└── 附件2：免责申明（固定模板）
```

### 6.2 Python代码

```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

def generate_word_report(report_data: dict, output_path: str):
    """生成Word报告"""
    
    doc = Document()
    
    # 设置默认字体
    style = doc.styles['Normal']
    style.font.name = 'Microsoft YaHei'
    style._element.rPr.rFonts.set(docx.oxml.ns.qn('w:eastAsia'), 'Microsoft YaHei')
    style.font.size = Pt(12)
    
    # 1. 前言
    doc.add_heading('前言', level=1)
    doc.add_paragraph(report_data['generated_content']['preface'])
    
    # 2. 项目背景
    doc.add_heading('一、项目背景', level=1)
    doc.add_paragraph(report_data['generated_content']['background'])
    
    # 3. 项目开展
    doc.add_heading('二、项目开展情况', level=1)
    doc.add_paragraph(report_data['generated_content']['project_info'])
    
    # 4. 问卷说明
    doc.add_heading('三、问卷说明', level=1)
    doc.add_paragraph('''为增强数据间的可比性与分析结果的准确性，本次报告对问卷原始数据采用以下标准化统计处理方法进行系统整理：

1.数据清洗：严格筛选原始数据，剔除无效填写、关键信息缺失等不符合调研规范的数据样本，保障分析数据的真实性与可靠性；

2.数据转换：针对问卷收集的分类数据进行规范化转换，使其适配后续统计分析逻辑，提升数据应用的合理性与一致性；

3.数据聚合：对具有同类属性的调研数据进行归类整合，凝练核心分析维度，避免数据分散导致的结论偏差，聚焦关键研究问题；

4.数据可视化：结合报告呈现需求，通过直观的可视化方式展示数据分布特征与占比关系，助力快速把握数据规律与核心信息。

通过上述标准化数据处理流程，有效提升了数据的可比性与分析的严谨性，为报告结论的科学性与可信度提供了坚实支撑。''')
    
    # 5. 问卷结果分析（维度分析）
    doc.add_heading('四、问卷结果分析', level=1)
    
    for dim in report_data['dimensions']:
        # 维度大标题
        doc.add_heading(f"{dim['dimension_number']}{dim['dimension_title']}", level=2)
        
        for q in dim['questions']:
            # 小分析标题
            doc.add_heading(q['analysis_title'], level=3)
            
            # 数据表格
            table = doc.add_table(rows=len(q['options']) + 2, cols=5)
            table.style = 'Table Grid'
            
            # 表头
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = q['question_title']
            hdr_cells[1].text = '选项'
            
            for i, opt in enumerate(q['options']):
                hdr_cells[i + 2].text = f"{opt['key']}. {opt['text']}"
            
            # 样本量行
            count_cells = table.rows[1].cells
            count_cells[0].text = ''
            count_cells[1].text = '样本量'
            for i, opt in enumerate(q['options']):
                count_cells[i + 2].text = str(opt['count'])
            
            # 占比行
            pct_cells = table.rows[2].cells
            pct_cells[0].text = ''
            pct_cells[1].text = '占比'
            for i, opt in enumerate(q['options']):
                pct_cells[i + 2].text = opt['percentage']
            
            # 空行
            doc.add_paragraph()
    
    # 6. 调研结果
    doc.add_heading('五、调研结果', level=1)
    doc.add_paragraph(report_data['generated_content']['conclusion'])
    
    # 7. 建议
    doc.add_heading('六、建议', level=1)
    doc.add_paragraph(report_data['generated_content']['suggestions'])
    
    # 8. 附件
    doc.add_heading('附件1：问卷原文', level=1)
    for dim in report_data['dimensions']:
        for q in dim['questions']:
            p = doc.add_paragraph()
            p.add_run(f"{q['question_number']}. {q['question_title']}").bold = True
            for opt in q['options']:
                doc.add_paragraph(f"   {opt['key']}. {opt['text']}", style='List Bullet')
    
    doc.add_heading('附件2：免责申明', level=1)
    doc.add_paragraph('''（1）本次调研项目以随机选取对象进行面对面调研，本次调研只对本次样本数据负责。

（2）承接单位调研项目，是针对该产品品种调研，并非指定厂家指定品种。

（3）本次调研只针对调研区域数据负责，不代表全国调研数据。

服务提供单位：北京玖麟空科技有限公司''')
    
    # 保存
    doc.save(output_path)
    return output_path
```

---

## 七、API接口设计

### 7.1 维度配置接口

```python
# 创建维度模板
POST /api/dimension-templates
{
  "template_name": "患者问卷模板",
  "report_type": "patient",
  "dimensions": [
    {
      "dimension_number": "4.1",
      "dimension_title": "用药基础信息",
      "questions": [
        {"question_number": 1, "analysis_title": "用药原因分析"},
        {"question_number": 2, "analysis_title": "药品获取途径分析"}
      ]
    }
  ]
}

# 获取模板列表
GET /api/dimension-templates

# 获取模板详情
GET /api/dimension-templates/{id}

# 更新模板
PUT /api/dimension-templates/{id}

# 删除模板
DELETE /api/dimension-templates/{id}
```

### 7.2 报告生成接口

```python
# 创建报告（上传Excel后）
POST /api/reports
{
  "template_id": 1,
  "report_title": "补中益气口服液调研报告",
  "product_name": "补中益气口服液",
  "survey_region": "海南省",
  "survey_time_range": "2025年10月1日-10月31日",
  "sample_count": 707,
  "excel_data": {...}  # 解析后的Excel数据
}

# 生成报告（调用扣子）
POST /api/reports/{id}/generate
# 返回：生成的各章节内容

# 获取报告内容
GET /api/reports/{id}

# 导出Word
GET /api/reports/{id}/export
# 返回：Word文件下载
```

---

## 八、总结

| 模块 | 实现方式 |
|------|----------|
| 维度配置 | 后台界面，人工配置大标题+小标题+题号 |
| 报告生成 | 选择模板 → 上传Excel → 调用扣子（5节点）→ 生成Word |
| 扣子节点 | 前言、项目背景、项目开展、调研结果、建议（共5个） |
| 维度分析 | 配置内容 + Excel数据表格（无AI生成） |
| Word生成 | python-docx，纯文本+表格 |

**核心优势**：
1. 维度可配置，灵活适配不同问卷
2. 扣子节点精简，只有5个必要节点
3. 无图表，开发简单
4. 流程清晰，易于维护

