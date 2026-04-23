from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routes import auth, health_profile, diet_preferences, health_goals, chat, recipes, knowledge
from app.routes.knowledge_base import router as knowledge_base_router
from app.routes.admin import router as admin_router
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="智能营养顾问系统 API",
    description="基于LLM的智能营养顾问与食谱推荐系统后端接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(health_profile.router, prefix="/api/v1")
app.include_router(diet_preferences.router, prefix="/api/v1")
app.include_router(health_goals.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(recipes.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(knowledge_base_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@app.get("/", tags=["首页"])
def read_root():
    return {
        "message": "欢迎使用智能营养顾问系统 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["健康检查"])
def health_check():
    return {"status": "healthy"}


@app.get("/debug/routes", tags=["调试"])
def list_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else []
            })
    return {"routes": routes}


@app.get("/debug/headers", tags=["调试"])
async def debug_headers(request: Request):
    auth_header = request.headers.get("Authorization")
    return {
        "authorization": auth_header,
        "all_headers": dict(request.headers)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
