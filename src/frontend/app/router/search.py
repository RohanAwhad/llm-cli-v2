from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

# first-party
from src.core import search, models

router = APIRouter(prefix="/api/v1", tags=["search"])

# Model mapping based on models.py
MODEL_MAPPING = {
    "flash": models.Models.FLASH,
    "qwen7b": models.Models.QWEN_7B,
    "qwen72b": models.Models.QWEN_72B,
    "deepseek": models.Models.DS_V3,
    "gemini": models.Models.GEMINI,
    "sonnet": models.Models.SONNET,
    "gpt4": models.Models.GPT_4O
}

class SearchRequest(BaseModel):
    query: str
    model: Optional[str] = "flash"  # default to flash model

    class Config:
        schema_extra = {
            "example": {
                "query": "What is Python?",
                "model": "flash"
            }
        }

class SearchResponse(BaseModel):
    result: str
    model_used: str


@router.post("/search")
async def perform_search(request: SearchRequest):
    try:
        # Map model string to actual model
        model_key = request.model.lower()
        if model_key not in MODEL_MAPPING:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model. Available models: {', '.join(MODEL_MAPPING.keys())}"
            )
            
        model = MODEL_MAPPING[model_key]

        # Initialize search session
        ss = search.SearchSession(model=model)
        
        # Perform search
        coros = ss.ask_stream(request.query)
        async def generate_stream():
            async for chunk in coros:
                yield chunk

        return StreamingResponse(generate_stream(), media_type="text/event-stream")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
