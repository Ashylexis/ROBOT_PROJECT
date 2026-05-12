from machine import PWM

class Servo:
    def __init__(self, pin, min_us=1000, max_us=2000, angle=180):
        self.pwm = PWM(pin)
        self.pwm.freq(50)
        self.min_us = min_us
        self.max_us = max_us
        self.angle = angle
        self._angle = -1
        self.write_us(1500)

    def write_us(self, us):
        us = max(self.min_us, min(self.max_us, us))
        duty = int(us * 65536 / 20000)
        self.pwm.duty_u16(duty)

    def write_ms(self, ms):
        self.write_us(int(ms * 1000))

    def set_angle(self, angle=None):
        if angle is None:
            return self._angle
        angle = max(0, min(self.angle, angle))
        self._angle = angle
        us = self.min_us + (self.max_us - self.min_us) * angle / self.angle
        self.write_us(int(us))

    def calibrate(self, pulse_0, pulse_180):
        self.min_us = pulse_0
        self.max_us = pulse_180