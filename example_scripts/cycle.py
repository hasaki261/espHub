from machine import Pin, SoftI2C
import ssd1306
import time

def run(client, should_stop, gpio=5, drive=0, *_):
    screen_i2c = SoftI2C(scl=Pin(15), sda=Pin(4))
    screen = ssd1306.SSD1306_I2C(128, 64, screen_i2c)
    screen.fill(0)
    led = Pin(gpio, Pin.OUT, drive=drive)
    while not should_stop():
        screen.fill(0)
        led.on()
        screen.text('Led: ON', 0, 0)
        screen.show()
        time.sleep(5)
        screen.fill(0)
        led.off()
        screen.text('Led: OFF', 0, 0)
        screen.show()
        time.sleep(5)
    led.off()
