import os
from dotenv import load_dotenv
from openai import OpenAI
from utils import cache_key, cache_get, cache_set

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

def ask(messages):
    k = cache_key(messages)
    c = cache_get(k)
    if c:
        return c

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        out = response.choices[0].message.content
        cache_set(k, out)
        return out

    except Exception as e:
        print(e)
        return "خطأ ❌"