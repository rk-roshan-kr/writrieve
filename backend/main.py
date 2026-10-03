import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.generation import router as generation_router
from api.decision import router as decision_router
from api.control_plane import router as control_plane_router
from api.benchmark import run_3way_benchmark
from connectors.factory import get_context_provider

app = FastAPI(
    title="Writrieve — Open-Weight Personal Context Engine",
    description="Task-aware personal context orchestration layer selecting minimum sufficient context for open-weight language models.",
    version="1.0.0"
)

# Enable CORS for Chrome Extension and Frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation_router)
app.include_router(decision_router)
app.include_router(control_plane_router)

@app.get("/api/health")
async def health_check():
    provider = get_context_provider()
    caps = provider.capabilities()
    return {
        "status": "healthy",
        "service": "Write4U Engine",
        "model_architecture": "Qwen3-8B (Planner & Writer) + BGE-M3 + BGE-Reranker-v2",
        "provider_adapter": caps,
        "indexed_signals": len(provider.get_all_candidates())
    }

@app.get("/api/benchmark")
async def get_benchmark():
    """
    Executes and returns the 3-way evaluation:
    Naive Full Context vs Standard RAG vs Write4U Adaptive Selection
    """
    return run_3way_benchmark()

@app.get("/api/candidates")
async def get_all_candidates():
    """
    Returns the indexed pool of candidates via active ContextProvider adapter.
    """
    provider = get_context_provider()
    candidates = provider.get_all_candidates()
    return {
        "total": len(candidates),
        "provider": provider.capabilities()["provider"],
        "items": candidates
    }

@app.get("/api/connect/{app_name}")
async def connect_integration(app_name: str = "gmail", redirect_url: str = None):
    """
    Generates a real OAuth authorization link via Composio for the user.
    """
    provider = get_context_provider()
    if hasattr(provider, "get_connection_link"):
        return provider.get_connection_link(app_name=app_name, redirect_url=redirect_url)
    return {
        "success": False,
        "error": "Active provider does not support live OAuth connection.",
        "provider": provider.capabilities()["provider"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
