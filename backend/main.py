from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from strawberry.fastapi import GraphQLRouter

from app.database import engine
from app.models.base import Base
from app.schemas.graphql import schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    
    # Run migrations automatically
    from migrations.auto_migrate import run_all_migrations
    run_all_migrations()
    
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Locales API",
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

# TODO: Add your REST API routers here


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI + GraphQL Boilerplate!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port: {port}")
    print(f"PORT environment variable: {os.getenv('PORT', 'NOT SET')}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Auto-reload on code changes
        reload_dirs=["app"]  # Watch app directory for changes
    )
