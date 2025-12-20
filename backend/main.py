from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
from strawberry.fastapi import GraphQLRouter

from app.database import async_engine, engine
from app.models.base import Base
from app.schemas.graphql import schema
from app.routers.project_router import router as project_router
from app.routers.github_router import router as github_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
# Uncomment to debug SQL queries:
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting application...")
    
    print("📦 Creating database tables...")
    # Use async engine for table creation
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables ready")
    
    # Run migrations automatically (migrations still use sync for simplicity)
    print("🔄 Running migrations...")
    from migrations.auto_migrate import run_all_migrations
    run_all_migrations()
    print("✅ Migrations complete")
    
    print("✅ Application startup complete!")
    
    yield
    # Shutdown
    print("👋 Shutting down application...")
    await async_engine.dispose()
    print("✅ Async engine disposed")


app = FastAPI(
    title="Keeys API",
    description="API for localization management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL context getter
async def get_context(request: Request):
    """
    Get context for GraphQL requests.
    """
    return {"request": request}


# GraphQL endpoint
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

# REST API routers
app.include_router(project_router)
app.include_router(github_router)


@app.get("/")
async def root():
    return {"message": "Hi there! This is Keeys API. Visit https://keeys.app for more information."}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Starting server on port: {port}")
    print(f"PORT environment variable: {os.getenv('PORT', 'NOT SET')}")
    
    # Use reload only in development
    is_dev = os.getenv("ENVIRONMENT", "production") == "development"
    
    config = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": port,
        "reload": is_dev,
    }
    
    if is_dev:
        config["reload_dirs"] = ["app"]
    else:
        # Production settings
        config["workers"] = 1  # Railway starter plan, use 1 worker
        config["log_level"] = "info"
    
    print(f"🔧 Configuration: {config}")
    uvicorn.run(**config)
