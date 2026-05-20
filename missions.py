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
        ("drive", -360, -360),
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
        ("drive", 210.0, 0),      # linkes Rad 1 Umdrehung vorwärts
        ("drive", 0, 210.0),      # rechtes Rad 1 Umdrehung vorwärts
    ],
}
