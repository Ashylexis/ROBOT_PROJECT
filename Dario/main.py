# Bibliotheken laden
import network
import machine
import socket
import rp2
import time
from servo import Servo
from grove_rgb_lcd import RgbLcd

print("Altes main von Dario gestartet")

# Onboard-LED initialisieren
led = machine.Pin('LED', machine.Pin.OUT)

# Servo initialisieren
servo = Servo(machine.Pin(16))
servo_angle = 0  # Aktuelle Position speichern

def set_servo_angle(angle):
    global servo_angle
    servo_angle = angle
    servo.set_angle(angle)

# I2C und Grove LCD initialisieren (GPIO 4 und 5)
try:
    i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4), freq=400000)
    lcd = RgbLcd(i2c)
    lcd.clear()
    lcd.set_rgb(255, 0, 0)  # Rot
    print('LCD initialisiert')
except Exception as e:
    print('LCD Fehler:', e)
    lcd = None
    
# I2C Scan
print('I2C Scan:')
devices = i2c.scan()
print('Gefundene I2C Geräte:', [hex(device) for device in devices])

# WLAN-Konfiguration
wlanSSID = 'Dotspot'
wlanPW = 'qwerty99'
network.country('CH')

# HTML-Datei
html = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="shortcut icon" href="data:"><title>Raspberry Pi Pico W</title><style>input[type='range'] { width: 300px; height: 10px; }</style></head><body><h1 align="center">Hi, I'am your Raspberry Pi Pico W</h1><hr>TEXT<hr><p align="center">DEMO von Elektronik-Kompendium.de</p></body></html>"""

# Funktion: WLAN-Verbindung
def wlanConnect():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('WLAN-Verbindung herstellen')
        wlan.config(pm = 0xa11140)
        wlan.active(True)
        wlan.connect(wlanSSID, wlanPW)
        for i in range(10):
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            print('.')
            time.sleep(1)
    if wlan.isconnected():
        print('WLAN-Verbindung hergestellt')
        netConfig = wlan.ifconfig()
        print('IPv4-Adresse:', netConfig[0])
        print()
        return netConfig[0]
    else:
        print('Keine WLAN-Verbindung')
        print('WLAN-Status:', wlan.status())
        print()
        return ''

# WLAN-Verbindung herstellen
ipv4 = wlanConnect()

# HTTP-Server starten
if ipv4 != '':
    print('Server starten')
    addr = socket.getaddrinfo(ipv4, 80)[0][-1]
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(addr)
    server.listen(1)
    print('Server hört auf', addr)
    print()
    print('Beenden mit STRG + C')
    print()

# Auf eingehende Verbindungen hören
while True:
    try:
        conn, addr = server.accept()
        print('HTTP-Request von Client', addr)
        request = conn.recv(1024)
        #print('Request:', request)
        request = str(request)
        request = request.split()
        print('URL:', request[1])
        # URL auswerten
        if request[1] == '/light/on':
            print('LED einschalten')
            led.value(1)
        elif request[1] == '/light/off':
            print('LED ausschalten')
            led.value(0)
        elif request[1] == '/light/toggle':
            print('LED umschalten')
            led.toggle()
        elif request[1] == '/servo/toggle':
            print('Servo umschalten')
            if servo_angle == 0:
                set_servo_angle(90)
                print('Servo auf 90°')
            else:
                set_servo_angle(0)
                print('Servo auf 0°')
        elif request[1].startswith('/servo/angle='):
            angle_str = request[1].split('=')[1]
            try:
                angle = int(angle_str)
                if 0 <= angle <= 180:
                    set_servo_angle(angle)
                    print('Servo auf ' + str(angle) + '°')
            except:
                pass
        # LED-Status auswerten
        #print('LED-Status:', led.value())
        state_is = ''
        if led.value() == 1:
            state_is += '<p align="center"><b>LED ist AN</b> <a href="/light/off"><button>AUS</button></a></p>'
        if led.value() == 0:
            state_is += '<p align="center"><b>LED ist AUS</b> <a href="/light/on"><button>AN</button></a></p>'
        # Servo-Status anzeigen
        state_is += '<p align="center"><b>Servo Position: <span id="angle">' + str(servo_angle) + '</span>°</b></p>'
        state_is += '<p align="center"><input type="range" min="0" max="180" value="' + str(servo_angle) + '" onchange="fetch(\'/servo/angle=\' + this.value); document.getElementById(\'angle\').innerText = this.value;"></p>'
        # HTTP-Response erzeugen und senden
        response = html.replace('TEXT', state_is)
        conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        conn.send(response)
        conn.close()
        print('HTTP-Response gesendet')
        
        # LCD aktualisieren
        if lcd:
            try:
                lcd.clear()
                lcd.set_cursor(0, 0)
                lcd.write('Servo: ' + str(servo_angle) + 'gr')
                lcd.set_cursor(0, 1)
                lcd.write('LED: ' + ('AN' if led.value() == 1 else 'AUS'))
            except Exception as e:
                print('LCD Update Fehler:', e)
        print()
    except OSError as e:
        break
    except (KeyboardInterrupt):
        break

try: conn.close()
except NameError: pass
try: server.close()
except NameError: pass
print('Server beendet')
