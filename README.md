# ESP32 Venmar EA1500

## Description

A MicroPython controller that emulates the Venmar C34 remote control to manage and automate a Venmar EA1500 air exchanger via MQTT or HTTP.

## Hardware

- [ESP32C3 - XIAO](https://www.digikey.ca/en/products/detail/seeed-technology-co-ltd/113991054/16652880)
- [0.96" TFT RGB Graphic Display – Adafruit](https://www.digikey.ca/en/products/detail/adafruit-industries-llc/3533/7386265)
- [Digital Potentiometer 50k - MCP4141-503E/P](https://www.digikey.ca/en/products/detail/microchip-technology/MCP4141-503E-P/1874267)

## How It Works

The EA1500 air exchanger supports four operating presets: Off, Normal, Boost, and Recirculation.

On the original C34 remote, there is a switch that mechanically changes which resistor is connected between the black and green wires. To reproduce this behavior, a digital potentiometer can be used to replicate the same resistances expected by the air exchanger.

| Preset        | Resistance |
| ------------- | ---------- |
| Off           | ~42kΩ      |
| Normal        | ~21kΩ      |
| Boost         | ~12kΩ      |
| Recirculation | ~7kΩ       |

The remote control also uses a red and a yellow wire, but the unit works perfectly without connecting these two other wires.

## Home Assistant

The goal of the project is to be able to remotely control and automate the air exchanger via Home Assistant.

For example, it is useful to ventilate with the Normal or Boost preset (e.g., while cooking), but during winter this brings in cold air and in summer hot, humid air. With Home Assistant, you can monitor outdoor conditions and automatically switch the air exchanger back to Recirculation.

Communication is handled through the Home Assistant [MQTT integration](https://www.home-assistant.io/integrations/mqtt/). The ESP32 publishes discovery data to `homeassistant/device/[DEVICE_ID]/config`, publishes state to `homeassistant/device/[DEVICE_ID]/state`, and listens for commands on `homeassistant/device/[DEVICE_ID]/command/+`.
