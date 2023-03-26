import json


def parse(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Log file not found")
        return None


def update(path, dict):
    with open(path, "w") as f:
        json.dump(dict, f, indent=1)
