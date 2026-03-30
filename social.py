from ai import ask

def update_relationships(mem, text):
    try:
        res = ask([
            {
                "role": "system",
                "content": """
Detect relationships between users.

Return JSON:
{ "user1": "...", "user2": "...", "type": "friend" }
"""
            },
            {"role": "user", "content": text}
        ])

        if "{" in res:
            mem.setdefault("relations", []).append(res)

    except:
        pass


def get_relations(mem):
    return mem.get("relations", [])[-5:]