import micropython
import time
from machine import Pin

class Button:

    DEBOUNCE_MS = 200

    def __init__(self, pin: Pin, on_press=None, on_release=None):
        self.pin = pin
        self.on_press = on_press
        self.on_release = on_release
        self.__last_press = 0
        self.__last_release = 0


        self.pin.init(Pin.IN, Pin.PULL_UP)
        self.pin.irq(
            trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
            handler=lambda p: micropython.schedule(self.__handler, p),
        )
        
    
    def __handler(self, pin):
        now = time.ticks_ms()
        if pin.value() == 0:
            if time.ticks_diff(now, self.__last_press) < self.DEBOUNCE_MS:
                return
            
            self.__last_press = now
            if self.on_press:
                self.on_press(pin)
        else:
            if time.ticks_diff(now, self.__last_release) < self.DEBOUNCE_MS:
                return
            
            self.__last_release = now
            if self.on_release:
                self.on_release(pin)
