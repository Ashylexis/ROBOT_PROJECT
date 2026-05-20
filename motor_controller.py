# file: motor_controller.py

from machine import Pin, PWM
import math
import time
from smartstepper import SmartStepper
from config import (
    CANNON_SERVO_PINS,
    ANGLE_SERVO_PIN,
    SERVO_FREQUENCY_HZ,
    WHEEL_DIAMETER_MM,
    TRACK_WIDTH_MM,
    STEPPER_MICRO,
    STEPPER_MIN_SPEED,
    STEPPER_MAX_SPEED,
    STEPPER_ACCELERATION,
    GUN_GEAR_RATIO,
)
from missions import missions

print("motor_controller geladen")

# === SERVO SETUP ===
servos = []
states = [False, False, False, False]

# === BUTTON SERVOS ===
for pin in CANNON_SERVO_PINS:
    pwm = PWM(Pin(pin))
    pwm.freq(SERVO_FREQUENCY_HZ)
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


def calibrate_servos():
    print("Kalibriere Servos: öffnen und schließen")
    for idx, servo in enumerate(servos):
        states[idx] = True
        set_servo(servo, 90)
    time.sleep(0.5)
    for idx, servo in enumerate(servos):
        states[idx] = False
        set_servo(servo, 0)
    time.sleep(0.1)

# === STEPPER SETUP (NEMA17) ===
class StepperWrapper:
    def __init__(self, name, step, direction, micro=STEPPER_MICRO):
        self.stepper = SmartStepper(stepPin=step, dirPin=direction, accelCurve='smooth2')
        self.micro = micro
        self.stepper.minSpeed = STEPPER_MIN_SPEED
        self.stepper.maxSpeed = STEPPER_MAX_SPEED
        self.stepper.acceleration = STEPPER_ACCELERATION

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
    motor_R = StepperWrapper("Rechts", step=26, direction=18)
    motor_R.stepper.reverse = False  # Versuche reverse wieder
    motor_R.set_wheel(WHEEL_DIAMETER_MM)

    motor_L = StepperWrapper("Links", step=19, direction=20)
    motor_L.stepper.reverse = True
    motor_L.set_wheel(WHEEL_DIAMETER_MM)

    motor_E = StepperWrapper("Gun", step=21, direction=22)
    motor_E.stepper.reverse = False
    motor_E.set_degrees(GUN_GEAR_RATIO)
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
# Jede Mission ist eine Folge von Aktionen wie drive, turn, gun, fire und delay.


def turn_degrees(degrees):
    # Positive Werte drehen nach rechts, negative nach links.
    circumference = math.pi * TRACK_WIDTH_MM
    distance = (circumference * degrees) / 360.0
    motor_L.stepper.moveTo(distance, relative=True)
    motor_R.stepper.moveTo(-distance, relative=True)
    print(f"Drehe {degrees}° -> {distance:.1f}mm")


class MissionExecutor:
    def __init__(self):
        self.reset()

    def reset(self):
        self.mission_id = None
        self.steps = None
        self.step_index = 0
        self.current_action = None
        self.wait_until = None
        self.running = False

    def start(self, mission_id):
        if mission_id not in missions:
            print("Mission nicht gefunden", mission_id)
            return False
        self.mission_id = mission_id
        self.steps = missions[mission_id]
        self.step_index = 0
        self.current_action = None
        self.wait_until = None
        self.running = True
        print(f"Mission gestartet: {mission_id}")
        return True

    def stop(self):
        self.reset()

    def is_running(self):
        return self.running

    def step(self):
        if not self.running or self.steps is None:
            return

        now = time.ticks_ms()

        if self.current_action == "delay":
            if self.wait_until is None or time.ticks_diff(now, self.wait_until) < 0:
                return
            self.current_action = None
            self.wait_until = None
            self.step_index += 1

        elif self.current_action == "fire":
            if self.wait_until is None or time.ticks_diff(now, self.wait_until) < 0:
                return
            self.current_action = None
            self.wait_until = None
            self.step_index += 1

        elif self.current_action == "gun":
            if motor_E.stepper.moving:
                return
            self.current_action = None
            self.step_index += 1

        elif self.current_action in ["drive", "turn"]:
            if motor_L.stepper.moving or motor_R.stepper.moving:
                return
            self.current_action = None
            self.step_index += 1

        while self.step_index < len(self.steps):
            step = self.steps[self.step_index]
            action = step[0]

            if action == "drive":
                motor_L.stepper.moveTo(step[1], relative=True)
                motor_R.stepper.moveTo(step[2], relative=True)
                self.current_action = "drive"
                return

            elif action == "turn":
                turn_degrees(step[1])
                self.current_action = "turn"
                return

            elif action == "gun":
                set_gun_angle(step[1])
                self.current_action = "gun"
                return

            elif action == "fire":
                toggle_servo(step[1])
                self.wait_until = time.ticks_add(now, 500)
                self.current_action = "fire"
                return

            elif action == "delay":
                self.wait_until = time.ticks_add(now, step[1])
                self.current_action = "delay"
                return

            else:
                print("Unbekannte Missionsaktion:", action)
                self.step_index += 1

        print(f"Mission beendet: {self.mission_id}")
        self.reset()


mission_executor = MissionExecutor()


def start_mission(mission_id):
    return mission_executor.start(mission_id)


def step_mission():
    mission_executor.step()


def execute_mission(mission_id):
    print("execute_mission ist veraltet, nutze start_mission()")
    start_mission(mission_id)
