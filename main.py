# file: main.py
 
import socket
import time
import machine
import motor_controller
from robot_state import RobotStateMachine, RobotState
from config import PROGRAM_SWITCH_PINS, START_SWITCH_PIN, RESET_SWITCH_PIN, LOAD_GUNS_MODE_PIN
from wifi_setup import start_access_point
from web_page import webpage


class LedBlinker:
    def __init__(self, pin_name="LED"):
        self.pin = None
        self.state = 0
        self.last_toggle = time.ticks_ms()
        self.interval_ms = 500
        try:
            self.pin = machine.Pin(pin_name, machine.Pin.OUT)
        except Exception:
            try:
                self.pin = machine.Pin(25, machine.Pin.OUT)
            except Exception:
                self.pin = None
        if self.pin:
            self.pin.value(0)

    def set_rate(self, frequency_hz):
        if frequency_hz and frequency_hz > 0:
            self.interval_ms = int(500 / frequency_hz)
        else:
            self.interval_ms = 500

    def tick(self):
        if not self.pin:
            return
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_toggle) >= self.interval_ms:
            self.state ^= 1
            self.pin.value(self.state)
            self.last_toggle = now


print("Main gestartet")
 
# === LED für Startup und Idle ===
led = LedBlinker()
led.set_rate(5)

# === WIFI STARTEN ===
robot = RobotStateMachine()
robot.transition_to(RobotState.STARTUP)
start_access_point(status_callback=led.tick)
robot.startup_complete()

