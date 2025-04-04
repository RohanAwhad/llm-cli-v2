from pydantic_ai import Agent

from . import models

class ChatSession:
  system_prompt = """
You are a language model, and your job is to help user and address their queries.

Your name is Edith.
  """.strip()

  def __init__(self, system_prompt=None):
    self.message_history = None
    if system_prompt is not None: self.system_prompt = system_prompt

  async def stream_chat(self, message, model=models.Models.QWEN_7B):
    agent = self._get_agent(model)
    return agent.run_stream(message, message_history=self.message_history)

  async def chat(self, message, model=models.Models.QWEN_7B):
    agent = self._get_agent(model)
    result = await agent.run(message, message_history=self.message_history)
    self.message_history = result.all_messages()
    return result.data

  def _get_agent(self, model):
    return Agent(model, system_prompt=self.system_prompt, instrument=True)

