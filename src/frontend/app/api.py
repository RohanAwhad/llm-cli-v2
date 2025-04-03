from dotenv import load_dotenv
from src import logger
load_dotenv('.dev.env')
logger.setup_logging()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# first-party
from .router import search_router

# Create FastAPI app
app = FastAPI(
    title="Search API",
    version="1.0.0",
    description="API for performing searches using various language models"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(search_router)

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8005)
