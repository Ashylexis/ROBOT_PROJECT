"""
servo_controller.py - Gun und Servo Klassen für die Kanonen
"""
from machine import Pin, PWM
from config import CANNON_SERVO_PINS, SERVO_FREQUENCY_HZ


class Servo:
    """Servo für eine Gun mit expliziten open/close Methoden"""
    def __init__(self, pwm_pin, frequency, inverted=False):
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(frequency)
        self.is_open = False
        self.inverted = inverted  # Wenn True: 0° = offen, 90° = geschlossen
    
    def open(self):
        """Öffnet die Gun (90° oder 0° wenn invertiert)"""
        if not self.is_open:
            angle = 0 if self.inverted else 90
            self._set_angle(angle)
            self.is_open = True
    
    def close(self):
        """Schließt die Gun (0° oder 90° wenn invertiert)"""
        if self.is_open:
            angle = 90 if self.inverted else 0
            self._set_angle(angle)
            self.is_open = False
    
    def _set_angle(self, angle):
        """Setzt den Winkel (0-90°)"""
        angle = max(0, min(90, angle))
        min_duty = 2000
        max_duty = 8000
        duty = int(min_duty + (angle / 90) * (max_duty - min_duty))
        self.pwm.duty_u16(duty)


class Gun:
    """Eine Gun mit integrierter Servo-Kontrolle"""
    def __init__(self, gun_num, servo_pin, frequency, inverted=False):
        self.gun_num = gun_num
        self.servo = Servo(servo_pin, frequency, inverted=inverted)
    
    def fire(self):
        """Feuert die Gun (öffnet den Servo)"""
        print(f"Gun {self.gun_num} feuert")
        self.servo.open()
    
    def stop(self):
        """Stoppt die Gun (schließt den Servo)"""
        print(f"Gun {self.gun_num} stoppt")
        self.servo.close()
    
    def is_loaded(self):
        """Prüft, ob die Gun geladen ist"""
        return self.servo.is_open


# === GUN INSTANCES ===
# Guns 2 und 3 sind invertiert (andersherum eingebaut)
guns = [
    Gun(1, CANNON_SERVO_PINS[0], SERVO_FREQUENCY_HZ, inverted=False),
    Gun(2, CANNON_SERVO_PINS[1], SERVO_FREQUENCY_HZ, inverted=True),   # Invertiert
    Gun(3, CANNON_SERVO_PINS[2], SERVO_FREQUENCY_HZ, inverted=True),   # Invertiert
    Gun(4, CANNON_SERVO_PINS[3], SERVO_FREQUENCY_HZ, inverted=False),
]

# Compatibility aliases für alte Code
servos = [gun.servo for gun in guns]


def toggle_servo(gun_num):
    """Compatibility Funktion: Togglet den Servo (open/close)"""
    gun = guns[gun_num - 1]
    if gun.servo.is_open:
        gun.stop()
    else:
        gun.fire()


def load_guns():
    """Lädt alle Guns (öffnet alle Servos)"""
    print("Lade Guns")
    for gun in guns:
        gun.fire()


def calibrate_servos():
    """Kalibriert die Servos: öffnen, warten, schließen"""
    import time
    print("Kalibriere Servos")
    for gun in guns:
        gun.fire()
    time.sleep(0.5)
    for gun in guns:
        gun.stop()
    time.sleep(0.1)
