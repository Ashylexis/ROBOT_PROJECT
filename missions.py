# Mission table definitions for ROBOT_PROJECT

missions = {
      "p1": [
        ("gun", 45),
        ("turn", 90),    
        ("drive", 600, 600),  
        ("gun", 10),          
        ("fire", 1),
        ("turn", -2),  
        ("fire", 2),
        ("fire", 3),
        ("turn", -2),
        ("fire", 4),
        # Vor dem Fluss warten nach dem schiessen und neu ausrichten
        ("turn", -86),
        ("drive", 50, 50), 
("turn", 180),
("drive", 70, 70),
        ("drive", -350, -350),
        ("turn", -90), 
        #Vor der brücke warten
        ("drive", 1200, 1200), 
("drive", -50, -50),
("turn", 90),
        ("drive", 350, 350), 

                ],
    "p2": [
        ("gun", 90),
        ("drive", 1000, 1000),      # 100mm vorwärts
        ("delay", 3000),            # 1 Sekunde warten
        ("turn", 90),            # 360° nach rechts drehen
        ("turn", 90),            # 360° nach rechts drehen
        ("turn", 90),            # 360° nach rechts drehen
        ("turn", 90),            # 360° nach rechts drehen
        ("turn", -360),           # 360° nach links drehen
        ("drive", -1000, -1000),      # 100mm vorwärts

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
