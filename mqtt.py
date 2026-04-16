import machine
import asyncio

from lib.umqtt import MQTTClient, MQTTException

class MQTT:
    DEFAULT_PORT = 1883

    def __init__(self, host, username, password, callback):
        server, port = self._split_server_port(host)

        self.connected = False
        self.subscriptions = set()
        self.client_id = machine.unique_id().hex()
        self.mqtt = MQTTClient(
            self.client_id,
            server,
            port,
            username,
            password,
        )
        self._callback = callback
        self.mqtt.set_callback(self._message_received)

    def connect(self):
        try:
            print("MQTT connecting...")
            self.connected = False
            self.mqtt.connect()
            self.connected = True
            for topic in self.subscriptions:
                self.mqtt.subscribe(topic)
            print("MQTT connected")
        except OSError as e:
            print("MQTT error:", e)
        except MQTTException as e:
            print("MQTT error:", e)
    
    def publish(self, topic, message):
        if not self.connected:
            return

        try:
            print(f"MQTT publish {topic}")
            self.mqtt.publish(topic, message)
        except OSError as e:        
            print("MQTT error:", e)
            self.connected = False

    def subscribe(self, topic):
        self.subscriptions.add(topic)

        if not self.connected:
            return
        
        try:
            self.mqtt.subscribe(topic)
        except OSError as e:        
            print("MQTT error:", e)
            self.connected = False

    async def listen_loop(self):
        while True:
            if self.connected:
                try:
                    self.mqtt.check_msg()
                except OSError as e:
                    print("MQTT error:", e)
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
        print(f"MQTT incoming {topic} - {msg}")
        self._callback(topic, msg)