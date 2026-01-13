# main.py
import sys
from pathlib import Path

# 将当前目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # 导入静态文件支持
from routes import auth, info, model, chat

# 创建FastAPI应用实例
app = FastAPI(
    title="时序系统",
    description="时序系统",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # 允许前端访问所有响应头
)


static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 注册认证路由
app.include_router(auth.router)
app.include_router(info.router)  # 注册数据路由
app.include_router(model.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {
        "message": "FastAPI认证服务已启动",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthys"}