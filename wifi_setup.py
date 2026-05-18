# file: wifi_setup.py

import network
import time

from config import SSID_AP, PASSWORD_AP


def start_access_point(status_callback=None):
    ap = network.WLAN(network.AP_IF)

    ap.active(True)

    ap.config(
        essid=SSID_AP,
        password=PASSWORD_AP
    )

    while not ap.active():
        if status_callback:
            status_callback()
        time.sleep(0.05)

    ip = ap.ifconfig()[0]

    print("Access Point gestartet")
    print("IP:", ip)

    return ap