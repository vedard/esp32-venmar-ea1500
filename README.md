# ESP32 Venmar EA1500

## Description

A MicroPython controller that emulates the Venmar C34 remote control to manage and automate a Venmar EA1500 air exchanger via an HTTP API.

## Hardware

- [ESP32C3 - XIAO](https://www.digikey.ca/en/products/detail/seeed-technology-co-ltd/113991054/16652880)
- [0.96" TFT RGB Graphic Display – Adafruit](https://www.digikey.ca/en/products/detail/adafruit-industries-llc/3533/7386265)
- [Digital Potentiometer 50k - MCP4141-503E/P](https://www.digikey.ca/en/products/detail/microchip-technology/MCP4141-503E-P/1874267)

## How It Works

The EA1500 air exchanger supports four operating modes: Off, Normal, Boost, Recirculation

On the original C34 remote, there is a switch that mechanically changes which resistor is connected between the black and green wires. To reproduce this behavior, a digital potentiometer can be used to replicate the same resistances expected by the air exchanger.

| Mode          | Resistance |
| ------------- | ---------- |
| Off           | ~42kΩ      |
| Normal        | ~21kΩ      |
| Boost         | ~12kΩ      |
| Recirculation | ~7kΩ       |

The remote control also uses a red and a yellow wire, but the unit works perfectly without connecting these two other wires.

## Home assistant

The goal of the project is to be able to remotely control and automate the air exchanger via Home Assistant.

For example, it is useful to ventilate in Normal or Boost mode (e.g., while cooking), but during winter this brings in cold air and in summer hot, humid air. With Home Assistant, you can monitor outdoor conditions and automatically switch the air exchanger back to Recirculation.

A [REST Sensor](https://www.home-assistant.io/integrations/rest/) can be used to retrieve the operating mode of the air exchanger.

```yml
rest:
  - resource: http://[REPLACE_ESP32_IP]/
    scan_interval: 10
    sensor:
      - name: Air Exchanger State
        value_template: "{{ value_json.state }}"
```

A [REST command](https://www.home-assistant.io/integrations/rest_command/) allows Home Assistant to change the air exchanger mode.

```yml
rest_command:
  set_air_exchanger:
    url: http://[REPLACE_ESP32_IP]/
    method: POST
    headers:
      Content-Type: application/json
      Authorization: "Bearer [REPLACE AUTH TOKEN]"
    payload: '{ "state": "{{ state }}" }'
```

Finally, the [template select entity](https://www.home-assistant.io/integrations/template/#select) provides a control that can be used from a Home Assistant dashboard.

```yml
template:
  - select:
      - name: Air Exchanger
        options: >
          {{ ['Off', 'Normal', 'Boost', 'Recirculation'] }}
        state: "{{ states('sensor.air_exchanger_state') }}"
        select_option:
          - service: rest_command.set_air_exchanger
            data:
              state: "{{ option }}"
        icon: >
          {% if states('sensor.air_exchanger_state') == 'Normal' %}
            mdi:fan
          {% elif states('sensor.air_exchanger_state') == 'Boost' %}
            mdi:fan-plus
          {% elif states('sensor.air_exchanger_state') == 'Recirculation' %}
            mdi:recycle
          {% else %}
            mdi:fan-off
          {% endif %}
```
