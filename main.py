from dotenv import load_dotenv
load_dotenv()

import asyncio
import os
from typing import Callable

# first-party
from src import logger
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
    logger.setup_logging()
    writer = Writer()
    writer.add_sink(write_to_file)
    writer.add_sink(write_to_stdout)

    ss = search.SearchSession(model=models.Models.FLASH)
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
