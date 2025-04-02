# ===
# logging configuration
# ===

import os
import base64
from dotenv import load_dotenv
load_dotenv()


def setup_logging():
    try:
        # Langfuse credentials
        LANGFUSE_PUBLIC_KEY = os.environ['LANGFUSE_PUBLIC_KEY']
        LANGFUSE_SECRET_KEY = os.environ['LANGFUSE_SECRET_KEY']
        LANGFUSE_AUTH = base64.b64encode(f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()).decode()

        # OpenTelemetry endpoints
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:3000/api/public/otel"
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
         
        trace_provider = TracerProvider()
        trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
         
        # Sets the global default tracer provider
        from opentelemetry import trace
        trace.set_tracer_provider(trace_provider)
         
        # Creates a tracer from the global tracer provider
        tracer = trace.get_tracer(__name__)

        # OpenLLMetry
        from traceloop.sdk import Traceloop
        Traceloop.init(disable_batch=True,
                       api_endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
                       headers=os.environ.get(f"Authorization=Basic {LANGFUSE_AUTH}"),)

        print('logging initialized')
    except Exception as e:
        print(e)
        print('Couldn\'t start logging')

# ===

import asyncio
from typing import Callable

# first-party
from src.core import search, models

class Writer: 
    def __init__(self): self.sinks = []
    def add_sink(self, func: Callable): self.sinks.append(func)
    def write(self, *args, **kwargs):
        for sink in self.sinks: sink(*args, **kwargs)


def write_to_file(user_input, response):
    if not os.path.exists('tmp.txt'): open('tmp.txt', 'w').close()
    with open('tmp.txt', 'a') as f: f.write(f'### {user_input}\n\n{response.strip()}\n\n')
def write_to_stdout(user_input, response): print(response)

async def main():
    setup_logging()
    writer = Writer()
    writer.add_sink(write_to_file)
    writer.add_sink(write_to_stdout)

    ss = search.SearchSession(model=models.Models.FLASH, stream=True)
    user_input = input('user> ').strip()
    # res = await ss.ask(user_input, models.Models.QWEN_7B)
    res = await ss.ask(user_input)
    writer.write(user_input, res)


async def mock_main():
    writer = Writer()
    writer.add_sink(write_to_file)
    writer.add_sink(write_to_stdout)

    user_input = input('user> ')
    # res = await ss.ask(user_input, models.Models.QWEN_7B)
    res = 'hello there from ai'
    writer.write(user_input, res)



if __name__ == "__main__":
    asyncio.run(main())
