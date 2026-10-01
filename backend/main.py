"""LegalEase - FastAPI Main Application Entry Point.

Initializes FastAPI, configures CORS, mounts health checks and modular routes.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("LegalEaseAPI")

# Initialize FastAPI Application
app = FastAPI(
    title="LegalEase – AI Legal Document Generator",
    description="High-performance backend API for generating structured legal documents using Google Gemini.",
    version="1.0.0",
)

# Enable CORS for Streamlit and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(router)


@app.get("/", tags=["Health"])
def home():
    """Root health-check confirming that LegalEase API is running."""
    return {
        "status": "success",
        "message": "LegalEase API is running",
        "service": "LegalEase – AI-Powered Legal Document Generator",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    logger.info("Starting LegalEase FastAPI server on port 8000...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
