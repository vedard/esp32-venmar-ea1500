import machine
import asyncio
import logging

from lib.umqtt import MQTTClient, MQTTException


class MQTT:
    DEFAULT_PORT = 1883

    def __init__(self, host, username, password):
        server, port = self._split_server_port(host)

        self.logger = logging.getLogger("MQTT")
        self.connected = False
        self._connect_callbacks = []
        self._message_callbacks = []
        self.client_id = machine.unique_id().hex()
        self.mqtt = MQTTClient(
            self.client_id,
            server,
            port,
            username,
            password,
        )
        self.mqtt.set_callback(self._message_received)

    def connect(self):
        try:
            self.connected = False
            self.logger.info("Connecting")
            self.mqtt.connect()
            self.logger.info("Connected")
            self.connected = True
            for callback in self._connect_callbacks:
                callback()
        except OSError as e:
            self.logger.exception("Connection failed", e)
        except MQTTException as e:
            self.logger.exception("Connection failed", e)
    
    def publish(self, topic, message):
        if not self.connected:
            return

        try:
            self.logger.info(f"Publishing {topic}")
            self.mqtt.publish(topic, message)
        except OSError as e:
            self.logger.exception("Publish failed", e)
            self.connected = False

    def subscribe(self, topic):
        if not self.connected:
            return
        
        try:
            self.logger.info(f"Subscribing {topic}")
            self.mqtt.subscribe(topic)
        except OSError as e:
            self.logger.exception("Subscribe failed", e)
            self.connected = False

    def add_connect_callback(self, callback):
        self._connect_callbacks.append(callback)

    def add_message_callback(self, callback):
        self._message_callbacks.append(callback)

    async def listen_loop(self):
        while True:
            if self.connected:
                try:
                    self.mqtt.check_msg()
                except OSError as e:
                    self.logger.exception("Listen failed", e)
                    self.connected = False
            
            await asyncio.sleep(1)
    
    async def reconnect_loop(self):
        while True:
            if not self.connected:
                self.connect()
            
            await asyncio.sleep(30)


    def _split_server_port(self, host):
        split = host.split(":")
        if len(split) == 2:
            return split[0], int(split[1])
        else:
            return host, 1883
        
    def _message_received(self, topic, msg):
        topic = topic.decode()
        msg = msg.decode()
        self.logger.info(f"Incoming {topic} - {msg}")
        for callback in self._message_callbacks:
            callback(topic, msg)
