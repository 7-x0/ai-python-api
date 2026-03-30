def track_event(mem, event):
    if "events" not in mem:
        mem["events"] = []

    mem["events"].append(event)


def get_recent_events(mem):
    return mem.get("events", [])[-10:]