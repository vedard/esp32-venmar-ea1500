import micropython
import http

from lib.microdot import Microdot
from machine import Pin, SoftSPI
from MCP41X1 import MCP41X1
from EA1500 import EA1500
from storage import Storage
from wifi import WiFi
from display import Display


class App:
    def __init__(self):
        self.storage = Storage(
            {
                "current_preset": "Off",
                "ea1500.presets": [
                    {"name": "Off", "value": 128},
                    {"name": "Normal", "value": 64},
                    {"name": "Boost", "value": 32},
                    {"name": "Recirculation", "value": 16},
                ],
            }
        )

        self.wifi = WiFi(
            self.storage.get_secret("wifi.ssid"),
            self.storage.get_secret("wifi.password"),
        )

        self.spi = SoftSPI(
            baudrate=3200000,
            sck=Pin(self.storage.get_option("spi.sck")),
            miso=Pin(self.storage.get_option("spi.miso")),
            mosi=Pin(self.storage.get_option("spi.mosi")),
        )

        self.ea1500 = EA1500(
            MCP41X1(
                self.spi, Pin(self.storage.get_option("mcp41x1.cs"), Pin.OUT, value=1)
            )
        )
        self.ea1500.configure_presets(self.storage.get_persistent_value("ea1500.presets"))

        self.button = Pin(self.storage.get_option("button.gpio"), Pin.IN, Pin.PULL_UP)
        self.button.irq(
            trigger=Pin.IRQ_RISING,
            handler=lambda _: micropython.schedule(self.__on_button_click, None),
        )

        self.display = Display(
            self.spi,
            self.storage.get_option("display.cs"),
            self.storage.get_option("display.dc"),
            self.storage.get_option("display.rst"),
            self.storage.get_option("display.lit"),
        )
        self.display.set_brightness(self.storage.get_option("display.brightness"))
        self.display.set_inactivity_timeout(
            self.storage.get_option("display.inactivity_timeout")
        )
        self.display.set_draw_callback(self.__on_display_draw)

        self.webserver = Microdot()
        http.register_routes(self)

    def run(self):
        self.ea1500.apply_preset(
            self.storage.get_persistent_value("current_preset")
        )
        self.display.draw()
        self.display.wake()

        self.wifi.connect()
        self.display.draw()
        self.display.wake()

        self.webserver.run(
            host=self.storage.get_option("http.server.host"),
            port=self.storage.get_option("http.server.port"),
        )

    def __on_button_click(self, _):
        if self.display.is_awake():
            preset = self.ea1500.cycle_preset()
            self.storage.save_persistent_value("current_preset", preset["name"])
            self.display.draw()
            self.display.wake()
        else:
            self.display.wake()

    def __on_display_draw(self, tft, font):
        tft.fill(tft.BLACK)
        tft.rect((1, 26), (160, 80), tft.PURPLE)
        tft.rect((2, 27), (158, 78), tft.PURPLE)
        tft.text((7, 32), f"{self.ea1500.state["name"]}", tft.WHITE, font, 2, nowrap=False)
        tft.text((7, 50), f"{self.ea1500.state["value"]}", tft.WHITE, font, 1, nowrap=False)
        
        ip = self.wifi.get_ip()
        if ip != "0.0.0.0":
            tft.text((7, 93), f"IP: {ip}", tft.WHITE, font, 1, nowrap=False)
        else:
            tft.text((7, 93), f"connecting...", tft.WHITE, font, 1, nowrap=False)
