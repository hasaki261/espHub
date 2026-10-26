from machine import Pin, SoftI2C
import ssd1306

def run(client, should_stop, scl=23, sda=22, *_):
    screen_i2c = SoftI2C(scl=Pin(15), sda=Pin(4))
    screen = ssd1306.SSD1306_I2C(128, 64, screen_i2c)
    i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda))
    scanneds = i2c.scan()
    found = [hex(a) for a in scanneds]
    msg = "Scanned: " + (", ".join(found) if found else "nothing")
    print(msg)
    client.publish('esp32/Logs', msg)
    screen.fill(0)
    screen.text("Scanned: ", 0, 0)
    if not found:
        screen.text("[Nothing]", 0, 16)
    else:
        for i in range(0, len(found), 3):
            screen.text(" ".join(found[i:i + 3]), 0, 16 + (i // 3) * 8)
    screen.show()
