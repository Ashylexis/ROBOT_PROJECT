import time
from machine import Pin
from config import PROGRAM_SWITCH_PINS, START_SWITCH_PIN, RESET_SWITCH_PIN

PROGRAM_MAP = {
    0: None,
    1: 'p1',
    2: 'p2',
    3: 'p3',
}


def read_switch(pin):
    return pin.value() == 0


class SwitchPanel:
    def __init__(self):
        self.program_pins = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in PROGRAM_SWITCH_PINS]
        self.start_pin = Pin(START_SWITCH_PIN, Pin.IN, Pin.PULL_UP)
        self.reset_pin = Pin(RESET_SWITCH_PIN, Pin.IN, Pin.PULL_UP) if RESET_SWITCH_PIN is not None else None
        self.last_program_code = self._read_program_code()
        self.last_start = self._read_start()
        self.last_reset = self._read_reset()
        self.debounce_ms = 50
        self.last_change = time.ticks_ms()

    def _read_program_code(self):
        code = 0
        for idx, pin in enumerate(self.program_pins):
            if read_switch(pin):
                code |= 1 << idx
        return code

    def _read_start(self):
        return read_switch(self.start_pin)

    def _read_reset(self):
        return read_switch(self.reset_pin) if self.reset_pin else False

    def selected_program(self):
        return PROGRAM_MAP.get(self._read_program_code())

    def poll(self):
        now = time.ticks_ms()
        program_code = self._read_program_code()
        start_pressed = self._read_start()
        reset_pressed = self._read_reset()

        if program_code != self.last_program_code or start_pressed != self.last_start or reset_pressed != self.last_reset:
            self.last_change = now

        if time.ticks_diff(now, self.last_change) < self.debounce_ms:
            return None

        event = {
            'selection': PROGRAM_MAP.get(program_code),
            'start': start_pressed and not self.last_start,
            'reset': reset_pressed and not self.last_reset,
            'program_code': program_code,
        }

        self.last_program_code = program_code
        self.last_start = start_pressed
        self.last_reset = reset_pressed
        return event
