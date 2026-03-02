# 大纲配置功能开发计划

## 1. 后端开发

### 1.1 定义数据模型
- **文件**: `backend/app/models/database.py`
- **任务**: 添加 `OutlineChapter` 模型，包含以下字段：
    - `id`: bigint, primary key
    - `template_id`: bigint, foreign key to `dimension_templates.id`
    - `chapter_type`: varchar(50)
    - `chapter_title`: varchar(200)
    - `sort_order`: int
    - `is_enabled`: boolean
    - `level`: int
    - `parent_id`: bigint, foreign key to `outline_chapters.id` (self-referencing)
    - `generation_type`: enum ('ai', 'fixed', 'data')
    - `prompt_config_id`: bigint, foreign key to `prompt_configs.id`
    - `fixed_content`: text

### 1.2 定义 Pydantic Schema
- **文件**: `backend/app/models/schemas.py`
- **任务**: 添加 `OutlineChapterBase`, `OutlineChapterCreate`, `OutlineChapterUpdate`, `OutlineChapter` (Response) 模型。

### 1.3 创建 API 路由
- **文件**: `backend/app/api/outline.py` (新建)
- **任务**: 实现以下接口：
    - `GET /api/v1/templates/{template_id}/outline`: 获取模板的大纲章节列表
    - `POST /api/v1/templates/{template_id}/outline`: 创建/重置大纲章节
    - `PUT /api/v1/outline/chapters/{chapter_id}`: 更新章节信息 (标题, 开关, 排序等)
    - `POST /api/v1/outline/chapters/reorder`: 批量更新排序
    - `DELETE /api/v1/outline/chapters/{chapter_id}`: 删除章节 (仅自定义章节可删除)

### 1.4 注册路由
- **文件**: `backend/app/main.py`
- **任务**: 引入并注册 `outline` router。

## 2. 前端开发

### 2.1 创建大纲配置页面
- **文件**: `frontend/outline-config.html` (新建)
- **任务**:
    - 复制 `frontend/index.html` 或 `frontend/templates.html` 作为基础模板。
    - 实现大纲列表展示区域。
    - 实现章节项的 HTML 结构 (包含标题、开关、编辑按钮、拖拽手柄)。
    - 引入 SortableJS (CDN) 用于拖拽排序。

### 2.2 实现前端逻辑
- **文件**: `frontend/outline-config.html` (内联 JS 或新建 `frontend/js/outline.js`)
- **任务**:
    - `loadOutline(templateId)`: 加载大纲数据。
    - `renderOutline(chapters)`: 渲染大纲列表。
    - `updateChapter(chapterId, data)`: 调用 API 更新章节。
    - `handleDragEnd(evt)`: 处理拖拽结束事件，调用排序 API。
    - `toggleChapter(chapterId, isEnabled)`: 处理开关切换。

### 2.3 添加导航入口
- **文件**: `frontend/index.html`, `frontend/reports.html`, `frontend/templates.html`
- **任务**: 在导航栏添加「大纲配置」链接，指向 `outline-config.html`。

## 3. 验证与测试
- **任务**:
    - 重启后端服务。
    - 打开前端页面。
    - 测试大纲加载、编辑、排序、开关功能。
    - 验证数据持久化。
