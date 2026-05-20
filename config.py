# file: config.py

# === WIFI ===

SSID_AP = "MeinRoboter"
PASSWORD_AP = "Robo1234"

# === SERVO ===

CANNON_SERVO_PINS = [2, 3, 4, 5]
SERVO_FREQUENCY_HZ = 50

# === PHYSIKALISCHE SCHALTER ===
# Die Schalter ziehen die Pins im EIN-Zustand auf 0V (aktive LOW-Schaltung).
PROGRAM_SWITCH_PINS = [6, 7]  # Im normalen Modus: Programmauswahl (00=none, 01=p1, 10=p2, 11=p3)
START_SWITCH_PIN = 8           # Im normalen Modus: Mission starten
RESET_SWITCH_PIN = 9           # Im normalen Modus: Reset
LOAD_GUNS_MODE_PIN = 10        # Wenn ON: Servo-Modus aktivieren (Pins 6,7,8,9 steuern dann Servos 1-4)

# Im LoadGuns-Modus werden diese Pins umfunktioniert:
# Pin 6 -> Servo 1 (Gun 1)
# Pin 7 -> Servo 2 (Gun 2)
# Pin 8 -> Servo 3 (Gun 3)
# Pin 9 -> Servo 4 (Gun 4)

# === STEPPER PHYSIK ===

WHEEL_DIAMETER_MM = 67 + 3.4
TRACK_WIDTH_MM = 120

# Drive stepper parameters
DRIVE_STEPPER_MICRO = 16
DRIVE_STEPPER_MIN_SPEED = 5
DRIVE_STEPPER_MAX_SPEED = 200
DRIVE_STEPPER_ACCELERATION = 200

# Gun stepper parameters
GUN_STEPPER_MICRO = 16
GUN_STEPPER_MIN_SPEED = 5
GUN_STEPPER_MAX_SPEED = 100
GUN_STEPPER_ACCELERATION = 100


GUN_GEAR_RATIO = 5

# === POSITIONEN ===

POS_0 = 0
POS_90 = 90