import asyncio
import re
from typing import List

# first-party
from . import chat, models
from src.tools import search

QUERY_GENERATOR_PROMPT = '''
You are a language model, and your job is to write google search queries for the given user question.

1. You need to first think out loud and reflect on what the user asked.
2. Then you need to understand and formulate things you could possibly search for on google.
3. Finally you need to write down search queries. Maximum of 5. Minimum of 2

You should respond in below format:

<reflection>
  [...]
</reflection>
<formulation>
  [...]
</formulation>
<queries>
  <query>query 1</query>
  <query>query 2</query>
  <query>query 3</query>
</queries>
'''.strip()

RESULT_PRUNER_PROMPT = '''
You are a language model and your job is, based on user's question, figure out if the google search result is a valid search result and would it help in answering user's question.

1. You need to first think out loud and reflect on what the user has asked.
2. You need to reflect on the search_result that is provided.
3. Then you need to think out if and how the search result is related to the user question
4. Finally you need to output, whether or not the search result should be used to generate the final answer.


Your input will be in the following format:
<search_result>
  <title>title of the search result</title>
  <url>url of the search result</url>
  <description>brief description of the search result</description>
  <extra_snippets>additional snippets related to the search result</extra_snippets>
</search_result>
<user_question>[...]</user_question>


Your response will be in the following format:
<user_question_reflection>
  [...]
</user_question_reflection>
<search_result_reflection>
  [...]
</search_result_reflection>
<result_relation>
  [...]
</result_relation>

<should_be_used>true/false</should_be_used>
'''.strip()

ANSWER_GENERATOR_PROMPT = '''
You are a language model and your job is, based on user's question and search result, write the final answer for the user.

1. You need to first think out loud and reflect on what the user asked.
2. Then, you need to reflect on what all context you have right now.
3. Then, you need to formulate an outline of the answer for the given user question
4. Then, you need to generate the final answer.


Your input will be in following format:
<context>
  <search_result>
    <title>title of the search result</title>
    <url>url of the search result</url>
    <description>brief description of the search result</description>
    <extra_snippets>additional snippets related to the search result</extra_snippets>
  </search_result>
</context>
<user_question>[...]</user_question>


Your response should be in following format:
<user_question_reflection>
  [...]
</user_question_reflection>
<context_reflection>
  [...]
</context_reflection>
<answer_formulation>
  [...]
</answer_formulation>
<final_answer>
  [...]
</final_answer>
'''.strip()



def parse_query_response(response: str) -> List[str]:
  """
  Parse the response from query generator prompt to extract search queries.
  
  Args:
      response: The response string from the LLM
      
  Returns:
      List of search queries
  """
  # Extract the queries section using regex
  queries_match = re.search(r'<queries>(.*?)</queries>', response, re.DOTALL)
  
  if not queries_match: return []
  
  queries_text = queries_match.group(1)
  queries = re.findall(r'<query>(.*?)</query>', queries_text)
  return [q.strip() for q in queries]



class SearchSession:
  async def ask(self, question, model=models.qwen7b_model):
    queries = await self._get_queries(question, model)
    search_results = await self._get_search_results(queries)
    pruned_search_results = await self._prune_search_results(question, search_results, model)
    final_answer = await self._get_final_answer(question, pruned_search_results, model)
    return final_answer

  async def _get_queries(self, question, model):
    query_gen_chat = chat.ChatSession(QUERY_GENERATOR_PROMPT)
    res = await query_gen_chat.chat(question, model)
    return parse_query_response(res)

  async def _get_search_results(self, queries):
    tasks = [search.search_brave(q) for q in queries]
    search_results: list[list[search.SearchResult]] = await asyncio.gather(*tasks)
    return [x for y in search_results for x in y]

  async def _prune_search_results(self, question, search_results, model):
    user_question = f'<user_question>{question}</user_question>'
    tasks = []
    for res in search_results:
      xml_res = self.search_result_to_xml(res)
      prompt = f'{xml_res}\n{user_question}'
      cs = chat.ChatSession(RESULT_PRUNER_PROMPT)
      tasks.append(cs.chat(prompt, model))

    responses_list = await asyncio.gather(*tasks)
    pruned_results_list = []
    for i, response in enumerate(responses_list):
      match = re.search(r'<should_be_used>(.*?)</should_be_used>', response, re.DOTALL)
      if match:
        value = match.group(1).strip().lower()
        if value == 'true':
          pruned_results_list.append(search_results[i])

    return pruned_results_list


  async def _get_final_answer(self, question, search_results, model):
    search_results = [self.search_result_to_xml(x, indent=1) for x in search_results]
    context = '<context>\n' + '\n'.join(search_results) + '\n</context>'
    user_question = f'<user_question>{question}</user_question>'
    prompt = context + '\n' + user_question
    cs = chat.ChatSession(ANSWER_GENERATOR_PROMPT)
    response = await cs.chat(prompt, model)
    match = re.search(r'<final_answer>(.*?)</final_answer>', response, re.DOTALL)
    if match: return match.group(1).strip()
    return None


  def search_result_to_xml(self, res: search.SearchResult, indent=0):
    TAB = '  '
    ret = [f'{TAB*(indent)}<search_result']
    ret.append(f'{TAB*(indent+1)}<title>{res.title}</title>')
    ret.append(f'{TAB*(indent+1)}<url>{res.url}</url>')
    ret.append(f'{TAB*(indent+1)}<description>{res.description}</description>')
    if res.extra_snippets:
      ret.append(f'{TAB*(indent+1)}<extra_snippet>')
      for x in res.extra_snippets:
        ret.append(f'{TAB*(indent+2)}<snippet>{x}</snippet>')
      ret.append(f'{TAB*(indent+1)}</extra_snippet>')
    ret.append(f'{TAB*(indent)}</search_result>')
    return '\n'.join(ret)

#
#
# how to handle rate limiting with async await? i have rate limit on cs.chat function call
# You need to add rate limiting to your async calls to prevent too many concurrent requests. Here's a simple solution using a semaphore:
#
# ```python
# import asyncio
#
# class SearchSession:
#   def __init__(self, max_concurrent_requests=3):
#     self.semaphore = asyncio.Semaphore(max_concurrent_requests)
#   
#   async def rate_limited_call(self, func, *args, **kwargs):
#     async with self.semaphore:
#       return await func(*args, **kwargs)
#   
#   # Then modify your methods to use rate_limited_call
#   
#   async def _prune_search_results(self, question, search_results, model):
#     user_question = f'<user_question>{question}</user_question>'
#     tasks = []
#     for res in search_results:
#       xml_res = self.search_result_to_xml(res)
#       prompt = f'{xml_res}\n{user_question}'
#       cs = chat.ChatSession(RESULT_PRUNER_PROMPT)
#       tasks.append(self.rate_limited_call(cs.chat, prompt, model))
#     
#     responses_list = await asyncio.gather(*tasks)
#     # rest of your code remains the same
# ```
#
# Apply this pattern to all methods that call `cs.chat`. Adjust `max_concurrent_requests` based on your API limits.
