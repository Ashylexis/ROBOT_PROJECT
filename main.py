# file: main.py
 
import socket
import time
import machine
import motor_controller
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
start_access_point(status_callback=led.tick)
 
# === Servo-Test beim Start ===
print("Servos:", motor_controller.servos)
motor_controller.set_servo(motor_controller.servos[0], 90)

selected_mission = None
 
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
 
 
def get_status():
    try:
        x = motor_controller.motor_L.position
        y = motor_controller.motor_R.position
        r = motor_controller.motor_E.position
        return "{:.1f}|{:.1f}|{:.1f}".format(x, y, r)
    except Exception as e:
        print("get_status Fehler:", e)
        return "0.0|0.0|0.0"
 
 
def handle_post(post_data):
    global selected_mission
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
            selected_mission = cmd
            print("Mission vorgewaehlt:", cmd)
 
        elif cmd == "start":
            if selected_mission:
                print("Mission bereit:", selected_mission)
                return selected_mission
            else:
                print("Keine Mission ausgewaehlt!")
 
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
            print("NOT-AUS!")
            try:
                motor_controller.motor_L.stepper.stop(emergency=True)
                motor_controller.motor_R.stepper.stop(emergency=True)
                motor_controller.motor_E.stepper.stop(emergency=True)
            except Exception as e:
                print("Stop Fehler:", e)
 
        else:
            print("Unbekannter CMD:", cmd)
 
    else:
        print("Unbekanntes POST-Format:", post_data)
 
    return None
 
 
while True:
    led.tick()
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
                    except:
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
                motor_controller.execute_mission(mission_to_run)
 
    except Exception as e:
        print("Fehler im Loop:", e)
    finally:
        if client:
            try:
                client.close()
            except:
                pass