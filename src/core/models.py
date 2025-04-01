import os
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


qwen7b_model = OpenAIModel(
  model_name='qwen2.5:7b-instruct-q4_K_M',
  provider=OpenAIProvider(base_url='http://localhost:11434/v1')
)
qwen72b_model = OpenAIModel(
  model_name='Qwen/Qwen2-72B-Instruct',
  provider=OpenAIProvider(
    base_url='https://api.together.xyz/v1',
    api_key=os.environ['TOGETHER_API_KEY']
  )
)

class Models:
  QWEN_7B = qwen7b_model
  QWEN_72B = qwen72b_model
  DS_V3 = 'deepseek:deepseek-chat'
  FLASH = 'google-gla:gemini-2.0-flash'
  GEMINI = ''
  SONNET = 'anthropic:claude-3-5-sonnet-latest'
  GPT_4O = 'openai:gpt-4o'
