# 报告生成工具 - 系统设计文档

## 一、系统分析

### 1.1 现状分析

**当前系统状态**: 目前项目仅有PRD文档，尚未有任何代码实现。

**差距识别**:
1. ✅ 需求完整：PRD文档涵盖了所有功能需求、非功能需求、用户场景
2. ❌ 无数据库：未建立MySQL数据库
3. ❌ 无后端API：未实现任何API接口
4. ❌ 无前端界面：未构建任何UI
5. ❌ 无扣子集成：未配置扣子工作流
6. ❌ 无Word生成：未实现python-docx逻辑

### 1.2 PRD需求归纳

| 模块 | PRD要求 | 优先级 |
|------|---------|--------|
| 维度配置 | 模板CRUD + 维度管理 + 问题配置 | P0 |
| 报告生成 | 选择模板 + 上传Excel + 生成Word | P0 |
| 扣子集成 | 5个LLM节点（前言/背景/开展/结果/建议） | P0 |
| Word生成 | python-docx，纯文本+表格 | P0 |

---

## 二、系统架构设计

### 2.1 技术栈

| 层次 | 技术选择 | 理由 |
|------|---------|------|
| 前端 | HTML5 + Tailwind CSS + Vanilla JS | 轻量、快速开发、B端风格 |
| 后端 | Python + FastAPI | 高性能、现代、易集成 |
| 数据库 | MySQL 8.0 | 结构化数据、事务支持 |
| AI服务 | 扣子API | PRD指定、流式输出 |
| 文档生成 | python-docx | PRD指定 |

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端层 (Frontend)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ 维度配置页面  │  │ 报告生成页面  │  │ 报告查看/下载页面    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API层 (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ 模板管理API   │  │ 报告管理API   │  │ 扣子集成API          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         服务层 (Services)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Excel解析服务 │  │ 扣子流式调用  │  │ Word生成服务         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         数据层 (Data)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ MySQL数据库   │  │ 文件存储      │  │ 扣子API             │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 模块划分

| 模块 | 职责 | 对应PRD章节 |
|------|------|-------------|
| Template Management | 维度模板的CRUD操作 | 3.1, 3.2 |
| Dimension Management | 维度（4.1, 4.2...）的增删改 | 3.2 |
| Question Config | 问题分析配置的增删改 | 3.2 |
| Report Generation | 报告创建、生成、导出 | 4.1, 4.2 |
| Excel Parser | Excel数据解析 | 4.1 |
| Coze Integration | 扣子5节点工作流调用 | 5.1, 5.2, 5.3 |
| Word Generator | Word文档生成 | 6.1, 6.2 |

---

## 三、数据库设计

### 3.1 实体关系图 (ERD)

```
┌──────────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│ dimension_templates  │       │     dimensions       │       │question_analysis_   │
│ ───────────────────  │       │ ───────────────────  │       │     configs          │
│ PK id                │───────│ PK id                │───────│ PK id                │
│    template_name     │  1:N  │ FK template_id       │  1:N  │ FK dimension_id      │
│    report_type       │       │    dimension_number  │       │    question_number   │
│    description       │       │    dimension_title   │       │    analysis_title    │
│    created_at        │       │    sort_order        │       │    sort_order        │
│    updated_at        │       └──────────────────────┘       └──────────────────────┘
└──────────────────────┘
           │
           │ 1:N
           ▼
┌──────────────────────┐
│       reports        │
│ ───────────────────  │
│ PK id                │
│ FK template_id       │
│    report_title      │
│    product_name      │
│    survey_region     │
│    survey_time_range │
│    sample_count      │
│    excel_data (JSON) │
│    generated_content │
│    status            │
│    created_at        │
└──────────────────────┘
```

### 3.2 表结构定义

#### 3.2.1 维度模板表 (dimension_templates)

```sql
CREATE TABLE dimension_templates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    template_name VARCHAR(100) NOT NULL COMMENT '模板名称',
    report_type ENUM('doctor', 'patient') NOT NULL COMMENT '报告类型：医生/患者',
    description TEXT COMMENT '模板描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_report_type (report_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='维度模板表';
```

#### 3.2.2 维度表 (dimensions)

```sql
CREATE TABLE dimensions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    template_id BIGINT NOT NULL COMMENT '所属模板ID',
    dimension_number VARCHAR(10) NOT NULL COMMENT '维度编号（如：4.1）',
    dimension_title VARCHAR(100) NOT NULL COMMENT '维度标题',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (template_id) REFERENCES dimension_templates(id) ON DELETE CASCADE,
    INDEX idx_template_sort (template_id, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='维度表';
```

#### 3.2.3 问题分析配置表 (question_analysis_configs)

```sql
CREATE TABLE question_analysis_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    dimension_id BIGINT NOT NULL COMMENT '所属维度ID',
    question_number INT NOT NULL COMMENT '问题编号（如：1）',
    analysis_title VARCHAR(200) NOT NULL COMMENT '分析标题',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (dimension_id) REFERENCES dimensions(id) ON DELETE CASCADE,
    UNIQUE KEY uk_dimension_question (dimension_id, question_number),
    INDEX idx_dimension_sort (dimension_id, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问题分析配置表';
```

#### 3.2.4 提示词配置表 (prompt_configs)

```sql
CREATE TABLE prompt_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    config_name VARCHAR(100) NOT NULL COMMENT '配置名称',
    report_type ENUM('doctor', 'patient') NOT NULL COMMENT '报告类型',
    section_type ENUM('preface', 'background', 'project_info', 'conclusion', 'suggestions') NOT NULL COMMENT '章节类型',
    system_prompt TEXT NOT NULL COMMENT '系统提示词',
    user_prompt_template TEXT NOT NULL COMMENT '用户提示词模板',
    temperature DECIMAL(3,2) DEFAULT 0.7 COMMENT '温度参数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_type_section (report_type, section_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提示词配置表';
```

#### 3.2.5 报告表 (reports)

```sql
CREATE TABLE reports (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    template_id BIGINT NOT NULL COMMENT '使用的维度模板ID',
    report_title VARCHAR(200) NOT NULL COMMENT '报告标题',
    product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
    survey_region VARCHAR(100) NOT NULL COMMENT '调研区域',
    survey_time_range VARCHAR(100) NOT NULL COMMENT '调研时间范围',
    sample_count INT NOT NULL COMMENT '样本数量',
    question_count INT DEFAULT 0 COMMENT '问题数量',
    excel_data JSON COMMENT '解析后的Excel数据',
    generated_content JSON COMMENT '扣子生成的各章节内容',
    status ENUM('draft', 'generating', 'completed', 'failed') DEFAULT 'draft' COMMENT '状态',
    error_message TEXT COMMENT '错误信息',
    word_file_path VARCHAR(500) COMMENT 'Word文件路径',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (template_id) REFERENCES dimension_templates(id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报告表';
```

---

## 四、API接口设计

### 4.1 RESTful API规范

- **Base URL**: `/api/v1`
- **Content-Type**: `application/json`
- **字符编码**: UTF-8

### 4.2 维度模板接口

#### 4.2.1 创建模板

```
POST /api/v1/templates
Request:
{
    "template_name": "患者问卷模板",
    "report_type": "patient",
    "description": "适用于患者用药体验调研"
}

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "template_name": "患者问卷模板",
        "report_type": "patient",
        "description": "适用于患者用药体验调研",
        "created_at": "2025-02-26T10:00:00"
    }
}
```

#### 4.2.2 获取模板列表

```
GET /api/v1/templates?page=1&page_size=20&report_type=patient

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 10,
        "page": 1,
        "page_size": 20,
        "list": [
            {
                "id": 1,
                "template_name": "患者问卷模板",
                "report_type": "patient",
                "dimension_count": 7,
                "created_at": "2025-02-26T10:00:00"
            }
        ]
    }
}
```

#### 4.2.3 获取模板详情（含维度配置）

```
GET /api/v1/templates/{template_id}

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "template_name": "患者问卷模板",
        "report_type": "patient",
        "description": "...",
        "dimensions": [
            {
                "id": 1,
                "dimension_number": "4.1",
                "dimension_title": "用药基础信息",
                "sort_order": 1,
                "questions": [
                    {
                        "id": 1,
                        "question_number": 1,
                        "analysis_title": "用药原因分析",
                        "sort_order": 1
                    }
                ]
            }
        ]
    }
}
```

#### 4.2.4 更新模板

```
PUT /api/v1/templates/{template_id}
Request:
{
    "template_name": "患者问卷模板（更新）",
    "description": "更新后的描述"
}

Response:
{
    "code": 200,
    "message": "success",
    "data": null
}
```

#### 4.2.5 删除模板

```
DELETE /api/v1/templates/{template_id}

Response:
{
    "code": 200,
    "message": "success",
    "data": null
}
```

### 4.3 维度管理接口

#### 4.3.1 添加维度

```
POST /api/v1/templates/{template_id}/dimensions
Request:
{
    "dimension_number": "4.1",
    "dimension_title": "用药基础信息",
    "sort_order": 1
}

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "dimension_number": "4.1",
        "dimension_title": "用药基础信息",
        "sort_order": 1
    }
}
```

#### 4.3.2 更新维度

```
PUT /api/v1/dimensions/{dimension_id}
Request:
{
    "dimension_number": "4.1",
    "dimension_title": "用药基础信息（更新）",
    "sort_order": 2
}
```

#### 4.3.3 删除维度

```
DELETE /api/v1/dimensions/{dimension_id}
```

### 4.4 问题配置接口

#### 4.4.1 添加问题

```
POST /api/v1/dimensions/{dimension_id}/questions
Request:
{
    "question_number": 1,
    "analysis_title": "用药原因分析",
    "sort_order": 1
}
```

#### 4.4.2 更新问题

```
PUT /api/v1/questions/{question_id}
Request:
{
    "question_number": 1,
    "analysis_title": "用药原因分析（更新）",
    "sort_order": 2
}
```

#### 4.4.3 删除问题

```
DELETE /api/v1/questions/{question_id}
```

### 4.5 报告生成接口

#### 4.5.1 创建报告

```
POST /api/v1/reports
Request:
{
    "template_id": 1,
    "report_title": "补中益气口服液调研报告",
    "product_name": "补中益气口服液",
    "survey_region": "海南省",
    "survey_time_range": "2025年10月1日-10月31日",
    "sample_count": 707,
    "question_count": 12
}

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "status": "draft",
        "created_at": "2025-02-26T10:00:00"
    }
}
```

#### 4.5.2 上传Excel并解析

```
POST /api/v1/reports/{report_id}/upload-excel
Content-Type: multipart/form-data
Request:
- file: Excel文件 (.xlsx)

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "parsed_data": {
            "question_count": 12,
            "questions": [
                {
                    "question_number": 1,
                    "question_title": "您当时是因何种症状服用...",
                    "options": [...]
                }
            ]
        }
    }
}
```

#### 4.5.3 生成报告内容（调用扣子）

```
POST /api/v1/reports/{report_id}/generate
Request:
{
    "coze_workflow_id": "workflow_xxx"  // 可选，使用默认配置
}

Response (Async):
{
    "code": 200,
    "message": "success",
    "data": {
        "report_id": 1,
        "status": "generating",
        "progress": 0
    }
}
```

#### 4.5.4 获取生成进度（流式）

```
GET /api/v1/reports/{report_id}/progress
Content-Type: text/event-stream

Event Stream:
event: progress
data: {"section": "preface", "progress": 20, "status": "processing"}

event: progress
data: {"section": "background", "progress": 40, "status": "processing"}

event: complete
data: {"progress": 100, "status": "completed"}
```

#### 4.5.5 获取报告详情

```
GET /api/v1/reports/{report_id}

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "report_title": "...",
        "status": "completed",
        "generated_content": {
            "preface": "...",
            "background": "...",
            "project_info": "...",
            "conclusion": "...",
            "suggestions": "..."
        },
        "dimensions": [...],
        "created_at": "..."
    }
}
```

#### 4.5.6 导出Word

```
GET /api/v1/reports/{report_id}/export
Response: Word文件下载 (application/vnd.openxmlformats-officedocument.wordprocessingml.document)
```

#### 4.5.7 获取报告列表

```
GET /api/v1/reports?page=1&page_size=20&status=completed

Response:
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 50,
        "page": 1,
        "page_size": 20,
        "list": [
            {
                "id": 1,
                "report_title": "补中益气口服液调研报告",
                "product_name": "补中益气口服液",
                "status": "completed",
                "created_at": "2025-02-26T10:00:00"
            }
        ]
    }
}
```

### 4.6 错误码定义

| 错误码 | 描述 | 说明 |
|--------|------|------|
| 200 | success | 请求成功 |
| 400 | bad_request | 请求参数错误 |
| 404 | not_found | 资源不存在 |
| 422 | validation_error | 数据验证失败 |
| 500 | internal_error | 服务器内部错误 |
| 501 | generate_failed | 报告生成失败 |

---

## 五、前端界面设计

### 5.1 界面风格规范

基于已生成的设计系统：

**颜色方案**:
- Primary: #6366F1 (Indigo)
- Secondary: #818CF8
- CTA: #10B981 (Emerald)
- Background: #F5F3FF (Light lavender)
- Text: #1E1B4B (Dark indigo)
- Border: #E5E7EB
- Surface: #FFFFFF

**字体**: Plus Jakarta Sans (Google Fonts)

**交互**:
- 按钮Hover: opacity变化 + color变化
- 过渡时间: 200ms ease
- 无阴影，Flat Design风格

### 5.2 页面结构

#### 5.2.1 主布局 (Main Layout)

```
┌─────────────────────────────────────────────────────────────────┐
│  Header: Logo + 用户菜单                                         │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│   Sidebar    │              Main Content                        │
│              │                                                  │
│   • 维度配置  │                                                  │
│   • 报告生成  │                                                  │
│   • 报告列表  │                                                  │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

#### 5.2.2 维度配置页面

```
┌─────────────────────────────────────────────────────────────────┐
│  报告生成工具 / 维度配置                                         │
├─────────────────────────────────────────────────────────────────┤
│  [+ 新建模板]                                                   │
│  ┌─────────────┐  ┌─────────────────────────────────────────┐  │
│  │  模板列表   │  │          维度配置详情                   │  │
│  │             │  │                                         │  │
│  │ ● 患者问卷  │  │  模板名称: [____________]               │  │
│  │ ○ 医生问卷  │  │  报告类型: [患者问卷 ▼]                 │  │
│  │             │  │  描述:    [____________]                │  │
│  │             │  │                                         │  │
│  │             │  │  ┌─────────────────────────────────┐   │  │
│  │             │  │  │ 维度 4.1: 用药基础信息           │   │  │
│  │             │  │  │ [编辑] [删除]                     │   │  │
│  │             │  │  │                                 │   │  │
│  │             │  │  │  题号 │ 分析标题                │   │  │
│  │             │  │  │  ──── │ ─────────────────────── │   │  │
│  │             │  │  │   1   │ 用药原因分析            │   │  │
│  │             │  │  │   2   │ 药品获取途径分析        │   │  │
│  │             │  │  │  [+ 添加问题]                    │   │  │
│  │             │  │  └─────────────────────────────────┘   │  │
│  │             │  │                                         │  │
│  │             │  │  [+ 添加维度]                           │  │
│  │             │  │                                         │  │
│  │             │  │  [保存模板]                             │  │
│  └─────────────┘  └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### 5.2.3 报告生成页面

```
┌─────────────────────────────────────────────────────────────────┐
│  报告生成工具 / 生成新报告                                       │
├─────────────────────────────────────────────────────────────────┤
│  Step 1        Step 2        Step 3        Step 4              │
│  ●─────────────○─────────────○─────────────○                   │
│ 选择模板      填写信息      上传Excel      生成报告             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Step 1 内容]                                                   │
│  选择维度模板:                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ○ 患者问卷模板    ○ 医生问卷模板                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  [下一步]                                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 组件清单

| 组件名称 | 类型 | 用途 |
|---------|------|------|
| Sidebar | Layout | 侧边导航栏 |
| Header | Layout | 顶部标题栏 |
| TemplateList | Data Display | 模板列表展示 |
| DimensionCard | Data Entry | 维度卡片（可展开） |
| QuestionTable | Data Display | 问题列表表格 |
| ReportWizard | Navigation | 报告生成步骤向导 |
| ExcelUploader | Data Entry | Excel上传组件 |
| ProgressBar | Feedback | 生成进度条 |
| EmptyState | Feedback | 空状态提示 |

---

## 六、扣子集成设计

### 6.1 工作流配置

根据PRD第5章，扣子工作流包含5个LLM节点：

```
开始节点
  │ 输入: report_info + dimensions
  ▼
┌─────────────────┐
│ 节点1: 生成前言  │ → 输出: preface
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ 节点2: 项目背景  │ → 输出: background
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ 节点3: 项目开展  │ → 输出: project_info
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ 节点4: 调研结果  │ → 输出: conclusion
└─────────────────┘
  │
  ▼
┌─────────────────┐
│ 节点5: 生成建议  │ → 输出: suggestions
└─────────────────┘
  │
  ▼
结束节点 → 返回所有章节内容
```

### 6.2 提示词配置

提示词存储在数据库的`prompt_configs`表中，按`report_type`和`section_type`分类。

**默认提示词**（来自PRD第5.3节）：
- 节点1-5的系统提示词和用户提示词模板
- 支持变量替换: `{{product_name}}`, `{{survey_region}}`, `{{sample_count}}`等

### 6.3 API调用封装

```python
class CozeService:
    """扣子服务封装"""
    
    async def generate_section(
        self, 
        section_type: str,
        report_data: dict,
        template_data: dict
    ) -> str:
        """生成单个章节内容"""
        pass
    
    async def generate_full_report(
        self,
        report_id: int,
        progress_callback: Callable
    ) -> dict:
        """生成完整报告，带进度回调"""
        pass
```

---

## 七、Word生成设计

### 7.1 文档结构

根据PRD第6.1节：

```
问卷调研分析报告
├── 前言（扣子生成）
├── 一、项目背景（扣子生成）
├── 二、项目开展情况（扣子生成）
├── 三、问卷说明（固定模板）
├── 四、问卷结果分析（配置+Excel数据）
│   ├── 4.1 用药基础信息
│   │   ├── 用药原因分析
│   │   │   ├── 数据表格
│   │   │   └── 数据解读（预留）
│   │   └── ...
│   └── 4.2 ...
├── 五、调研结果（扣子生成）
│   ├── 5.1 问卷重点问题分析
│   ├── 5.2 调研结果分析
│   └── 5.3 建议
├── 附件1：问卷原文
└── 附件2：免责申明
```

### 7.2 样式规范

| 元素 | 样式 |
|------|------|
| 主标题 | 18pt, 加粗, 居中 |
| 一级标题 | 16pt, 加粗 |
| 二级标题 | 14pt, 加粗 |
| 三级标题 | 12pt, 加粗 |
| 正文 | 12pt, 常规 |
| 表格 | 带边框, 表头灰色背景 |
| 字体 | Microsoft YaHei |

---

## 八、部署架构

### 8.1 目录结构

```
report-generator/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI入口
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── templates.py     # 模板API
│   │   │   ├── dimensions.py    # 维度API
│   │   │   ├── questions.py     # 问题API
│   │   │   ├── reports.py       # 报告API
│   │   │   └── coze.py          # 扣子API
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── database.py      # 数据库连接
│   │   │   └── schemas.py       # Pydantic模型
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── template_service.py
│   │   │   ├── report_service.py
│   │   │   ├── coze_service.py
│   │   │   ├── excel_service.py
│   │   │   └── word_service.py
│   │   └── utils/
│   │       └── __init__.py
│   ├── config.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── templates.html           # 维度配置页面
│   ├── report-create.html       # 报告生成页面
│   ├── reports.html             # 报告列表页面
│   ├── css/
│   │   └── main.css
│   └── js/
│       ├── api.js
│       ├── templates.js
│       └── reports.js
├── database/
│   └── init.sql                 # 数据库初始化脚本
├── docs/
│   ├── PRD.MD                   # 原始PRD文档
│   └── DESIGN.MD                # 本设计文档
└── docker-compose.yml
```

### 8.2 环境变量配置

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=report_generator
DB_USER=root
DB_PASSWORD=password

# Coze API
COZE_API_KEY=your_api_key
COZE_BASE_URL=https://api.coze.cn

# App
APP_PORT=8000
APP_HOST=0.0.0.0
DEBUG=false
```

---

## 九、验收标准

根据PRD要求，系统需满足以下验收标准：

### 9.1 功能验收

| 验收项 | 标准 | 状态 |
|--------|------|------|
| 维度模板管理 | 支持CRUD操作 | 待开发 |
| 维度配置 | 支持大标题（4.1等）+ 小标题配置 | 待开发 |
| 报告生成流程 | 选择模板 → 上传Excel → 生成Word | 待开发 |
| 扣子集成 | 5个节点依次调用，流式输出 | 待开发 |
| Word导出 | 生成符合格式要求的Word文档 | 待开发 |

### 9.2 性能验收

- Excel解析: < 5秒（1000行数据）
- 单章节生成: < 30秒
- 完整报告生成: < 3分钟
- 并发支持: 同时处理5个报告生成请求

### 9.3 非功能验收

- 数据持久化: MySQL存储，定期备份
- 日志记录: 关键操作日志（生成、导出）
- 错误处理: 优雅降级，用户友好提示

---

## 十、开发计划

### Phase 1: 基础架构 (Week 1)
- [x] 设计文档编写
- [ ] 数据库初始化
- [ ] FastAPI项目搭建
- [ ] 前端基础框架

### Phase 2: 核心功能 (Week 2)
- [ ] 维度配置模块
- [ ] Excel解析服务
- [ ] Word生成服务

### Phase 3: AI集成 (Week 3)
- [ ] 扣子API封装
- [ ] 5节点工作流
- [ ] 流式输出实现

### Phase 4: 完善优化 (Week 4)
- [ ] 前端界面优化
- [ ] 测试与修复
- [ ] 部署配置

---

**文档版本**: v1.0
**创建时间**: 2025-02-26
**最后更新**: 2025-02-26
