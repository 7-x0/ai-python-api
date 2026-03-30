from ai import ask

def should_intervene(text):
    res = ask([
        {
            "role": "system",
            "content": "should AI join this conversation? yes/no"
        },
        {
            "role": "user",
            "content": text
        }
    ])

    return "yes" in res.lower()