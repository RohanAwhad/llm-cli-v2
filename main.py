# ===
# logging configuration
# ===

import os
import base64
from dotenv import load_dotenv
load_dotenv()

# Langfuse credentials
LANGFUSE_PUBLIC_KEY = os.environ['LANGFUSE_PUBLIC_KEY']
LANGFUSE_SECRET_KEY = os.environ['LANGFUSE_SECRET_KEY']
LANGFUSE_AUTH = base64.b64encode(f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()).decode()

# OpenTelemetry endpoints
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:3000/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

import logfire
logfire.configure(service_name='my-chat-service', send_to_logfire=False)


import asyncio
from src.core import chat, search, models


async def main():
    # cs = chat.ChatSession()
    # while True:
    #     user_input = input('user> ')
    #     res = await cs.chat(user_input)
    #     print(res)

    ss = search.SearchSession()
    user_input = input('user> ')
    res = await ss.ask(user_input, models.Models.GPT_4O)
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
