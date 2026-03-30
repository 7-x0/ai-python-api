from ai import ask

def should_speak(history):
    res = ask([
        {"role":"system","content":"should AI speak? yes/no"},
        {"role":"user","content":str(history)}
    ])
    return "yes" in res.lower()

def generate_topic():
    return ask([
        {"role":"system","content":"generate interesting topic Arabic"}
    ])