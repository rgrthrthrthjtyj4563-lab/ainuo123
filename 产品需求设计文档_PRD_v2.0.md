# 报告生成工具 - 产品需求设计文档 (PRD)

**文档版本**: v2.0  
**创建日期**: 2026-03-02  
**文档状态**: 正式版  
**适用范围**: 报告生成工具 v2.0

---

## 目录

1. [文档概述](#一文档概述)
2. [产品背景与目标](#二产品背景与目标)
3. [产品范围](#三产品范围)
4. [用户角色与场景](#四用户角色与场景)
5. [功能需求](#五功能需求)
6. [非功能需求](#六非功能需求)
7. [数据模型](#七数据模型)
8. [接口设计](#八接口设计)
9. [界面设计](#九界面设计)
10. [系统集成](#十系统集成)
11. [实施计划](#十一实施计划)
12. [附录](#十二附录)

---

## 一、文档概述

### 1.1 文档目的

本文档详细描述了"报告生成工具"的产品需求,包括功能规格、用户场景、数据模型、接口规范、界面设计等内容,为开发团队、测试团队和相关干系人提供明确的产品实现指导。

### 1.2 读者对象

| 角色 | 关注重点 |
|------|----------|
| 产品经理 | 功能完整性、用户体验 |
| 开发工程师 | 技术实现、数据模型、接口规范 |
| 测试工程师 | 验收标准、测试场景 |
| 运维工程师 | 部署架构、性能要求 |
| 项目经理 | 进度规划、风险管控 |

### 1.3 术语定义

| 术语 | 定义 |
|------|------|
| **维度模板** | 定义报告第四章"问卷结果分析"的结构配置,包含大维度(4.1/4.2等)和小分析标题 |
| **报告结构** | 完整的报告章节树形结构,包含所有章节和数据分析节点 |
| **节点类型** | 报告结构中的内容单元类型: AI生成章节、固定内容、章节分组、数据分析 |
| **扣子API** | 字节跳动旗下AI能力平台,提供大语言模型服务 |
| **Excel解析** | 将问卷统计数据的Excel文件解析为结构化数据 |
| **Word导出** | 使用python-docx库生成符合格式要求的Word文档 |

### 1.4 参考文档

- 设计系统规范: `/design-system/报告生成工具/MASTER.md`
- 系统架构设计: `/docs/DESIGN.md`
- 历史PRD文档: `prd2.md`, `prd3.md`, `prd4.md`

---

## 二、产品背景与目标

### 2.1 背景

在医药市场调研领域,问卷调研分析报告是了解产品市场表现、用户反馈的重要工具。传统报告撰写流程存在以下痛点:

1. **人工撰写效率低**: 一份专业报告需要2-3天人工撰写
2. **格式不统一**: 不同撰写人产出的报告格式差异大
3. **数据整理繁琐**: Excel数据需要手动整理成表格和图表
4. **重复劳动**: 相似结构的报告需要重复配置
5. **质量不稳定**: 人工撰写质量依赖个人经验

### 2.2 目标

构建一个智能化的问卷调研报告生成系统,实现:

| 指标 | 现状 | 目标 | 提升幅度 |
|------|------|------|----------|
| 报告生成时间 | 2-3天 | < 10分钟 | 99%↓ |
| 格式一致性 | 低 | 100%标准化 | 显著提升 |
| 数据整理时间 | 4-6小时 | 自动完成 | 100%↓ |
| 结构配置时间 | 30分钟 | 5分钟 | 83%↓ |

### 2.3 核心价值主张

**"5分钟生成专业问卷调研报告"**

- **快**: 上传Excel即可自动生成完整报告
- **准**: AI智能分析数据,生成专业洞察
- **美**: 标准化Word格式,可直接交付
- **易**: 可视化配置,无需技术背景

---

## 三、产品范围

### 3.1 功能边界

**包含功能**:

✅ **报告结构配置**
- Word模板智能提取结构
- 可视化节点编辑(拖拽、调整层级)
- 节点类型管理(AI章节/固定内容/数据分析)
- 题号映射配置
- 图表配置(饼图/柱状图/条形图/雷达图)

✅ **维度模板管理**
- 模板CRUD操作
- 维度(大标题)管理
- 问题分析配置(小标题+题号)

✅ **报告生成**
- 报告创建与信息管理
- Excel数据解析
- AI内容生成(扣子API 5节点工作流)
- 生成进度实时推送(SSE)
- Word文档导出

✅ **报告管理**
- 报告列表与搜索
- 报告详情查看
- 在线预览与下载

**不包含功能**(未来版本规划):

❌ 用户权限管理系统(RBAC)  
❌ 报告版本历史  
❌ 多人协作编辑  
❌ 自定义图表样式  
❌ Excel模板智能匹配  
❌ 数据可视化看板  

### 3.2 技术边界

**支持格式**:
- Word: `.docx` (仅支持标准格式,暂不支持.doc)
- Excel: `.xlsx` (暂不支持.xls)
- 输出: `.docx`

**支持报告类型**:
- 医生问卷报告
- 患者问卷报告

**AI能力边界**:
- 依赖扣子API服务可用性
- 生成内容需人工审核
- 不支持实时联网查询

---

## 四、用户角色与场景

### 4.1 用户角色

#### 4.1.1 系统管理员

**特征**: 熟悉报告结构,负责配置模板

**主要职责**:
- 创建和维护维度模板
- 配置报告结构(章节、维度、分析节点)
- 管理提示词配置
- 监控系统运行状态

**使用频率**: 低频次,每次调研项目前配置一次

#### 4.1.2 报告生成员

**特征**: 实际使用系统生成报告的业务人员

**主要职责**:
- 选择已有模板生成报告
- 填写报告基本信息
- 上传Excel数据
- 导出并交付Word报告

**使用频率**: 高频次,每周生成多份报告

### 4.2 用户故事

#### 故事1: 配置报告结构

**作为** 系统管理员  
**我希望** 通过上传Word模板自动生成报告结构  
**以便** 快速配置不同格式的报告模板,无需手动创建每个节点

**验收标准**:
- 支持上传Word文档自动提取标题层级
- AI自动识别节点类型(AI生成/固定内容/数据分析)
- 显示识别置信度,低置信度节点需人工确认
- 支持可视化调整节点层级和顺序
- 支持配置题号映射和图表类型

#### 故事2: 生成报告

**作为** 报告生成员  
**我希望** 选择模板后上传Excel自动生成Word报告  
**以便** 快速产出标准化的调研分析报告

**验收标准**:
- 可选择已配置的模板
- 填写报告基本信息(标题、产品、区域等)
- 上传Excel自动解析并匹配到对应题目
- AI自动生成5个章节内容(前言、背景、开展、结果、建议)
- 实时显示生成进度
- 导出符合格式要求的Word文档

#### 故事3: 管理模板复用

**作为** 系统管理员  
**我希望** 提取的模板结构可以被复用  
**以便** 相似报告无需重复配置

**验收标准**:
- 提取的模板可保存到模板库
- 支持基于已有模板创建新模板(复制并修改)
- 显示模板使用次数和成功率统计

---

## 五、功能需求

### 5.1 报告结构配置模块

#### 5.1.1 Word模板智能提取

**功能描述**: 上传Word格式的参考报告,系统自动提取章节结构

**输入**:
- Word文件(.docx)
- 模板类型(医生/患者)

**处理流程**:

```
上传Word文件
    │
    ▼
解析文档结构
    ├── 提取标题层级(Heading 1/2/3)
    ├── 提取内容预览(前300字)
    └── 构建树形结构
    │
    ▼
AI节点分类
    ├── 规则引擎快速分类(高置信度)
    ├── LLM辅助识别(低置信度)
    └── 输出节点类型推荐
    │
    ▼
可视化预览
    ├── 展示树形结构
    ├── 标注节点类型
    ├── 显示置信度
    └── 高亮待确认节点
```

**输出**:
- 提取的结构树(JSON)
- 整体置信度分数
- 低置信度节点列表

**异常处理**:
- 格式不规范: 提供格式指南,尽可能容错提取
- 提取失败: 提供手动配置入口

#### 5.1.2 节点类型定义

| 节点类型 | 代码值 | 说明 | 典型示例 |
|----------|--------|------|----------|
| AI生成章节 | `ai_chapter` | 内容由AI大模型生成 | 前言、项目背景、结论、建议 |
| 固定内容 | `fixed_content` | 固定不变的文本内容 | 问卷说明、免责声明 |
| 章节分组 | `container` | 用于组织子章节的父级节点 | 四、问卷结果分析 |
| 数据分析 | `data_analysis` | 展示数据表格和图表 | 4.1用药基础信息、用药原因分析 |

#### 5.1.3 可视化结构编辑

**功能点**:

1. **树形结构展示**
   - 层级缩进显示
   - 可折叠/展开子节点
   - 节点类型图标标识
   - 置信度可视化(颜色/标签)

2. **拖拽调整**
   - 支持拖拽调整节点顺序
   - 支持拖拽改变节点层级
   - 实时预览调整结果

3. **节点编辑**
   - 修改节点标题
   - 修改节点类型
   - 配置题号映射(数据分析节点)
   - 配置图表类型和展示顺序
   - 编辑固定内容文本

4. **批量操作**
   - 批量导入题号映射
   - 批量设置图表配置
   - 一键重置为默认结构

#### 5.1.4 图表配置

**支持的图表类型**:

| 图表类型 | 适用场景 | 限制条件 |
|----------|----------|----------|
| 饼图 | 占比分布 | 选项≤5个时效果最佳 |
| 柱状图 | 横向对比 | 选项≥3个时使用 |
| 条形图 | 标签较长的选项 | 纵向展示,适合长文本选项 |
| 雷达图 | 多维度综合评价 | 需3个以上维度 |

**配置项**:
- 图表类型多选(可多选多个图表)
- 图表展示顺序
- 内容展示顺序(图表/表格/AI解读)

#### 5.1.5 结构保存与复用

**功能点**:

1. **保存结构**
   - 命名结构配置
   - 选择报告类型
   - 保存为可复用模板

2. **模板复用**
   - 查看可复用模板列表
   - 基于模板创建新报告
   - 复制并修改现有模板

3. **模板管理**
   - 查看模板使用统计
   - 删除/归档旧模板
   - 导出/导入模板配置(JSON)

### 5.2 维度模板管理模块

#### 5.2.1 模板CRUD

**功能点**:

1. **创建模板**
   - 模板名称
   - 报告类型(医生/患者)
   - 描述信息
   - 批量添加维度和问题

2. **查询模板**
   - 列表分页查询
   - 按报告类型筛选
   - 查看维度数量统计

3. **更新模板**
   - 修改基本信息
   - 启用/禁用模板

4. **删除模板**
   - 软删除(保留历史报告关联)
   - 硬删除(彻底删除)

#### 5.2.2 维度管理

**功能点**:

1. **添加维度**
   - 维度编号(如: 4.1)
   - 维度标题(如: 用药基础信息)
   - 排序序号

2. **编辑维度**
   - 修改维度编号和标题
   - 调整排序

3. **删除维度**
   - 级联删除关联问题

#### 5.2.3 问题分析配置

**功能点**:

1. **添加问题**
   - 题号(对应Excel列)
   - 分析标题(如: 用药原因分析)
   - 排序序号

2. **编辑问题**
   - 修改题号和标题

3. **删除问题**
   - 单条删除

### 5.3 报告生成模块

#### 5.3.1 报告创建流程

**步骤1: 选择模板**
- 下拉选择已有模板
- 显示模板详情预览
- 支持搜索和筛选

**步骤2: 填写报告信息**
- 报告标题
- 产品名称
- 调研区域
- 调研时间范围
- 样本数量
- 问题数量

**步骤3: 上传Excel**
- 拖拽或点击上传
- 实时解析预览
- 显示解析结果统计
- 题号匹配检查(提示未匹配题目)

**步骤4: 生成报告**
- 确认信息无误后提交生成
- 显示生成进度(SSE流式推送)
- 生成完成通知

#### 5.3.2 Excel解析

**支持的Excel格式**:

```
问卷数据表结构:
├── 题目列: 题号、题目文本、选项A/B/C/D...、样本量、占比...
└── 数据行: 每道题的统计数据
```

**解析规则**:
- 自动识别题号列
- 提取题目文本和选项
- 解析样本量和百分比
- 支持多sheet(默认读取第一个)

**数据映射**:
- 根据结构配置中的题号映射
- 自动匹配到对应分析节点
- 未匹配题目给出警告提示

#### 5.3.3 AI内容生成

**扣子工作流(5节点)**:

```
开始节点
    │ 输入: report_info + dimensions
    ▼
┌─────────────────┐
│ 节点1: 生成前言  │ → 400-500字
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 节点2: 项目背景  │ → 300-400字
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 节点3: 项目开展  │ → 100-150字(固定格式)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 节点4: 调研结果  │ → 500-600字(含重点问题分析)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 节点5: 生成建议  │ → 300-400字(3点建议)
└─────────────────┘
    │
    ▼
结束节点
```

**提示词配置**:
- 系统提示词定义写作风格和要求
- 用户提示词模板支持变量替换
- 按报告类型和章节类型分别配置

**变量替换**:
- `{{product_name}}` - 产品名称
- `{{survey_region}}` - 调研区域
- `{{survey_time_range}}` - 调研时间
- `{{sample_count}}` - 样本数量
- `{{question_count}}` - 问题数量
- `{{dimensions_data}}` - 维度汇总数据

#### 5.3.4 生成进度推送

**实现方式**: Server-Sent Events (SSE)

**事件类型**:

```json
// 进度更新事件
event: progress
data: {
  "section": "preface",
  "section_name": "前言",
  "progress": 20,
  "status": "processing",
  "message": "正在生成前言..."
}

// 完成事件
event: complete
data: {
  "progress": 100,
  "status": "completed",
  "report_id": 123,
  "download_url": "/api/v1/reports/123/export"
}

// 错误事件
event: error
data: {
  "status": "failed",
  "error_code": "GENERATE_FAILED",
  "message": "AI服务调用失败"
}
```

#### 5.3.5 Word文档生成

**报告结构**:

```
问卷调研分析报告
├── 前言 (AI生成)
├── 一、项目背景 (AI生成)
├── 二、项目开展情况 (AI生成)
├── 三、问卷说明 (固定模板)
├── 四、问卷结果分析 (配置+Excel数据)
│   ├── 4.1 用药基础信息 (维度大标题)
│   │   ├── 用药原因分析 (小分析标题)
│   │   │   ├── 数据图表 (可选:饼图/柱状图等)
│   │   │   ├── 数据表格 (Excel数据)
│   │   │   └── AI解读 (可选)
│   │   └── 药品获取途径分析
│   │       └── ...
│   ├── 4.2 用药行为与习惯
│   └── ...
├── 五、调研结果 (AI生成)
│   ├── 5.1 问卷重点问题分析
│   ├── 5.2 调研结果分析
│   └── 5.3 建议
├── 附件1: 问卷原文 (Excel问题列表)
└── 附件2: 免责声明 (固定模板)
```

**样式规范**:

| 元素 | 样式 |
|------|------|
| 报告标题 | 18pt, 加粗, 居中 |
| 一级标题 | 16pt, 加粗 |
| 二级标题 | 14pt, 加粗 |
| 三级标题 | 12pt, 加粗 |
| 正文 | 12pt, 常规 |
| 表格 | 带边框, 表头灰色背景 |
| 字体 | Microsoft YaHei |

**图表生成**:
- 使用matplotlib生成图表
- 支持饼图、柱状图、条形图、雷达图
- 临时文件方式,生成后自动清理

### 5.4 报告管理模块

#### 5.4.1 报告列表

**功能点**:
- 分页展示报告列表
- 按状态筛选(草稿/生成中/已完成/失败)
- 按时间范围筛选
- 搜索报告标题
- 显示关键信息(标题、产品、状态、创建时间)

#### 5.4.2 报告详情

**功能点**:
- 显示报告基本信息
- 显示生成内容预览
- 显示使用的模板和结构
- 显示Excel数据概览
- 操作按钮(重新生成/导出Word/删除)

#### 5.4.3 报告导出

**功能点**:
- 导出Word文档(.docx)
- 下载文件命名规范: `{报告标题}_{日期}.docx`
- 支持在线预览(可选)

---

## 六、非功能需求

### 6.1 性能需求

| 场景 | 性能指标 | 备注 |
|------|----------|------|
| Excel解析 | < 5秒 | 1000行数据 |
| Word结构提取 | < 10秒 | 50页文档 |
| 单章节AI生成 | < 30秒 | 扣子API响应时间 |
| 完整报告生成 | < 3分钟 | 5个章节串行生成 |
| 报告列表查询 | < 500ms | 单页20条 |
| Word导出 | < 10秒 | 含图表生成 |
| 并发支持 | 5个同时生成 | 超过则排队 |

### 6.2 可用性需求

| 指标 | 目标值 |
|------|--------|
| 系统可用性 | 99.5% (排除AI服务不可用时段) |
| 数据持久化 | 100%, 零数据丢失 |
| 恢复时间 | < 30分钟 |

### 6.3 安全需求

1. **数据安全**
   - 敏感配置信息(如API密钥)环境变量存储
   - 数据库连接加密
   - 用户上传文件隔离存储

2. **访问安全**
   - API接口CORS限制
   - 文件上传类型限制(.xlsx, .docx)
   - 文件大小限制(Excel < 10MB, Word < 50MB)

3. **日志审计**
   - 关键操作记录(生成、导出、删除)
   - 错误日志记录
   - 保留30天日志

### 6.4 兼容性需求

| 维度 | 要求 |
|------|------|
| 浏览器 | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |
| 移动端 | 支持响应式,主要功能可用(管理功能建议PC端) |
| Word版本 | 支持Microsoft Word 2016+ |
| Excel版本 | 支持Microsoft Excel 2016+ |

### 6.5 扩展性需求

1. **水平扩展**
   - 无状态服务设计,支持多实例部署
   - 数据库读写分离预留

2. **功能扩展**
   - 预留新节点类型扩展接口
   - 预留新图表类型扩展接口

3. **国际化预留**
   - 文案抽离,便于多语言切换
   - 时区处理

---

## 七、数据模型

### 7.1 实体关系图

```
┌──────────────────────┐       ┌──────────────────────┐
│   report_structures  │       │ template_extractions │
│   (报告结构配置表)    │       │   (模板提取记录表)    │
├──────────────────────┤       ├──────────────────────┤
│ PK id                │       │ PK id                │
│    structure_name    │       │    file_hash         │
│    report_type       │       │    extracted_data    │
│    is_active         │       │    confidence        │
└──────────┬───────────┘       └──────────────────────┘
           │
           │ 1:N
           ▼
┌──────────────────────┐
│    structure_nodes   │
│   (结构节点表)        │
├──────────────────────┤
│ PK id                │
│ FK structure_id      │
│    parent_id         │ (自关联,支持树形)
│    level             │ (1=章, 2=节, 3=小节)
│    node_type         │ (ai_chapter/fixed_content/
│    title             │  container/data_analysis)
│    sort_order        │
│    question_number   │ (题号映射)
│    charts            │ (图表配置JSON)
│    content_order     │ (内容顺序JSON)
│    show_data_table   │
│    show_ai_interp    │
│    fixed_content     │
│    ai_recommended    │
│    confidence_score  │
└──────────────────────┘

┌──────────────────────┐       ┌──────────────────────┐
│ dimension_templates  │       │      dimensions      │
│   (维度模板表)        │       │     (维度表)          │
├──────────────────────┤       ├──────────────────────┤
│ PK id                │───┐   │ PK id                │
│    template_name     │   │   │ FK template_id       │
│    report_type       │   └──<│    dimension_number  │
│    description       │       │    dimension_title   │
│    is_active         │       │    sort_order        │
└──────────────────────┘       └──────────┬───────────┘
                                          │
                                          │ 1:N
                                          ▼
                              ┌──────────────────────┐
                              │question_analysis_    │
                              │     configs          │
                              │  (问题分析配置表)     │
                              ├──────────────────────┤
                              │ PK id                │
                              │ FK dimension_id      │
                              │    question_number   │
                              │    analysis_title    │
                              │    sort_order        │
                              └──────────────────────┘

┌──────────────────────┐
│       reports        │
│      (报告表)         │
├──────────────────────┤
│ PK id                │
│ FK template_id       │
│ FK structure_id      │ (新版结构)
│    report_title      │
│    product_name      │
│    survey_region     │
│    survey_time_range │
│    sample_count      │
│    question_count    │
│    excel_data        │ (JSON)
│    generated_content │ (JSON)
│    status            │
│    word_file_path    │
└──────────────────────┘
```

### 7.2 核心表结构

#### 7.2.1 报告结构表 (report_structures)

```sql
CREATE TABLE report_structures (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    structure_name VARCHAR(100) NOT NULL COMMENT '结构名称',
    report_type ENUM('doctor', 'patient') NOT NULL COMMENT '报告类型',
    description TEXT COMMENT '结构描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_report_type (report_type)
) ENGINE=InnoDB COMMENT='报告结构配置表';
```

#### 7.2.2 结构节点表 (structure_nodes)

```sql
CREATE TABLE structure_nodes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    structure_id BIGINT NOT NULL COMMENT '所属结构ID',
    parent_id BIGINT COMMENT '父节点ID',
    level TINYINT NOT NULL COMMENT '层级:1=章,2=节,3=小节',
    node_type ENUM('ai_chapter', 'fixed_content', 'container', 'data_analysis') NOT NULL,
    title VARCHAR(200) NOT NULL COMMENT '节点标题',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    question_number INT COMMENT '关联题号',
    charts JSON DEFAULT '[]' COMMENT '图表配置数组',
    content_order JSON DEFAULT '["table"]' COMMENT '内容展示顺序',
    show_data_table BOOLEAN DEFAULT TRUE COMMENT '显示数据表格',
    show_ai_interpretation BOOLEAN DEFAULT FALSE COMMENT '显示AI解读',
    fixed_content TEXT COMMENT '固定内容(固定内容节点使用)',
    ai_recommended BOOLEAN DEFAULT FALSE COMMENT '是否AI推荐',
    confidence_score DECIMAL(3,2) COMMENT 'AI置信度',
    recommendation_reason TEXT COMMENT '推荐理由',
    modified_by_user BOOLEAN DEFAULT FALSE COMMENT '是否被用户修改',
    original_title VARCHAR(200) COMMENT 'AI推荐的原标题',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (structure_id) REFERENCES report_structures(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES structure_nodes(id) ON DELETE CASCADE,
    INDEX idx_structure_level (structure_id, level, sort_order)
) ENGINE=InnoDB COMMENT='结构节点表';
```

#### 7.2.3 模板提取记录表 (template_extractions)

```sql
CREATE TABLE template_extractions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    original_filename VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_hash VARCHAR(64) NOT NULL UNIQUE COMMENT '文件MD5哈希',
    file_size INT COMMENT '文件大小(字节)',
    template_type ENUM('doctor', 'patient') NOT NULL,
    extracted_structure JSON NOT NULL COMMENT '提取的节点树JSON',
    confidence_scores JSON COMMENT '各节点置信度',
    overall_confidence DECIMAL(3,2) COMMENT '整体置信度',
    status ENUM('processing', 'completed', 'failed') DEFAULT 'processing',
    error_message TEXT COMMENT '错误信息',
    final_structure_id BIGINT COMMENT '确认后创建的structure_id',
    user_modifications JSON COMMENT '用户修改记录',
    is_reusable BOOLEAN DEFAULT TRUE COMMENT '是否可复用',
    use_count INT DEFAULT 0 COMMENT '被使用次数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_file_hash (file_hash),
    INDEX idx_template_type (template_type)
) ENGINE=InnoDB COMMENT='Word模板提取记录表';
```

#### 7.2.4 维度模板表 (dimension_templates)

```sql
CREATE TABLE dimension_templates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    template_name VARCHAR(100) NOT NULL COMMENT '模板名称',
    report_type ENUM('doctor', 'patient') NOT NULL COMMENT '报告类型',
    description TEXT COMMENT '模板描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_report_type (report_type)
) ENGINE=InnoDB COMMENT='维度模板表';
```

#### 7.2.5 维度表 (dimensions)

```sql
CREATE TABLE dimensions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    template_id BIGINT NOT NULL COMMENT '所属模板ID',
    dimension_number VARCHAR(10) NOT NULL COMMENT '维度编号(如:4.1)',
    dimension_title VARCHAR(100) NOT NULL COMMENT '维度标题',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES dimension_templates(id) ON DELETE CASCADE,
    INDEX idx_template_sort (template_id, sort_order)
) ENGINE=InnoDB COMMENT='维度表';
```

#### 7.2.6 问题分析配置表 (question_analysis_configs)

```sql
CREATE TABLE question_analysis_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    dimension_id BIGINT NOT NULL COMMENT '所属维度ID',
    question_number INT NOT NULL COMMENT '问题编号',
    analysis_title VARCHAR(200) NOT NULL COMMENT '分析标题',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dimension_id) REFERENCES dimensions(id) ON DELETE CASCADE,
    UNIQUE KEY uk_dimension_question (dimension_id, question_number),
    INDEX idx_dimension_sort (dimension_id, sort_order)
) ENGINE=InnoDB COMMENT='问题分析配置表';
```

#### 7.2.7 提示词配置表 (prompt_configs)

```sql
CREATE TABLE prompt_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    config_name VARCHAR(100) NOT NULL COMMENT '配置名称',
    report_type ENUM('doctor', 'patient') NOT NULL,
    section_type ENUM('preface', 'background', 'project_info', 'conclusion', 'suggestions') NOT NULL COMMENT '章节类型',
    system_prompt TEXT NOT NULL COMMENT '系统提示词',
    user_prompt_template TEXT NOT NULL COMMENT '用户提示词模板',
    temperature DECIMAL(3,2) DEFAULT 0.7 COMMENT '温度参数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_type_section (report_type, section_type)
) ENGINE=InnoDB COMMENT='提示词配置表';
```

#### 7.2.8 报告表 (reports)

```sql
CREATE TABLE reports (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    template_id BIGINT NOT NULL COMMENT '使用的维度模板ID(旧版)',
    structure_id BIGINT COMMENT '使用的报告结构ID(新版)',
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES dimension_templates(id),
    FOREIGN KEY (structure_id) REFERENCES report_structures(id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB COMMENT='报告表';
```

---

## 八、接口设计

### 8.1 接口规范

**基础信息**:
- Base URL: `/api/v1`
- Content-Type: `application/json`
- 字符编码: UTF-8
- 认证方式: 暂不需要(内网系统)

**响应格式**:

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**错误码定义**:

| 错误码 | 描述 | HTTP状态码 |
|--------|------|------------|
| 200 | success | 200 |
| 400 | bad_request | 400 |
| 404 | not_found | 404 |
| 422 | validation_error | 422 |
| 500 | internal_error | 500 |
| 501 | generate_failed | 500 |
| 502 | ai_service_error | 502 |

### 8.2 报告结构配置接口

#### 8.2.1 上传Word并提取结构

```http
POST /templates/extract
Content-Type: multipart/form-data

Request:
  - template_type: string (required) ["doctor", "patient"]
  - word_file: file (required) [.docx]

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "extraction_id": 123,
    "template_type": "doctor",
    "overall_confidence": 0.88,
    "structure_tree": [
      {
        "title": "前言",
        "level": 1,
        "node_type": "ai_chapter",
        "confidence": 0.92,
        "reasoning": "标题匹配AI章节规则",
        "children": []
      },
      {
        "title": "四、问卷结果分析",
        "level": 1,
        "node_type": "container",
        "confidence": 0.85,
        "children": [
          {
            "title": "4.1 用药基础信息",
            "level": 2,
            "node_type": "data_analysis",
            "confidence": 0.90,
            "settings": {
              "show_data_table": true,
              "show_ai_interpretation": false
            }
          }
        ]
      }
    ],
    "low_confidence_nodes": [...]
  }
}
```

#### 8.2.2 确认并保存结构

```http
POST /templates/extractions/{extraction_id}/confirm
Content-Type: application/json

Request:
{
  "structure_name": "医生问卷标准结构",
  "modified_nodes": [
    {
      "path": "/六、建议",
      "changes": {
        "node_type": "ai_chapter",
        "title": "六、结论与建议"
      }
    }
  ],
  "question_mappings": [
    {
      "node_path": "/四、问卷结果分析/4.1 用药基础信息",
      "question_numbers": [1, 2, 3]
    }
  ]
}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "structure_id": 456,
    "structure_name": "医生问卷标准结构",
    "node_count": 15,
    "created_at": "2026-02-27T10:30:00Z"
  }
}
```

#### 8.2.3 获取结构列表

```http
GET /structures?page=1&page_size=20&report_type=doctor&is_active=true

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
        "structure_name": "患者问卷标准结构",
        "report_type": "patient",
        "is_active": true,
        "node_count": 25,
        "created_at": "2026-02-20T08:00:00Z"
      }
    ]
  }
}
```

#### 8.2.4 获取结构详情

```http
GET /structures/{structure_id}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "structure_name": "患者问卷标准结构",
    "report_type": "patient",
    "nodes": [
      {
        "id": 1,
        "title": "前言",
        "level": 1,
        "node_type": "ai_chapter",
        "sort_order": 1,
        "children": []
      }
    ]
  }
}
```

#### 8.2.5 更新结构节点

```http
PUT /structures/nodes/{node_id}
Content-Type: application/json

Request:
{
  "title": "用药原因分析",
  "node_type": "data_analysis",
  "question_number": 1,
  "charts": [
    {"chart_type": "pie", "sort_order": 1},
    {"chart_type": "bar", "sort_order": 2}
  ],
  "content_order": ["chart", "table", "interpretation"],
  "show_data_table": true,
  "show_ai_interpretation": false
}

Response:
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

#### 8.2.6 获取可复用模板列表

```http
GET /templates/reusable?template_type=doctor&page=1&page_size=20

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 10,
    "list": [
      {
        "extraction_id": 123,
        "original_filename": "医生问卷模板-湖南省.docx",
        "template_type": "doctor",
        "overall_confidence": 0.88,
        "use_count": 5,
        "created_at": "2026-02-20T08:00:00Z"
      }
    ]
  }
}
```

### 8.3 维度模板接口

#### 8.3.1 创建模板

```http
POST /templates
Content-Type: application/json

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
    "created_at": "2025-02-26T10:00:00"
  }
}
```

#### 8.3.2 获取模板列表

```http
GET /templates?page=1&page_size=20&report_type=patient
```

#### 8.3.3 获取模板详情

```http
GET /templates/{template_id}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "template_name": "患者问卷模板",
    "report_type": "patient",
    "dimensions": [
      {
        "id": 1,
        "dimension_number": "4.1",
        "dimension_title": "用药基础信息",
        "questions": [
          {
            "id": 1,
            "question_number": 1,
            "analysis_title": "用药原因分析"
          }
        ]
      }
    ]
  }
}
```

#### 8.3.4 添加维度

```http
POST /templates/{template_id}/dimensions
Content-Type: application/json

Request:
{
  "dimension_number": "4.1",
  "dimension_title": "用药基础信息",
  "sort_order": 1
}
```

#### 8.3.5 更新维度

```http
PUT /dimensions/{dimension_id}
Content-Type: application/json

Request:
{
  "dimension_number": "4.1",
  "dimension_title": "用药基础信息",
  "sort_order": 1
}
```

#### 8.3.6 添加问题

```http
POST /dimensions/{dimension_id}/questions
Content-Type: application/json

Request:
{
  "question_number": 1,
  "analysis_title": "用药原因分析",
  "sort_order": 1
}
```

### 8.4 报告生成接口

#### 8.4.1 创建报告

```http
POST /reports
Content-Type: application/json

Request:
{
  "template_id": 1,
  "structure_id": 1,
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

#### 8.4.2 上传Excel

```http
POST /reports/{report_id}/upload-excel
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
      "questions": [...]
    },
    "matched_count": 10,
    "unmatched_questions": [11, 12]
  }
}
```

#### 8.4.3 生成报告

```http
POST /reports/{report_id}/generate
Content-Type: application/json

Request:
{
  "coze_workflow_id": "workflow_xxx"  // 可选
}

Response:
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

#### 8.4.4 获取生成进度(SSE)

```http
GET /reports/{report_id}/progress
Accept: text/event-stream

Response Stream:
event: progress
data: {"section": "preface", "section_name": "前言", "progress": 20, "status": "processing"}

event: progress
data: {"section": "background", "section_name": "项目背景", "progress": 40, "status": "processing"}

event: complete
data: {"progress": 100, "status": "completed", "download_url": "/api/v1/reports/1/export"}
```

#### 8.4.5 获取报告详情

```http
GET /reports/{report_id}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "report_title": "...",
    "status": "completed",
    "generated_content": {
      "nodes": [...]
    },
    "created_at": "..."
  }
}
```

#### 8.4.6 导出Word

```http
GET /reports/{report_id}/export

Response:
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="报告标题_20250302.docx"
```

#### 8.4.7 获取报告列表

```http
GET /reports?page=1&page_size=20&status=completed

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

---

## 九、界面设计

### 9.1 设计系统规范

**颜色方案**:

| 角色 | 色值 | 用途 |
|------|------|------|
| Primary | `#6366F1` | 主品牌色、链接、按钮 |
| Secondary | `#818CF8` | 辅助色、hover状态 |
| CTA/Accent | `#10B981` | 成功状态、主要操作按钮 |
| Background | `#F5F3FF` | 页面背景 |
| Text | `#1E1B4B` | 主要文字 |
| Border | `#E5E7EB` | 边框、分割线 |

**字体**:
- 主字体: Plus Jakarta Sans
- 备选: system-ui, sans-serif

**间距规范**:

| Token | 值 | 用途 |
|-------|-----|------|
| xs | 4px | 紧凑间距 |
| sm | 8px | 图标间隙 |
| md | 16px | 标准内边距 |
| lg | 24px | 区块内边距 |
| xl | 32px | 大间隙 |

**圆角规范**:
- 小元素: 6px
- 按钮/输入框: 8px
- 卡片: 12px
- 模态框: 16px

### 9.2 页面结构

#### 9.2.1 主布局

```
┌─────────────────────────────────────────────────────────────────┐
│  Header: Logo + 版本信息 + 用户菜单                               │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│   Sidebar    │              Main Content                        │
│              │                                                  │
│   • 首页     │                                                  │
│   • 报告结构配置                                               │
│   • 报告管理                                                   │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

#### 9.2.2 首页

**内容**:
- 欢迎标题
- 统计卡片(模板数、报告数、生成中)
- 快速操作入口(生成新报告、配置报告结构)

#### 9.2.3 报告结构配置页

**三栏布局**:

```
┌──────────────────┬──────────────────┬──────────────────┐
│   结构列表        │   结构树预览      │   节点编辑/预览   │
│                  │                  │                  │
│ • 患者问卷标准   │   ☰ 前言         │  节点属性:       │
│ • 医生问卷标准   │   ☰ 一、项目背景  │  - 标题          │
│                  │   ▼ 四、问卷分析  │  - 类型          │
│ [+ 新建结构]     │     ├─ 4.1 用药   │  - 题号          │
│                  │     └─ 4.2 行为   │  - 图表配置      │
│                  │   ☰ 五、调研结果  │                  │
│                  │                  │  [保存修改]      │
└──────────────────┴──────────────────┴──────────────────┘
```

**功能**:
- 左侧: 结构列表,支持搜索
- 中间: 树形结构展示,支持拖拽、折叠/展开
- 右侧: 选中节点的编辑面板

#### 9.2.4 报告生成页

**步骤向导**:

```
Step 1          Step 2          Step 3          Step 4
●───────────────○───────────────○───────────────○
选择模板        填写信息        上传Excel       生成报告

[内容区域]
```

**各步骤内容**:

1. **选择模板**: 卡片式选择结构模板,显示预览信息
2. **填写信息**: 表单输入报告基本信息
3. **上传Excel**: 拖拽上传区域,解析结果预览
4. **生成报告**: 进度展示,生成结果预览

#### 9.2.5 报告列表页

**内容**:
- 搜索栏
- 筛选器(状态、时间范围)
- 表格列表(标题、产品、状态、创建时间、操作)
- 分页器

### 9.3 关键组件

#### 9.3.1 结构树组件

**特性**:
- 递归渲染树形结构
- 拖拽手柄(☰)
- 展开/折叠按钮(▼/▶)
- 节点类型图标
- 置信度指示(低置信度黄色警告)
- 右键菜单(编辑/删除/添加子节点)

#### 9.3.2 节点编辑面板

**表单字段**:
- 节点标题(输入框)
- 节点类型(下拉选择)
- 题号映射(数字输入,数据分析节点显示)
- 图表配置(多选框+排序,数据分析节点显示)
- 内容顺序(下拉选择,数据分析节点显示)
- 固定内容(文本域,固定内容节点显示)

#### 9.3.3 Excel上传组件

**特性**:
- 拖拽上传区域
- 文件类型验证
- 上传进度条
- 解析结果统计
- 题号匹配状态(绿色=匹配,红色=未匹配)

#### 9.3.4 进度推送组件

**特性**:
- 实时进度条
- 当前步骤文字说明
- 已完成的步骤打勾
- 错误状态红色提示
- 完成后显示下载按钮

---

## 十、系统集成

### 10.1 扣子API集成

**服务封装**:

```python
class CozeService:
    """扣子服务封装"""
    
    async def chat(
        self, 
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7
    ) -> str:
        """单轮对话"""
        pass
    
    async def generate_section(
        self,
        section_type: str,
        report_data: dict,
        template_data: dict
    ) -> str:
        """生成单个章节"""
        pass
    
    async def generate_full_report(
        self,
        report_id: int,
        progress_callback: Callable
    ) -> dict:
        """生成完整报告"""
        pass
```

**错误处理**:
- 网络超时: 重试3次,间隔2秒
- API限流: 指数退避重试
- 内容过滤: 返回友好提示
- 服务不可用: 降级为模板内容

### 10.2 Word生成服务

**核心类**:

```python
class WordService:
    """Word文档生成服务"""
    
    def generate_report(
        self, 
        report_data: Dict[str, Any], 
        output_path: str
    ) -> str:
        """生成Word报告"""
        pass
    
    def _add_section(self, doc, title, content):
        """添加章节"""
        pass
    
    def _add_dimension_analysis(self, doc, dimensions, excel_data):
        """添加维度分析"""
        pass
    
    def _generate_chart(self, question_data, chart_config) -> str:
        """生成图表,返回临时文件路径"""
        pass
```

### 10.3 Excel解析服务

**核心类**:

```python
class ExcelService:
    """Excel解析服务"""
    
    def parse_excel(self, file_path: str) -> dict:
        """解析Excel文件"""
        pass
    
    def _extract_questions(self, df) -> list:
        """提取问题数据"""
        pass
    
    def _match_questions(self, questions, structure_config) -> dict:
        """匹配题号"""
        pass
```

### 10.4 Word结构提取服务

**核心类**:

```python
class WordStructureExtractor:
    """Word结构提取器"""
    
    def extract_structure(self, file_path: str) -> list:
        """提取文档结构"""
        pass
    
    def _extract_headings(self, doc) -> list:
        """提取所有标题"""
        pass
    
    def _build_tree(self, headings) -> list:
        """构建树形结构"""
        pass

class AINodeClassifier:
    """AI节点分类器"""
    
    async def classify(self, title, content_preview, level) -> ClassificationResult:
        """分类节点类型"""
        pass
```

---

## 十一、实施计划

### 11.1 开发阶段

#### Phase 1: 基础架构 (Week 1)

| 任务 | 工期 | 负责人 | 交付物 |
|------|------|--------|--------|
| 数据库设计 | 2天 | 后端 | SQL脚本、ER图 |
| FastAPI框架搭建 | 2天 | 后端 | 项目基础结构 |
| 前端基础框架 | 1天 | 前端 | 布局组件、路由 |
| 设计系统实施 | 1天 | 前端 | 组件库、样式规范 |

**里程碑 M1**: 基础架构完成,可启动服务

#### Phase 2: 核心功能 (Week 2-3)

| 任务 | 工期 | 负责人 | 交付物 |
|------|------|--------|--------|
| Word解析服务 | 3天 | 后端 | Extractor模块 |
| AI分类服务 | 2天 | 后端 | Classifier模块 |
| 结构配置API | 3天 | 后端 | CRUD接口 |
| 结构配置页面 | 4天 | 前端 | 树形编辑器 |
| 维度模板模块 | 3天 | 前后端 | 完整功能 |

**里程碑 M2**: 结构配置功能完成

#### Phase 3: 报告生成 (Week 4-5)

| 任务 | 工期 | 负责人 | 交付物 |
|------|------|--------|--------|
| Excel解析服务 | 2天 | 后端 | ExcelService |
| 扣子API集成 | 3天 | 后端 | CozeService |
| Word生成服务 | 3天 | 后端 | WordService |
| 报告生成流程 | 3天 | 前后端 | 完整流程 |
| 报告管理页面 | 2天 | 前端 | 列表、详情页 |

**里程碑 M3**: 报告生成功能完成

#### Phase 4: 集成测试 (Week 6)

| 任务 | 工期 | 负责人 | 交付物 |
|------|------|--------|--------|
| 前后端联调 | 3天 | 全团队 | 修复bug |
| 集成测试 | 2天 | 测试 | 测试报告 |
| 性能优化 | 2天 | 后端 | 优化报告 |
| 部署配置 | 1天 | 运维 | Docker配置 |

**里程碑 M4**: 系统可上线运行

### 11.2 关键里程碑

| 里程碑 | 日期 | 目标 | 验收标准 |
|--------|------|------|----------|
| M1 | Week 1 结束 | 基础架构 | 服务启动成功,数据库连接正常 |
| M2 | Week 3 结束 | 结构配置 | 可完成完整的结构配置流程 |
| M3 | Week 5 结束 | 报告生成 | 可完成从上传Excel到导出Word全流程 |
| M4 | Week 6 结束 | 上线就绪 | 测试通过,部署文档完成 |

### 11.3 风险评估与应对

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|----------|
| Word格式不标准导致解析失败 | 中 | 高 | 1.提供格式规范文档 2.增强容错处理 3.提供手动配置入口 |
| AI分类准确率低 | 低 | 中 | 1.优化规则库 2.允许用户快速修正 3.收集反馈迭代 |
| 扣子API服务不稳定 | 中 | 高 | 1.实现重试机制 2.降级为模板内容 3.缓存历史生成结果 |
| 大文档解析性能问题 | 低 | 中 | 1.异步处理 2.分页加载 3.进度实时反馈 |
| 图表生成依赖matplotlib字体 | 中 | 低 | 1.预装中文字体 2.提供字体安装指南 |

---

## 十二、附录

### 12.1 Word模板格式指南

**标题样式规范**:

1. **使用标准Heading样式**
   - 一级标题: Heading 1 或 标题 1
   - 二级标题: Heading 2 或 标题 2
   - 三级标题: Heading 3 或 标题 3

2. **标题命名规范**
   - 一级标题: "一、章节名称" 或 "1. 章节名称"
   - 二级标题: "1.1 维度名称" 或 "(1) 分析标题"
   - 三级标题: 分析小标题

3. **避免使用**
   - 手动设置的加粗文字作为标题
   - 艺术字、文本框作为标题
   - 表格内标题

**示例结构**:

```
前言 (Heading 1)
一、项目背景 (Heading 1)
二、项目开展情况 (Heading 1)
三、问卷说明 (Heading 1)
四、问卷结果分析 (Heading 1)
  4.1 用药基础信息 (Heading 2)
    用药原因分析 (Heading 3)
    药品获取途径分析 (Heading 3)
  4.2 用药行为与习惯 (Heading 2)
    ...
五、调研结果 (Heading 1)
六、建议 (Heading 1)
```

### 12.2 Excel数据格式指南

**标准格式**:

| 题号 | 题目 | 选项A | 选项B | 选项C | 选项D | ... | A样本量 | B样本量 | ... | A占比 | B占比 | ... |
|------|------|-------|-------|-------|-------|-----|---------|---------|-----|-------|-------|-----|
| 1 | 您当时是因何种症状... | 脾胃虚弱 | 体倦乏力 | 中气下陷 | 气虚所致 | ... | 162 | 169 | ... | 23% | 24% | ... |
| 2 | 您是从什么渠道... | 医院 | 药店 | 网上 | 其他 | ... | 300 | 250 | ... | 42% | 35% | ... |

**注意事项**:
- 题号需为数字或"Q+数字"格式
- 百分比需包含%符号
- 选项不宜过长(建议<30字)
- 避免合并单元格

### 12.3 提示词模板

**前言生成提示词**:

```
【系统提示词】
你是一位资深的医药市场研究报告撰写专家...

【用户提示词模板】
请为以下产品生成调研报告的前言部分。

【产品信息】
产品名称：{{product_name}}
调研区域：{{survey_region}}
调研时间：{{survey_time_range}}
样本数量：{{sample_count}}份

【输出要求】
...
```

### 12.4 API错误码对照表

| 错误码 | 描述 | 处理建议 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数格式和必填项 |
| 404 | 资源不存在 | 检查ID是否正确 |
| 422 | 数据验证失败 | 检查数据格式和业务规则 |
| 500 | 服务器内部错误 | 联系管理员查看日志 |
| 501 | 生成失败 | 查看错误详情,重试或联系支持 |
| 502 | AI服务错误 | 稍后重试,或检查AI服务状态 |

### 12.5 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2026-02-26 | 初始版本,基础功能定义 | - |
| v2.0 | 2026-03-02 | 整合结构配置功能,添加图表生成,完善详细设计 | - |

---

**文档结束**

*本文档由产品开发团队维护,如有疑问请联系产品负责人。*
