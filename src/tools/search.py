from typing import Optional
import aiohttp
import asyncio
import os

from dataclasses import dataclass
from loguru import logger

@dataclass
class SearchResult:
  """
  Dataclass to represent the search results from Brave Search API.

  :param title: The title of the search result.
  :param url: The URL of the search result.
  :param description: A brief description of the search result.
  :param extra_snippets: Additional snippets related to the search result.
  """
  title: str
  url: str
  description: str
  extra_snippets: list

  def __str__(self) -> str:
    """
    Returns a string representation of the search result.

    :return: A string representation of the search result.
    """
    return (
        f"Title: {self.title}\n"
        f"URL: {self.url}\n"
        f"Description: {self.description}\n"
        f"Extra Snippets: {', '.join(self.extra_snippets)}\n"
    )


async def search_brave(query: str, count: int = 5, rate_limiter = None) -> list[SearchResult]:
  """
  Searches the web using Brave Search API and returns structured search results.

  :param query: The search query string.
  :param count: The number of search results to return.
  :return: A list of SearchResult objects containing the search results.
  """
  return [SearchResult(
    title='Test Title',
    url='https://example.com',
    description='This is a test result',
    extra_snippets=[],
  )]
  if not query:
    return []

  url: str = "https://api.search.brave.com/res/v1/web/search"
  headers: dict = {
      "Accept": "application/json",
      "X-Subscription-Token": os.environ.get('BRAVE_SEARCH_AI_API_KEY', '')
  }
  if not headers['X-Subscription-Token']:
    logger.error("Error: Missing Brave Search API key.")
    return []

  params: dict = {
      "q": query,
      "count": count
  }

  retries: int = 0
  max_retries: int = 3
  backoff_factor: int = 2

  async with aiohttp.ClientSession() as session:
    while retries < max_retries:
      try:
        if rate_limiter is not None: await rate_limiter.acquire(num_tokens=1)
        async with session.get(url, headers=headers, params=params) as response:
          response.raise_for_status()
          results_json = await response.json()
          logger.debug('Got results')
          break
      except aiohttp.ClientError as e:
        logger.exception(f"HTTP Request failed: {e}, retrying...")

      finally:
        retries += 1
        if retries < max_retries:
          await asyncio.sleep(backoff_factor ** retries)
        else:
          return []


  results: list[SearchResult] = []
  for item in results_json.get('web', {}).get('results', []):
    result = SearchResult(
        title=item.get('title', ''),
        url=item.get('url', ''),
        description=item.get('description', ''),
        extra_snippets=item.get('extra_snippets', []),
    )
    results.append(result)
  return results

