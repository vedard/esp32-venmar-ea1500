from lib.ST7735 import TFT
from machine import Pin, PWM, Timer
from font import font


class Display:
    def __init__(self, spi, cs, dc, rst, lit):
        self.tft = TFT(spi, dc, rst, cs)
        self.tft.rotation(1)
        self.tft.initr()
        self.tft.rgb(True)
        self.tft.invertcolor(True)
        self.tft.fill(TFT.BLACK)

        self.brightness_level = 100
        self.brightness_pin = Pin(lit, Pin.OUT, value=1)
        self.brightness_pwm = PWM(self.brightness_pin, freq=5000, duty_u16=65535)

        self.inactivity_timeout = 5

        self.font = font
        self.sleep_timer = Timer(0)

    def __brightness_to_duty(self, value: int) -> int:
        return int(value * 65535 / 100 )

    def set_brightness(self, value):
        if not 1 <= value <= 100:
            raise ValueError("brightness value must be 1-100")

        self.brightness_level = value
        self.brightness_pwm.duty_u16(self.__brightness_to_duty(self.brightness_level))

    def set_inactivity_timeout(self, value):
        self.inactivity_timeout = value

    def sleep(self):
        self.brightness_pwm.duty_u16(0)

    def wake(self):
        self.brightness_pwm.duty_u16(self.__brightness_to_duty(self.brightness_level))
        if self.inactivity_timeout > 0:
            self.sleep_timer.deinit()
            self.sleep_timer.init(
                period=self.inactivity_timeout * 1000,
                mode=Timer.ONE_SHOT,
                callback=lambda _: self.sleep(),
            )
        
    def is_awake(self):
        return self.brightness_pwm.duty_u16() > 0

    def draw(self):
        self.draw_callback(self.tft, self.font)

    def set_draw_callback(self, function):
        self.draw_callback = function
