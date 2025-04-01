import asyncio

# token-bucket algorithm
class RateLimiter:
  def __init__(self, rate: int, capacity: int):
    self.rate = rate # tokens per second
    self.capacity = capacity # max tokens in bucket
    self.tokens = capacity
    self.last_refill = asyncio.get_event_loop().time()

  async def acquire(self, num_tokens: int = 1):
    while True:
      self.refill()
      if self.tokens >= num_tokens:
        self.tokens -= num_tokens
        return
      await asyncio.sleep(0.1) # check every 100ms

  def refill(self):
    now = asyncio.get_event_loop().time()
    elapsed = now - self.last_refill
    new_tokens = elapsed * self.rate
    self.tokens = min(self.capacity, self.tokens + new_tokens)
    self.last_refill = now
