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
        ("drive", 0, 150),      # Kurve fahren
        ("gun", 15),
        ("fire", 3),
    ],

    "p3": [
        ("drive", 100, 100),     # vorwärts 100 mm
        ("drive", 141, -141),    # 90° rechts drehen
        ("drive", 513, 513),     # weiter vorwärts
        ("gun", 45),             # Kanone auf 45° anheben
        ("fire", 1),             # Servo 1 auslösen
        ("drive", -50, -50),     # zurückfahren
        ("fire", 2),             # Servo 2 auslösen
    ],
}
