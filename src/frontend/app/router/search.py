from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict

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
    model: Optional[str] = "qwen7b"  # default to flash model

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


@router.post("/stream")
async def stream_response(request: SearchRequest):
    from pydantic_ai import Agent
    reflection_agent = Agent(models.Models.FLASH, system_prompt='You are a language model and your job is to reflect on the given user message', instrument=True)

    # Define an async generator for streaming data
    async def generate_stream(query: str):
        async with reflection_agent.run_stream(query) as result:
            async for chunk in result.stream_text(delta=True):
                yield chunk  # Yield each chunk of data

    return StreamingResponse(generate_stream(request.query), media_type="text/event-stream")




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
        ss = search.SearchSession(model=model, stream=True)
        
        # Perform search
        result = await ss.ask(request.query)
        return StreamingResponse(result, media_type="text/event-stream")
        
        if not result:
            raise HTTPException(status_code=404, detail="No results found")
            
        return SearchResponse(
            result=result,
            model_used=request.model
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
