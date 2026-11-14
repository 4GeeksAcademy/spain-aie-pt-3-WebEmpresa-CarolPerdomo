from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.auth.routes import router as auth_router
from services.users.routes import router as users_router
from services.profiles.routes import router as profiles_router
from services.core.config import settings


def create_app():
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Nexova API",
        description="Authentication and user management API for Nexova",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(profiles_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "service": "Nexova API",
            "version": "1.0.0"
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT
    )
