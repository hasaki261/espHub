import os
from machine import Pin, SoftI2C
from umqtt.simple import MQTTClient
import network, time, machine
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

pre_connected_anchor = time.ticks_ms()
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("SSID", "PASSWORD")

while not sta_if.isconnected():
    time.sleep(0.1)
logs_client = MQTTClient(LOG_CLIENT_ID, SERVER)
logs_client.connect()
print_log(f"Connected to WIFI in {time.ticks_diff(time.ticks_ms(), pre_connected_anchor)}ms")

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
            continue
        try:
            print_log(f"Running: {current}")
            time.sleep(1)
            mode = __import__(current)
            mode.run(client, should_stop, *args)
        except Exception as e:
            client.publish(b'esp32/Status', "error: {}".format(e))
        finally:
            import sys
            sys.modules.pop(current, None)
    else:
        client.wait_msg()