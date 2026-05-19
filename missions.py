# Mission table definitions for ROBOT_PROJECT

missions = {
    "p1": [
        ("turn", 90),    
        ("drive", 600, 600),            
        ("fire", 1),
        ("fire", 2),
        ("fire", 3),
        ("fire", 4), 
        ("turn", 90),
        ("drive", 500, 500), 
        ("turn", 90), 
        ("drive", -50, -50),          
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
