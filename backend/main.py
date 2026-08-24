from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.projects import router as projects_router

app = FastAPI(
    title="ClipForge Local API",
    description="Modular monolith backend for local AI-powered reel extraction",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)

@app.get("/")
def read_root():
    return {
        "name": "ClipForge Local API",
        "status": "online",
        "phase": "Phase 1 - Ingestion & Audio Pipeline"
    }
