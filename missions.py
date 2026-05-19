# Mission table definitions for ROBOT_PROJECT

missions = {
    "p1": [
        ("drive", 100, 100),    # 100 mm forward
        ("gun", 45),            # Kanone auf 45° stellen
        ("fire", 1),            # Servo 1 auslösen
        ("drive", -50, -50),    # 50 mm zurück
        ("fire", 2),            # Servo 2 auslösen
    ],

    "p2": [
        ("drive", 100, 100),      # 100mm vorwärts
        ("turn", 360),            # 360° nach rechts drehen
        ("turn", -360),           # 360° nach links drehen
        ("gun", 90),              # Guns auf 90° heben
        ("fire", 1),
        ("delay", 1000),          # 1 Sekunde warten
        ("fire", 2),
        ("delay", 1000),
        ("fire", 3),
        ("delay", 1000),
        ("fire", 4),
    ],

    "p3": [
        ("drive", 210.0, 0),      # linkes Rad 1 Umdrehung vorwärts
        ("drive", 0, 210.0),      # rechtes Rad 1 Umdrehung vorwärts
    ],
}
