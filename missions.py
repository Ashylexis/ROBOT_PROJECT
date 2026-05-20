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
        ("drive", -100, -100), 
        ("gun", 180),
        ("turn", 360),
        ("gun", 90),
        ("turn", 1900),
        ("gun", 45),

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
        ("drive", 360, 360),
        ("turn", 90), 
        #Ueber die Brücke fahren
        ("gun", 180),
        ("drive", 1200, 1200), 
("drive", -50, -50),
("turn", 90+360),
        ("drive", 350, 350), 
        ("drive", -100, -100), 
        ("turn", 360),
        ("gun", 90),
        ("turn", 900),
        ("gun", 45),
        ("turn", 900),

                ],
}
