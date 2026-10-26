# ESP32 MicroPython Hub

A hub for the ESP32 that lets you choose which MicroPython script it runs, using MQTT communication.

## Versions

There are two versions of the main script:

- `main.py`: uses an SSD1306 128x64 screen. You need to install the SSD1306 driver on your ESP32 first.
- `main_no_screen.py`: no screen configuration. You also need to rename it to `main.py` if you want to use this version.

The `example_scripts/` folder has some example scripts, like a lux sensor, a device scanner and a GPIO LOW/HIGH cycle.

> **Note:** the script files must be in the same folder as `main.py`. If you have other files in this folder, you can add them to the `IGNORE_SCRIPTS` list.

## Requirements

First, you need to connect your ESP32 to your Wi-Fi network, replacing the `"SSID"` and `"PASSWORD"` values with your real Wi-Fi credentials.

You will also need an MQTT broker. For example, you can use a cellphone with Termux and Mosquitto, also you can use the same phone to send messages to `esp32/Menu`. The broker's IP address needs to be fixed. If you can't set a fixed IP, you'll have to change the `SERVER` variable in the main file every time the address changes.

## How it works

Once the broker is up, every message sent to the `esp32/Menu` topic is read and interpreted by the ESP32 like this:

1. The message is split into parts by spaces;
2. The first part is the name of the script file (without `.py`);
3. All other parts are arguments, and you decide how they're used inside your script.

Example: `lux arg1 arg2` runs `lux` with `arg1` and `arg2` as arguments.

Logs are sent to `esp32/Logs`, and errors are sent to `esp32/Status`.

Also, two commands are already configured in the main file:

- `reset`: resets your ESP32 using `machine.reset()`.
- `list`: lists the available scripts.

## Creating your own script

After importing everything you need, create a `run` function. This is the function `main.py` will import and call. If `run` contains a loop, it should only keep going while `should_stop()` is `False`:

```python
while not should_stop():
    # your code here
```

This way, when you switch to another script, the old loop is stopped first.