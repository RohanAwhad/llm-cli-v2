# ===
# logging configuration
# ===

import os
import base64
from dotenv import load_dotenv
load_dotenv('.dev.env')

# Langfuse credentials
LANGFUSE_PUBLIC_KEY = os.environ['LANGFUSE_PUBLIC_KEY']
LANGFUSE_SECRET_KEY = os.environ['LANGFUSE_SECRET_KEY']
LANGFUSE_AUTH = base64.b64encode(f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()).decode()

# OpenTelemetry endpoints
LANGFUSE_HOST = os.environ['LANGFUSE_HOST']
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{LANGFUSE_HOST}/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

# Logfire
# import logfire
# logfire.configure(service_name='my-chat-service-test', send_to_logfire=False)

# OpenTelemetry
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

# Openllmetry
from traceloop.sdk.decorators import workflow, task
from traceloop.sdk import Traceloop
Traceloop.init(disable_batch=True,
               api_endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
               headers=os.environ.get(f"Authorization=Basic {LANGFUSE_AUTH}"),)
# ===


from pydantic_ai import Agent
from src.core.models import Models

reflection_agent = Agent(Models.QWEN_7B, system_prompt='You are a language model and your job is to reflect on the given user message', instrument=True)
answer_agent = Agent(Models.QWEN_7B, system_prompt='You are a language model, and you will be given a user message and a reflection on that user message, and your job is to finally respond back to the user in an apt fashion', instrument=True)


from dataclasses import dataclass

@dataclass
class OutputData:
    reflection: str
    user_question: str
    bleh: str

@task(name='adding-bleh')
def some_random_function(reflection, user_question):
    return OutputData(reflection=reflection, user_question=user_question, bleh='bleh')

@workflow(name='reflect-and-answer')
def main():

    user_message = 'Hi there, can you help me figure out should i take a left or a right?'

    reflection = reflection_agent.run_sync(user_message)
    print('reflection:', reflection.data)

    compiled_data = some_random_function(reflection.data, user_message)

    prompt = f'User message: {compiled_data.user_question}\nReflection: {compiled_data.reflection + compiled_data.bleh}'
    final_answer = answer_agent.run_sync(prompt)

    print('Final Answer:', final_answer.data)

main()
