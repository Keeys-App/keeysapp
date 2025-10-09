from fastapi import FastAPI
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

# GraphQL endpoint
graphql_app = GraphQLRouter(schema)
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
    uvicorn.run(app, host="0.0.0.0", port=port)