program_pins = [machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP) for pin in PROGRAM_SWITCH_PINS]
start_pin = machine.Pin(START_SWITCH_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
reset_pin = machine.Pin(RESET_SWITCH_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
load_guns_mode_pin = machine.Pin(LOAD_GUNS_MODE_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
# Im LoadGuns-Modus: Pins 6,7,8,9 steuern Servos (program_pins + start_pin + reset_pin)
all_servo_pins = program_pins + [start_pin, reset_pin]
PROGRAM_MAP = {0: None, 1: 'p1', 2: 'p2', 3: 'p3'}


 
# === SERVER ===
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

server = socket.socket()
server.bind(addr)
server.listen(1)
server.settimeout(0.05)
print("Server läuft auf Port 80...")

# Nach Abschluss des Startups in Idle-Modus wechseln
led.set_rate(1)
 
 
def send_in_chunks(client, data, chunk_size=1024):
    """Sendet grosse Daten in kleinen Stücken (wichtig auf MicroPython!)"""
    if isinstance(data, str):
        data = data.encode("utf-8")
    pos = 0
    while pos < len(data):
        client.send(data[pos:pos + chunk_size])
        pos += chunk_size
 
 
def read_gpio(pin):
    return pin.value() == 0


def read_program_code():
    code = 0
    for idx, pin in enumerate(program_pins):
        if read_gpio(pin):
            code |= 1 << idx
    return code


def get_status():
    try:
        x = motor_controller.motor_L.position
        y = motor_controller.motor_R.position
        r = motor_controller.motor_E.position
        state = robot.state
        program = PROGRAM_MAP.get(read_program_code()) or 'none'
        start_on = 'ON' if read_gpio(start_pin) else 'OFF'
        reset_on = 'ON' if read_gpio(reset_pin) else 'OFF'
        load_guns_on = 'ON' if read_gpio(load_guns_mode_pin) else 'OFF'
        servo_states = ''.join(['1' if read_gpio(pin) else '0' for pin in all_servo_pins])
        return "{}|{:.1f}|{:.1f}|{:.1f}|{}|{}|{}|{}|{}".format(
            state, x, y, r, program, start_on, reset_on, load_guns_on, servo_states)
    except Exception as e:
        print("get_status Fehler:", e)
        return "idle|0.0|0.0|0.0|none|OFF|OFF|OFF|0000"
 
 
def handle_post(post_data):
    print("POST empfangen:", repr(post_data))
 
    # 1. Slider
    if post_data.startswith("slider="):
        try:
            angle = int(post_data.split("=")[1])
            print("Slider:", angle)
            motor_controller.set_gun_angle(angle)
        except Exception as e:
            print("Slider Fehler:", e)
 
    # 2. Commands
    elif post_data.startswith("cmd="):
        cmd = post_data.split("=")[1].strip()
        print("CMD:", cmd)
 
        if cmd in ["p1", "p2", "p3"]:
            if robot.state != RobotState.IDLE:
                print("Programmauswahl nur im Idle möglich")
            elif robot.select_mission(cmd):
                print("Mission ausgewählt:", cmd)
                if robot.start_fight():
                    print("Mission startet direkt:", cmd)
                    return cmd
                else:
                    print("Mission konnte nicht gestartet")
            else:
                print("Mission nicht gefunden:", cmd)
        elif cmd == "start":
            if robot.state != RobotState.IDLE:
                print("Start nur im Idle möglich")
            elif robot.selected_mission:
                print("Mission bereit:", robot.selected_mission)
                return robot.selected_mission
            else:
                print("Keine Mission ausgewählt!")
 
        elif cmd == "load_guns":
            if robot.load_guns():
                print("Guns geladen")

        elif cmd == "reset":
            print("Reset to Idle")
            robot.reset()

        elif cmd == "status":
            print("Status abgefragt")

        elif cmd in ["up", "down", "left", "right"]:
            try:
                motor_controller.move_robot(cmd)
                print("move_robot OK")
            except Exception as e:
                print("move_robot Fehler:", e)
 
        elif cmd.startswith("s") and len(cmd) == 2:
            try:
                num = int(cmd[1])
                motor_controller.toggle_servo(num)
                print("Servo OK:", num)
            except Exception as e:
                print("Servo Fehler:", e)
 
        elif cmd == "reset_all":
            robot.emergency_stop()
 
        else:
            print("Unbekannter CMD:", cmd)
 
    else:
        print("Unbekanntes POST-Format:", post_data)
 
    return None
 
 
while True:
    led.tick()
    motor_controller.step_mission()
    robot.update()

    load_guns_mode_on = read_gpio(load_guns_mode_pin)

    if load_guns_mode_on:
        # === LOAD GUNS MODUS: Servos mit Pins 6,7,8,9 steuern ===
        for idx, pin in enumerate(all_servo_pins):
            if idx < 4:  # Nur 4 Servos
                gun = motor_controller.guns[idx]
                servo_on = read_gpio(pin)
                if servo_on:
                    gun.fire()  # Servo offen (90°)
                else:
                    gun.stop()  # Servo zu (0°)
    else:
        # === NORMALER MODUS: Mission-Steuerung ===
        program_code = read_program_code()
        selected_program = PROGRAM_MAP.get(program_code)
        start_on = read_gpio(start_pin)
        reset_on = read_gpio(reset_pin)

        if reset_on:
            print("Reset-Schalter ist ON, setze zurück")
            robot.reset()
        elif robot.state == RobotState.IDLE:
            if selected_program and selected_program != robot.selected_mission:
                robot.select_mission(selected_program)
                print("Physische Programmauswahl:", selected_program)

            if robot.selected_mission and start_on:
                print("Start-Schalter ist ON und Mission ausgewählt, starte jetzt")
                if robot.start_fight():
                    print("Mission startet physisch:", robot.selected_mission)
                else:
                    print("Startversuch fehlgeschlagen")

    client = None
    try:
        client, client_addr = server.accept()
    except OSError:
        continue

    try:
        print("Verbindung von:", client_addr)
        request = client.recv(2048).decode("utf-8", "ignore")
 
        if not request:
            client.close()
            continue
 
        # Browser sendet zuerst OPTIONS-Request (CORS preflight) — einfach bestätigen
        if request.startswith("OPTIONS"):
            client.send(
                "HTTP/1.1 204 No Content\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: POST, GET\r\n"
                "Access-Control-Allow-Headers: Content-Type\r\n"
                "Connection: close\r\n"
                "\r\n"
            )
 
        # === GET: Webseite in Chunks senden ===
        elif request.startswith("GET"):
            print("GET -> sende Webseite")
            html = webpage()
            header = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Content-Length: {}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).format(len(html.encode("utf-8")))
            client.send(header.encode())
            send_in_chunks(client, html)
 
        # === POST: Befehl verarbeiten ===
        elif request.startswith("POST"):
            if "\r\n\r\n" in request:
                headers, body = request.split("\r\n\r\n", 1)
            else:
                headers, body = request, ""
 
            content_length = 0
            for line in headers.split("\r\n"):
                if "content-length" in line.lower():
                    try:
                        content_length = int(line.split(":")[1].strip())
                    except Exception:
                        pass
 
            while len(body) < content_length:
                chunk = client.recv(256).decode("utf-8", "ignore")
                if not chunk:
                    break
                body += chunk
 
            post_data = body[:content_length]
            mission_to_run = handle_post(post_data)
 
            # Antwort SOFORT senden (mit CORS-Header damit Safari nicht blockiert!)
            status = get_status()
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Content-Length: {}\r\n"
                "Connection: close\r\n"
                "\r\n"
                "{}"
            ).format(len(status), status)
            client.send(response.encode())
            client.close()
 
            # Mission NACH dem Senden ausfuehren
            if mission_to_run:
                print("Starte Mission:", mission_to_run)
                robot.start_fight()
 
    except Exception as e:
        print("Fehler im Loop:", e)
    finally:
        if client:
            try:
                client.close()
            except Exception as close_error:
                print("Fehler beim Schließen des Clients:", close_error)