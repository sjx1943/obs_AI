from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .api.router import router as api_router
import os

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="本地LLM学习助手",
        description="一个集成RAG知识检索和OBS录屏功能的学习辅助工具。",
        version="1.0.0"
    )

    # Include the API router
    app.include_router(api_router, prefix="/api")

    # Mount static files for the frontend
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
    if os.path.exists(frontend_dir):
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")

    @app.on_event("startup")
    async def startup_event():
        print("--- 应用启动 ---")
        # Here you can initialize resources like DB connections, etc.

    @app.on_event("shutdown")
    async def shutdown_event():
        print("--- 应用关闭 ---")

    return app

app = create_app()
