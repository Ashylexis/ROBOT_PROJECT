# Mission table definitions for ROBOT_PROJECT

try:
    import uos as os
except ImportError:
    import os

try:
    import ujson as json
except ImportError:
    import json

MISSIONS_FILE = "missions.json"

DEFAULT_MISSIONS = {
    "p1": [
        ["drive", 100, 100],
        ["gun", 45],
        ["fire", 1],
        ["drive", -50, -50],
        ["fire", 2],
    ],
    "p2": [
        ["drive", 100, 100],
        ["turn", 360],
        ["turn", -360],
        ["gun", 90],
        ["fire", 1],
        ["delay", 1000],
        ["fire", 2],
        ["delay", 1000],
        ["fire", 3],
        ["delay", 1000],
        ["fire", 4],
    ],
    "p3": [
        ["drive", 210.0, 0],
        ["drive", 0, 210.0],
    ],
}


def load_missions():
    try:
        with open(MISSIONS_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception as e:
        print("missions.load_missions fehlgeschlagen:", e)
    return DEFAULT_MISSIONS.copy()


def save_missions(text):
    try:
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise ValueError("Missions müssen als Dictionary mit Missions-IDs gespeichert werden.")
        with open(MISSIONS_FILE, 'w') as f:
            json.dump(parsed, f)
        global missions
        missions = parsed
        return True
    except Exception as e:
        print("missions.save_missions fehlgeschlagen:", e)
        return False


def json_dump():
    try:
        return json.dumps(missions)
    except Exception as e:
        print("missions.json_dump fehlgeschlagen:", e)
        return "{}"


missions = load_missions()
