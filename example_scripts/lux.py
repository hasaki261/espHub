from machine import Pin, SoftI2C
from drivers.bh1750 import BH1750
import ssd1306
import time

def run(client, should_stop, scl=23, sda=22, addr = 0x23):
    TOPIC = "esp32/Planthas/lux"
    screen_i2c = SoftI2C(scl=Pin(15), sda=Pin(4))
    screen = ssd1306.SSD1306_I2C(128, 64, screen_i2c)
    sensor_i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda), freq=400000)
    light_sensor = BH1750(bus=sensor_i2c, addr=addr)
    try:
        while not should_stop():
            lux = light_sensor.luminance(BH1750.CONT_HIRES_2)
            msg = "Luz: {:.2f} lux".format(lux)
            screen.fill(0)
            screen.text(f"Luz: {lux:.1f} lux", 0, 24)
            screen.show()
            time.sleep(0.2)
            client.publish(TOPIC, msg)
    except Exception as e:
        print("An error occurred:", e)
        screen.fill(0)
        screen.text("error", 0, 24)
        screen.show()
        raise
    finally:
        screen.fill(0)
        time.sleep(1)
        screen.show()