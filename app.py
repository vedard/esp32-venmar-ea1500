import http
import asyncio
import json

from lib.microdot import Microdot
from machine import Pin, SPI
from MCP41X1 import MCP41X1
from EA1500 import EA1500
from storage import Storage
from wifi import WiFi
from display import Display
from button import Button
from mqtt import MQTT


class App:
    def __init__(self):
        self.storage = Storage(
            {
                "current_preset": "Off",
            }
        )

        self.wifi = WiFi(
            self.storage.get_secret("wifi.ssid"),
            self.storage.get_secret("wifi.password"),
        )

        self.mqtt = MQTT(
            self.storage.get_secret("mqtt.host"),
            self.storage.get_secret("mqtt.username"),
            self.storage.get_secret("mqtt.password"),
            self.__on_mqtt_message
        )

        self.spi = SPI(
            1,
            baudrate=self.storage.get_option("spi.baudrate"),
            sck=Pin(self.storage.get_option("spi.sck")),
            miso=Pin(self.storage.get_option("spi.miso")),
            mosi=Pin(self.storage.get_option("spi.mosi")),
        )

        self.ea1500 = EA1500(
            MCP41X1(
                self.spi, Pin(self.storage.get_option("mcp41x1.cs"), Pin.OUT, value=1)
            )
        )

        self.button = Button(Pin(self.storage.get_option("button.gpio")), self.__on_button_click)

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
    
    async def run(self):
        self.ea1500.apply_preset(self.storage.get_persistent_value("current_preset"))
        self.display.draw()
        self.display.wake()

        self.wifi.connect()
        self.display.draw()
        self.display.wake()
        
        self.mqtt.connect()
        self.mqtt.subscribe(f"homeassistant/device/{self.mqtt.client_id}/command/+")
        self.mqtt.publish(f'homeassistant/device/{self.mqtt.client_id}/config', json.dumps({
            "device": {
                "identifiers": [self.mqtt.client_id],
                "name": "Air Exchanger",
                "model": "EA1500",
                "manufacturer": "Venmar"
            },
            "origin": {
                "name": "vedard/esp32-venmar-ea1500"
            },
            "components":{
                 "mode": {
                    "p": "select",
                    "options": ["Off", "Normal", "Boost", "Recirculation"],
                    "command_topic": f"homeassistant/device/{self.mqtt.client_id}/command/mode",
                    "state_topic": f"homeassistant/device/{self.mqtt.client_id}/state",
                    "value_template": "{{value_json.mode}}",
                    "unique_id": "mode",
                    "icon": "mdi:fan",
                    "name": "mode"
                }
            }
        }))

        await asyncio.gather(
            self.mqtt.listen_loop(),
            self.mqtt.reconnect_loop(),
            self._publish_state_loop(),
            self.webserver.start_server(
                host=self.storage.get_option("http.server.host"),
                port=self.storage.get_option("http.server.port"),
            ),
        )

    async def _publish_state_loop(self):
        while True:
            self._publish_state()
            await asyncio.sleep(120)

    def _publish_state(self):
        self.mqtt.publish(f'homeassistant/device/{self.mqtt.client_id}/state', json.dumps({
            "mode": self.storage.get_persistent_value("current_preset")
        }))
        
    def __on_button_click(self, _):
        if self.display.is_awake():
            preset = self.ea1500.cycle_preset()
            self.storage.save_persistent_value("current_preset", preset["name"])
            self._publish_state()
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

    def __on_mqtt_message(self, topic, msg):
        if topic == f'homeassistant/device/{self.mqtt.client_id}/command/mode':
            self.ea1500.apply_preset(msg)
            self.storage.save_persistent_value("current_preset", msg)
            self.display.draw()
            self._publish_state()
