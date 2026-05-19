
from machine import Pin, PWM
import math
import time
from smartstepper import SmartStepper
from config import (
    CANNON_SERVO_PINS,
    SERVO_FREQUENCY_HZ,
    WHEEL_DIAMETER_MM,
    TRACK_WIDTH_MM,
    DRIVE_STEPPER_MICRO,
    DRIVE_STEPPER_MIN_SPEED,
    DRIVE_STEPPER_MAX_SPEED,
    DRIVE_STEPPER_ACCELERATION,
    GUN_STEPPER_MICRO,
    GUN_STEPPER_MIN_SPEED,
    GUN_STEPPER_MAX_SPEED,
    GUN_STEPPER_ACCELERATION,
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
    def __init__(self, name, step, direction, micro,
                 min_speed,
                 max_speed,
                 acceleration,
                 reverse):
        self.stepper = SmartStepper(stepPin=step, dirPin=direction, accelCurve='smooth2')
        self.micro = micro
        self.stepper.minSpeed = min_speed
        self.stepper.maxSpeed = max_speed
        self.stepper.acceleration = acceleration
        self.reverse = reverse

    @property
    def position(self):
        """Gibt die logische Position zurück (korrigiert Vorzeichen bei Invertierung)"""
        pos = self.stepper.position
        return -pos if self.reverse else pos

    def set_wheel(self, dia):
        # Berechnet Schritte pro mm
        self.stepper.stepsPerUnit = (200 * self.micro) / (math.pi * dia)

    def set_degrees(self, gear_ratio):
        # Berechnet Schritte pro Grad
        self.stepper.stepsPerUnit = (200 * self.micro * gear_ratio) / 360.0

    def move_to(self, target, relative=False):
        """Invertiert die Bewegung dynamisch auf Software-Ebene, falls nötig"""
        if self.reverse:
            target = -target
        self.stepper.moveTo(target, relative=relative)


# Initialisierung der 3 Motoren
try:
    motor_R = StepperWrapper(
        "Rechts",
        step=17,
        direction=18,
        micro=DRIVE_STEPPER_MICRO,
        min_speed=DRIVE_STEPPER_MIN_SPEED,
        max_speed=DRIVE_STEPPER_MAX_SPEED,
        acceleration=DRIVE_STEPPER_ACCELERATION,
        reverse=True
    )
    motor_R.set_wheel(WHEEL_DIAMETER_MM)

    motor_L = StepperWrapper(
        "Links",
        step=19,
        direction=20,
        micro=DRIVE_STEPPER_MICRO,
        min_speed=DRIVE_STEPPER_MIN_SPEED,
        max_speed=DRIVE_STEPPER_MAX_SPEED,
        acceleration=DRIVE_STEPPER_ACCELERATION,
        reverse=False
    )
    motor_L.set_wheel(WHEEL_DIAMETER_MM)

    motor_E = StepperWrapper(
        "Gun",
        step=21,
        direction=22,
        micro=GUN_STEPPER_MICRO,
        min_speed=GUN_STEPPER_MIN_SPEED,
        max_speed=GUN_STEPPER_MAX_SPEED,
        acceleration=GUN_STEPPER_ACCELERATION,
        reverse=False
    )
    motor_E.set_degrees(GUN_GEAR_RATIO)
    print("Stepper erfolgreich initialisiert")
except Exception as e:
    print("PIO Fehler: Versuche STRG+D in Thonny", e)

def move_robot(cmd):
    dist = 100 # 50mm pro Klick
    if cmd == "up":
        motor_L.move_to(dist, relative=True)
        motor_R.move_to(dist, relative=True)
    elif cmd == "down":
        motor_L.move_to(-dist, relative=True)
        motor_R.move_to(-dist, relative=True)
    elif cmd == "left":
        turn_degrees(-22.5) 
    elif cmd == "right":
        turn_degrees(22.5)  

def set_gun_angle(angle):
    print(f"Gun Stepper -> {angle}°")
    motor_E.move_to(float(angle))

def turn_degrees(degrees):
    circumference = math.pi * TRACK_WIDTH_MM
    distance = (circumference * degrees) / 360.0
    motor_L.move_to(distance, relative=True)
    motor_R.move_to(-distance, relative=True)
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
                motor_L.move_to(step[1], relative=True)
                motor_R.move_to(step[2], relative=True)
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

