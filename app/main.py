"""FastAPI Main Application."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.config import get_settings
from app.infrastructure.database.connection import close_db, init_db
from app.presentation.api.routes import chat_routes, document_routes, health_routes
from app.presentation.web.routes import router as web_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    settings = get_settings()
    print(f"🚀 Starting RAG Chatbot v{__version__}")
    print(f"   Environment: {settings.environment}")
    print(f"   Debug: {settings.debug}")

    try:
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
        print("   Make sure PostgreSQL is running and pgvector is installed")

    yield

    print("🛑 Shutting down...")
    await close_db()
    print("✅ Database connections closed")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="RAG Chatbot",
        description="Retrieval Augmented Generation Chatbot dengan FastAPI",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.include_router(health_routes.router)
    app.include_router(document_routes.router)
    app.include_router(chat_routes.router)
    app.include_router(web_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
