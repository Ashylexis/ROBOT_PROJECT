# file: motor_controller.py

from machine import Pin, PWM
import math
import time
from smartstepper import SmartStepper
from config import CANNON_SERVO_PINS, ANGLE_SERVO_PIN
from missions import missions

print("motor_controller geladen")

# === SERVO SETUP ===
servos = []
states = [False, False, False, False]

# === BUTTON SERVOS ===
for pin in CANNON_SERVO_PINS:
    pwm = PWM(Pin(pin))
    pwm.freq(50)
    servos.append(pwm)

def set_servo(servo, angle):
    angle = max(0, min(90, angle))
    min_duty = 2000
    max_duty = 8000
    duty = int(min_duty + (angle / 90) * (max_duty - min_duty))
    servo.duty_u16(duty)

def toggle_servo(servo_num):
    index = servo_num - 1
    if 0 <= index < len(servos):
        states[index] = not states[index]
        angle = 90 if states[index] else 0
        set_servo(servos[index], angle)
        print(f"Servo {servo_num} -> {angle}°")

def load_guns():
    print("Lade Guns")
    for idx, servo in enumerate(servos):
        states[idx] = True
        set_servo(servo, 90)
    time.sleep(1)

# === STEPPER SETUP (NEMA17) ===
class StepperWrapper:
    def __init__(self, name, step, direction, micro=16):
        self.stepper = SmartStepper(stepPin=step, dirPin=direction, accelCurve='smooth2')
        self.micro = micro
        self.stepper.minSpeed = 2
        self.stepper.maxSpeed = 200
        self.stepper.acceleration = 50

    @property
    def position(self):
        """Delegiert an SmartStepper.position (wird von main.py für Status gebraucht)"""
        return self.stepper.position

    def set_wheel(self, dia):
        # Berechnet Schritte pro mm
        self.stepper.stepsPerUnit = (200 * self.micro) / (math.pi * dia)

    def set_degrees(self, gear_ratio):
        # Berechnet Schritte pro Grad
        self.stepper.stepsPerUnit = (200 * self.micro * gear_ratio) / 360.0

# Initialisierung der 3 Motoren
try:
    motor_R = StepperWrapper("Rechts", step=17, direction=18)
    motor_R.stepper.reverse = False  # Versuche reverse wieder
    motor_R.set_wheel(67)

    motor_L = StepperWrapper("Links", step=19, direction=20)
    motor_L.stepper.reverse = True
    motor_L.set_wheel(67)

    motor_E = StepperWrapper("Gun", step=21, direction=22)
    motor_E.stepper.reverse = False
    motor_E.set_degrees(5)
    print("Stepper erfolgreich initialisiert")
except Exception as e:
    print("PIO Fehler: Versuche STRG+D in Thonny", e)

def move_robot(cmd):
    dist = 50 # 50mm pro Klick
    if cmd == "up":
        motor_R.stepper.moveTo(dist, relative=True)
        motor_L.stepper.moveTo(dist, relative=True)
    elif cmd == "down":
        motor_R.stepper.moveTo(-dist, relative=True)
        motor_L.stepper.moveTo(-dist, relative=True)
    elif cmd == "left":
        motor_L.stepper.moveTo(-dist, relative=True)
        motor_R.stepper.moveTo(dist, relative=True)
    elif cmd == "right":
        motor_L.stepper.moveTo(dist, relative=True)
        motor_R.stepper.moveTo(-dist, relative=True)

def set_gun_angle(angle):
    # Nutzt den Slider-Wert (0-90) für den Gun-Stepper
    print(f"Gun Stepper -> {angle}°")
    motor_E.stepper.moveTo(float(angle))

# Die Missionslogik bleibt als Tabelle in missions.py.
# Jede Mission ist eine Folge von Aktionen wie drive, gun und fire.

def execute_mission(mission_id):
    if mission_id not in missions:
        print("Mission nicht gefunden")
        return
    
    steps = missions[mission_id]
    print(f"Starte Mission: {mission_id}")
    
    for step in steps:
        action = step[0]
        
        if action == "drive":
            motor_L.stepper.moveTo(step[1], relative=True)
            motor_R.stepper.moveTo(step[2], relative=True)
            # Warten bis Fahrt beendet, damit Befehle nacheinander kommen
            while motor_L.stepper.moving or motor_R.stepper.moving:
                pass 
                
        elif action == "gun":
            set_gun_angle(step[1])
            while motor_E.stepper.moving: pass
            
        elif action == "fire":
            toggle_servo(step[1])
            time.sleep(0.5) # Kurze Pause für die Servo-Bewegung