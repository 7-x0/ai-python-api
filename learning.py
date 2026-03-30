from ai import ask
import json

def extract_memory(text):
    try:
        res = ask([
            {
                "role": "system",
                "content": """
Extract important memory ONLY if useful.

Return JSON:
{
 "type": "interest / relation / fact / none",
 "content": "...",
 "importance": 1-10
}

If not important → type = none
"""
            },
            {"role": "user", "content": text}
        ])

        data = json.loads(res)

        if data["type"] == "none":
            return None

        if data["importance"] < 5:
            return None

        return data

    except:
        return None