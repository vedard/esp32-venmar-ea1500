import json


class HomeAssistant:
    def __init__(self, mqtt, name, model, manufacturer, origin, components):
        self.mqtt = mqtt
        self.topic_prefix = f"homeassistant/device/{mqtt.client_id}/"
        self.components = components
        self._config = {
            "device": {
                "identifiers": [mqtt.client_id],
                "name": name,
                "model": model,
                "manufacturer": manufacturer,
            },
            "origin": {
                "name": origin,
            },
            "components": {x.component_id: x.config(self) for x in self.components},
        }

        self.mqtt.add_connect_callback(self._on_mqtt_connect)
        self.mqtt.add_message_callback(self._message_received)


    def publish_state(self, state):
        self.mqtt.publish(self.topic_prefix + "state", json.dumps(state))

    def _on_mqtt_connect(self):
        self.mqtt.subscribe(self.topic_prefix + "command/+")
        self.mqtt.publish(self.topic_prefix + "config", json.dumps(self._config))

    def _message_received(self, topic, message):
        for component in self.components:
            if component.handle_message(self, topic, message):
                return

class Component:
    platform = None

    def __init__(self, name, icon):
        self.name = name
        self.component_id = name.lower().replace(" ", "")
        self.icon = icon

    def config(self, homeassistant):
        return {
            "platform": self.platform,
            "unique_id": f"{homeassistant.mqtt.client_id}_{self.component_id}",
            "name": self.name,
            "state_topic": homeassistant.topic_prefix + "state",
            "value_template": "{{value_json." + self.component_id + "}}",
            "icon": self.icon
        }

    def handle_message(self, homeassistant, topic, message):
        return False


class Select(Component):
    platform = "select"

    def __init__(
        self,
        name,
        icon,
        options,
        on_command,
    ):
        super().__init__(name, icon)
        self.options = options
        self.on_command = on_command

    def config(self, homeassistant):
        config = super().config(homeassistant)
        config["options"] = self.options
        config["command_topic"] = homeassistant.topic_prefix + f"command/{self.component_id}"
        return config

    def handle_message(self, homeassistant, topic, message):
        if topic != homeassistant.topic_prefix + f"command/{self.component_id}":
            return False

        if message not in self.options:
            print(f"Home Assistant ignored invalid {self.component_id}: {message}")
            return True

        self.on_command(message)
        return True
