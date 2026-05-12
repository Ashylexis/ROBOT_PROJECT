# file: wifi_setup.py

import network
import time

from config import SSID_AP, PASSWORD_AP


def start_access_point():
    ap = network.WLAN(network.AP_IF)

    ap.active(True)

    ap.config(
        essid=SSID_AP,
        password=PASSWORD_AP
    )

    while not ap.active():
        time.sleep(0.1)

    ip = ap.ifconfig()[0]

    print("Access Point gestartet")
    print("IP:", ip)

    return ap