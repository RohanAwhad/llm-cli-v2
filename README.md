This is a cli based tool for ai-based search and answer. I didn't want to use perplexity because:

1. They take $20, which is lot for me. Gemini-flash with current search session can do 4000 queries for me at the same cost
2. Their base model hallucinates a lot. And their normal search is useless. Their Pro search is the only one, which is slightly usable.
3. Deep-Research is just a bit better than Pro. Frankly, I would rather just plan out the steps on my own, and then ask follow-up questions.
4. Reasoning-based search. This is by my understanding an explicit option during pro search. This gets way better results, because they use reasoning models, underneath. R1 is the best one, and i would rather just select r1 by myself.

But in all of this, the main reason i dont like is hallucination. Perplexity models, and lot of the models they use hallucinate a ton. I dont know which one hallucinates less, but based on no sort of scientific, purely observational study, 4o is very good at "Not Hallucinating".

According to Vectara's Hallucination Leaderboard (https://huggingface.co/spaces/vectara/leaderboard), Gemini-2.0-flash-001 hallucinates the least, so using that for now.

In-future, i would like to use my own model, which will cost $0, but for now this is it!

Right now it only has a Single Search mechanism.

You can skip logging, and simply run the following:
```bash
# first setup GEMINI_API_KEY
export GEMINI_API_KEY="..."
```
Then run main
```bash
uv sync
uv run main.py
```
