import asyncio
import json
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
    test: bool = False

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


'''
OpenAI streaming response:

data: {"id":"chatcmpl-247","object":"chat.completion.chunk","created":1743981561,"model":"qwen2.5-coder:0.5b","system_fingerprint":"fp_ollama","choices":[{"index":0,"delta":{"role":"assistant","content":"Hello"},"finish_reason":null}]}
'''

async def mock_streaming():

    def to_dict(x):
        return dict(choices=[{'delta': {'role': 'assistant', 'content': x}}])

    for x in "This is a mock streaming response.".split():
        yield f'data: {json.dumps(to_dict(x))}\n\n'
        await asyncio.sleep(0.2)

    yield f'data: [DONE]'


@router.post("/search")
async def perform_search(request: SearchRequest):
    try:
        if request.test: return StreamingResponse(mock_streaming(), media_type="text/event-stream")
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
            to_dict = lambda x: dict(choices=[{'delta': {'role': 'assistant', 'content': x}}])
            async for chunk in coros:
                yield f'data: {json.dumps(to_dict(chunk))}\n\n'
            yield 'data: [DONE]'

        return StreamingResponse(generate_stream(), media_type="text/event-stream")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
