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
