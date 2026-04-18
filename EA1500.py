import logging

from MCP41X1 import MCP41X1


class EA1500:
    """
    Venmar EA1500 air exchanger controller using MCP41X1 digital potentiometer
    """

    def __init__(self, mcp41x1):
        self.logger = logging.getLogger("EA1500")
        self.mcp41x1: MCP41X1 = mcp41x1
        self.presets = [
            {"name": "Off", "value": 128},
            {"name": "Normal", "value": 64},
            {"name": "Boost", "value": 32},
            {"name": "Recirculation", "value": 16},
        ]
        self.state = self.presets[0]

    def apply_preset(self, name):
        """
        Apply a preset by writing its value to the digital potentiometer.
        """
        for preset in self.presets:
            if name.lower() == preset["name"].lower():
                self.logger.info(f"Applying preset '{preset['name']}'")
                if self.mcp41x1.wiper_write(preset["value"]):
                    self.state = preset
                    return
        else:
            raise ValueError(f"Could not find preset '{name}'")
        
    def cycle_preset(self):
        """
        Cycle to the next preset in the order: OFF, Normal, Boost, Recirculation
        """
        try:
            next_index = (self.presets.index(self.state) + 1) % len(self.presets)
        except ValueError:
            next_index = 0
        
        self.apply_preset(self.presets[next_index]["name"])
        return self.presets[next_index]
