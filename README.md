# 报告生成工具

基于 PRD 文档开发的问卷调研报告生成系统。

## 📋 系统概述

**报告生成工具** 是一个用于生成专业问卷调研分析报告的系统，支持：

- 维度模板配置（管理员）
- 报告生成（用户）
- Excel数据解析
- AI智能内容生成（扣子API集成）
- Word报告导出

## 🏗️ 技术架构

| 层级 | 技术栈 |
|------|--------|
| 前端 | HTML5 + Tailwind CSS + Vanilla JS |
| 后端 | Python + FastAPI |
| 数据库 | MySQL 8.0 |
| AI服务 | 扣子API (Coze) |
| 文档生成 | python-docx |

## 🚀 快速开始

### 方式一：Docker部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd 爱诺模板项目
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置扣子API密钥
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **访问系统**
- 前端界面: http://localhost:8000/static/index.html
- API文档: http://localhost:8000/docs

### 方式二：本地开发

1. **安装Python依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **配置数据库**
```bash
# 创建MySQL数据库
mysql -u root -p < database/init.sql
```

3. **配置环境变量**
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export COZE_API_KEY=your_coze_api_key
```

4. **启动后端服务**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

5. **访问前端**
```bash
# 直接打开 frontend/index.html
# 或使用Live Server等工具
```

## 📁 项目结构

```
爱诺模板项目/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据库模型
│   │   ├── services/       # 业务服务
│   │   └── main.py         # 应用入口
│   ├── requirements.txt    # Python依赖
│   └── Dockerfile          # Docker配置
├── frontend/               # 前端代码
│   ├── index.html         # 首页
│   ├── templates.html     # 维度配置
│   ├── reports.html       # 报告列表
│   └── report-create.html # 生成报告
├── database/
│   └── init.sql           # 数据库初始化脚本
├── docker-compose.yml     # Docker编排配置
└── docs/
    ├── PRD.MD            # 产品需求文档
    └── DESIGN.md         # 系统设计文档
```

## 🔧 核心功能

### 1. 维度配置
- 创建/编辑维度模板
- 配置维度（如 4.1 用药基础信息）
- 配置问题分析标题（如 用药原因分析）

### 2. 报告生成流程
1. **选择模板** - 从预配置的维度模板中选择
2. **填写信息** - 输入报告标题、产品名称、调研区域等
3. **上传Excel** - 上传问卷统计数据（解析后自动填充）
4. **生成报告** - AI自动生成各章节内容
5. **导出Word** - 下载生成的Word报告

### 3. AI内容生成（扣子API）
系统通过扣子API的5个LLM节点生成：
- 前言
- 项目背景
- 项目开展情况
- 调研结果分析
- 建议

## 📊 API接口

### 维度模板管理
- `POST /api/v1/templates` - 创建模板
- `GET /api/v1/templates` - 获取模板列表
- `GET /api/v1/templates/{id}` - 获取模板详情
- `PUT /api/v1/templates/{id}` - 更新模板
- `DELETE /api/v1/templates/{id}` - 删除模板

### 维度管理
- `POST /api/v1/templates/{id}/dimensions` - 添加维度
- `PUT /api/v1/dimensions/{id}` - 更新维度
- `DELETE /api/v1/dimensions/{id}` - 删除维度

### 问题配置
- `POST /api/v1/dimensions/{id}/questions` - 添加问题
- `PUT /api/v1/questions/{id}` - 更新问题
- `DELETE /api/v1/questions/{id}` - 删除问题

### 报告生成
- `POST /api/v1/reports` - 创建报告
- `GET /api/v1/reports` - 获取报告列表
- `POST /api/v1/reports/{id}/upload-excel` - 上传Excel
- `POST /api/v1/reports/{id}/generate` - 生成报告
- `GET /api/v1/reports/{id}/progress` - 获取生成进度（SSE）
- `GET /api/v1/reports/{id}/export` - 导出Word

## 🎨 界面设计

系统采用现代B端管理后台风格：
- **Primary Color**: #6366F1 (Indigo)
- **Success Color**: #10B981 (Emerald)
- **Background**: #F5F3FF (Light lavender)
- **Text**: #1E1B4B (Dark indigo)
- **Font**: Plus Jakarta Sans

## ⚙️ 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DB_HOST | 数据库主机 | localhost |
| DB_PORT | 数据库端口 | 3306 |
| DB_NAME | 数据库名称 | report_generator |
| DB_USER | 数据库用户 | root |
| DB_PASSWORD | 数据库密码 | - |
| COZE_API_KEY | 扣子API密钥 | - |
| COZE_BASE_URL | 扣子API地址 | https://api.coze.cn |
| APP_PORT | 服务端口 | 8000 |
| DEBUG | 调试模式 | false |

## 📖 文档

- [产品需求文档 (PRD)](docs/PRD.MD)
- [系统设计文档](docs/DESIGN.MD)
- [API文档](http://localhost:8000/docs) (运行后访问)

## 🤝 贡献

欢迎提交Issue和Pull Request。

## 📄 许可证

MIT License

## 🙏 致谢

- FastAPI - 现代Python Web框架
- Tailwind CSS - 实用优先的CSS框架
- 扣子(Coze) - AI能力平台
