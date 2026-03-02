-- 数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS report_generator 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE report_generator;

-- ============================================
-- 1. 维度模板表
-- ============================================
CREATE TABLE IF NOT EXISTS dimension_templates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    template_name VARCHAR(100) NOT NULL COMMENT '模板名称',
    report_type ENUM('doctor', 'patient') NOT NULL COMMENT '报告类型：医生/患者',
    description TEXT COMMENT '模板描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_report_type (report_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='维度模板表';

-- ============================================
-- 2. 维度表
-- ============================================
CREATE TABLE IF NOT EXISTS dimensions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    template_id BIGINT NOT NULL COMMENT '所属模板ID',
    dimension_number VARCHAR(10) NOT NULL COMMENT '维度编号（如：4.1）',
    dimension_title VARCHAR(100) NOT NULL COMMENT '维度标题',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (template_id) REFERENCES dimension_templates(id) ON DELETE CASCADE,
    INDEX idx_template_sort (template_id, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='维度表';

-- ============================================
-- 3. 问题分析配置表
-- ============================================
CREATE TABLE IF NOT EXISTS question_analysis_configs (
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

-- ============================================
-- 4. 提示词配置表
-- ============================================
CREATE TABLE IF NOT EXISTS prompt_configs (
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

-- ============================================
-- 5. 报告表
-- ============================================
CREATE TABLE IF NOT EXISTS reports (
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

-- ============================================
-- 插入默认数据
-- ============================================

-- 插入默认提示词配置
INSERT INTO prompt_configs (config_name, report_type, section_type, system_prompt, user_prompt_template, temperature) VALUES
-- 前言配置
('前言-患者', 'patient', 'preface', 
'你是一位资深的医药市场研究报告撰写专家，擅长撰写专业、严谨、有洞察力的调研报告前言。

写作风格要求：
1. 语言正式、专业，体现行业权威性
2. 逻辑清晰，层层递进
3. 既有宏观背景，又有具体调研目的
4. 避免空洞套话，要有实质性内容
5. 适当引用行业术语，体现专业性

字数要求：400-500字',
'请为以下产品生成调研报告的前言部分。

【产品信息】
产品名称：{{product_name}}
调研区域：{{survey_region}}
调研时间：{{survey_time_range}}
样本数量：{{sample_count}}份

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
直接输出前言正文，不需要标题。使用专业、客观的语言风格。',
0.7),

-- 项目背景配置
('项目背景-患者', 'patient', 'background',
'你是一位专业的医药市场分析师，擅长从行业政策和市场需求角度分析项目背景。

写作风格要求：
1. 结合国家政策和行业趋势
2. 突出调研的必要性和紧迫性
3. 体现区域特色和差异化需求
4. 语言简洁有力，逻辑严密
5. 数据和事实支撑观点

字数要求：300-400字',
'请为以下调研项目生成"项目背景"章节内容。

【产品信息】
产品名称：{{product_name}}
调研区域：{{survey_region}}

【项目背景结构要求】
1. 第一段（150-200字）- 政策与行业背景：
   - 介绍中医药产业发展政策支持
   - 说明补益类中成药的市场趋势
   - 阐述患者用药体验的重要性

2. 第二段（150-200字）- 区域与需求背景：
   - 分析{{survey_region}}的区域特点
   - 说明该区域的市场需求特征
   - 阐述专项调研的必要性

【输出格式】
直接输出项目背景正文，不需要标题。分两段，每段一个核心观点。',
0.7),

-- 项目开展配置
('项目开展-患者', 'patient', 'project_info',
'你是一位专业的调研项目管理人员，擅长撰写项目执行情况说明。

写作风格要求：
1. 信息准确、客观
2. 格式规范、清晰
3. 数据精确、可追溯
4. 语言简洁、不冗余

字数要求：100-150字',
'请生成"项目开展情况"章节内容。

【项目信息】
产品名称：{{product_name}}
调研区域：{{survey_region}}
调研时间：{{survey_time_range}}
样本数量：{{sample_count}}份
问题数量：{{question_count}}道

【输出格式要求】
严格按照以下格式输出：

项目工具：调查问卷，{{question_count}}道选择题，其内容涵盖多个维度，全面覆盖患者用药全流程关键节点。

样本采集范围：{{survey_region}}

样本采集数量：本次共收集筛选到有效问卷{{sample_count}}份。

样本采集时间：{{survey_time_range}}',
0.5),

-- 调研结果配置
('调研结果-患者', 'patient', 'conclusion',
'你是一位资深的医药市场研究专家，擅长从调研数据中提炼核心发现并形成结构化结论。

写作风格要求：
1. 分点陈述，逻辑清晰
2. 每个观点有数据支撑
3. 结论明确、可执行
4. 语言简洁有力
5. 体现专业性和权威性

字数要求：500-600字',
'请根据以下维度数据，生成"调研结果"章节内容。

【产品信息】
产品名称：{{product_name}}
样本数量：{{sample_count}}

【维度汇总数据】
{{dimensions_data}}

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
[核心发现]',
0.7),

-- 建议配置
('建议-患者', 'patient', 'suggestions',
'你是一位资深的医药市场策略顾问，擅长基于调研数据提出可执行的建议。

写作风格要求：
1. 建议具体、可执行
2. 针对性强，直击问题核心
3. 分层次提出建议（产品、推广、服务等）
4. 语言简洁，避免空话
5. 体现专业性和前瞻性

字数要求：300-400字',
'请根据以下调研结果，生成"建议"内容。

【产品信息】
产品名称：{{product_name}}
调研区域：{{survey_region}}

【关键发现】
{{key_findings}}

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
[具体建议，100字左右]',
0.7);

-- ============================================
-- 插入示例模板数据
-- ============================================
-- 患者问卷模板
INSERT INTO dimension_templates (id, template_name, report_type, description) VALUES
(1, '患者问卷模板', 'patient', '适用于患者用药体验与疗效反馈调研');

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
-- 4.1 用药基础信息
(1, 1, '用药原因分析', 1),
(1, 2, '药品获取途径分析', 2),
(1, 3, '用药时长分析', 3),
-- 4.2 用药行为与习惯
(2, 4, '服用剂量规范性分析', 1),
(2, 10, '联合调理方式分析', 2),
-- 4.3 药品使用体验
(3, 5, '药品口味接受度分析', 1),
(3, 7, '包装设计满意度分析', 2),
-- 4.4 用药安全性
(4, 6, '不良反应发生率分析', 1),
-- 4.5 疗效评价
(5, 8, '疗效满意度分析', 1),
(5, 9, '症状改善程度分析', 2),
-- 4.6 药品改进需求
(6, 11, '改进需求分析', 1),
-- 4.7 临床价值延伸
(7, 12, '复购意愿分析', 1);
