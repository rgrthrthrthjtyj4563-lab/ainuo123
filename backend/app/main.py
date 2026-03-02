"""
FastAPI 主应用入口
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from config import get_settings
from app.models.database import Base, engine
from app.api import templates, dimensions, questions, reports, outline, report_structures

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建表
    Base.metadata.create_all(bind=engine)
    
    # 创建上传和输出目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    # 挂载静态文件（在目录创建后进行）
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "../frontend")
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
    app.mount("/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")
    
    yield
    
    # 关闭时的清理工作
    pass


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="报告生成工具 - API服务",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件挂载将在生命周期管理中处理

# 注册路由
app.include_router(templates.router, prefix="/api/v1/templates", tags=["维度模板"])
# 修正：dimensions.router 中包含了 create_dimension 路由，路径为 /{template_id}/dimensions
# 如果挂载在 /api/v1/dimensions，则完整路径为 /api/v1/dimensions/{template_id}/dimensions
# 但 templates.html 中调用的路径是 /api/v1/templates/{template_id}/dimensions
# 这导致了 404 Not Found 或路径不匹配的问题。
# 更好的做法是将 create_dimension 移至 templates.py，或者在这里调整挂载路径。
# 由于 create_dimension 依赖 template_id，它更像是一个模板下的子资源。
# 但为了不破坏现有结构，我们保持代码逻辑，但在前端调用时需要注意。
# 实际上，之前的前端代码尝试访问 /api/v1/templates/{template_id}/dimensions，这在 templates.py 中没有定义。
# 而 dimensions.py 中定义了 @router.post("/{template_id}/dimensions")。
# 所以如果在 main.py 中 dimensions.router 挂载在 /api/v1/dimensions，则路径为 /api/v1/dimensions/{template_id}/dimensions。
# 前端之前修改为了 /api/v1/dimensions/{template_id}/dimensions，这是对的。
# 但是用户报错 TypeError: Failed to fetch，这通常是网络问题或跨域问题，或者服务器没启动。

app.include_router(dimensions.router, prefix="/api/v1/dimensions", tags=["维度管理"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["问题配置"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["报告生成"])
app.include_router(outline.router, prefix="/api/v1", tags=["大纲配置"])
app.include_router(report_structures.router, prefix="/api/v1", tags=["报告结构"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
