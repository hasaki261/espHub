import os
from machine import Pin, SoftI2C
from umqtt.simple import MQTTClient
import network, time, ssd1306, machine
IGNORE_SCRIPTS = ('boot.py', 'boot_console.py', 'main.py')

SERVER = 'SERVER_IP'
MAIN_CLIENT_ID = 'ESP32_Launcher'
LOG_CLIENT_ID = 'ESP32_Logs'
CMD_TOPIC = b'esp32/Menu'
LOGS_TOPIC = b'esp32/Logs'
pending = None

def print_log(msg):
    print(msg)
    return logs_client.publish(LOGS_TOPIC, msg)
def on_msg(topic, msg):
    global pending
    pending = msg.decode().strip()
def should_stop():
    client.check_msg()
    return pending is not None
def to_value(s):
    try:
        return int(s, 0)
    except ValueError:
        return s
def screen_text(text, y=0, length=16):
    for i in range(0, len(text), length):
        screen.text(text[i:i + length], 0, y)
        y += 8

screen_i2c = SoftI2C(scl=Pin(15), sda=Pin(4))
screen = ssd1306.SSD1306_I2C(128, 64, screen_i2c)
screen.fill(0)

pre_connected_anchor = time.ticks_ms()
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("SSID", "PASSWORD")
screen.text("Connecting", 0, 0)
screen.text("SSID", 0, 16)
screen.show()

while not sta_if.isconnected():
    time.sleep(0.1)
logs_client = MQTTClient(LOG_CLIENT_ID, SERVER)
logs_client.connect()
print_log(f"Connected to WIFI in {time.ticks_diff(time.ticks_ms(), pre_connected_anchor)}ms")
screen.fill(0)
screen.text("Waiting command", 0, 24)
screen.show()

client = MQTTClient(MAIN_CLIENT_ID, SERVER)
client.set_callback(on_msg)
client.connect()
client.subscribe(CMD_TOPIC)

while True: 
    if pending:
        cmd, pending = pending, None
        parts = cmd.split()
        current = parts[0]
        args = [to_value(a) for a in parts[1:]]
        if current == "reset":
            machine.reset()
        if current == "list":
            scripts = [f[:-3] for f in os.listdir() if f.endswith('.py') and f not in IGNORE_SCRIPTS]
            print_log("Scripts: " + ", ".join(scripts))
            screen.fill(0)
            screen.text("Scripts: ", 0, 0)
            if len(scripts) > 21:
                scripts = scripts[:21 - 1] + ["..."]
            for i, name in enumerate(scripts[:21]):
                if len(name) > 4:
                    name = name[:3] + "~"
                col = i % 3                   
                row = i // 3
                screen.text(name, 8 + col * 40, 8 + row * 8)
            screen.show()
            continue
        try:
            print_log(f"Running: {current}")
            screen.fill(0)
            screen.text("Running:", 0, 0)
            screen.text(current, 0, 8)
            screen_text(" ".join(str(a) for a in args), 24)
            screen.show()
            time.sleep(1)
            mode = __import__(current)
            mode.run(client, should_stop, *args)
        except Exception as e:
            client.publish(b'esp32/Status', "error: {}".format(e))
            screen.fill(0)
            screen.text("ERROR, Check:", 0, 0)
            screen.text("esp32/Status", 0, 24)
            screen.show()
        finally:
            import sys
            sys.modules.pop(current, None)
    else:
        client.wait_msg()