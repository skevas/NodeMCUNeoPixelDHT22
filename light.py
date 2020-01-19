import machine, neopixel
import time
import random
import dht
import socket


def color_picker(color):
    high_light = 200
    low_light = 50
    ultra_low_light = 10

    if color == "R":
        return ((ultra_low_light, 0, 0), (low_light, 0, 0), (high_light, 0, 0))
    elif color == "G":
        return ((0, ultra_low_light, 0), (0, low_light, 0), (0, high_light, 0))
    elif color == "B":
        return ((0, 0, ultra_low_light), (0, 0, low_light), (0, 0, high_light))
    return ((0, ultra_low_light), (0, low_light, 0), (0, high_light, 0))


def random_color():
    color = random.getrandbits(2) % 3
    if color == 0:
        return "G"
    elif color == 1:
        return "R"
    elif color == 2:
        return "B"


def erase_all(leds, np):
    for led in range(0, leds):
        np[led] = (0, 0, 0)


# ## DHT22
#
# Show the temperature and humidity on the LED strip


def sensor(leds, np):
    while True:
        try:
            d = dht.DHT22(machine.Pin(5))

            d.measure()
            temperature = d.temperature()
            humidity = d.humidity()
        except Exception as e:
            print("Error {}".format(e))
            temperature = 50
            humidity = 100
        finally:
            print("{} {}".format(temperature, humidity))

        max_temp = 30
        max_humidity = 100

        temp_leds = int((temperature * leds) / max_temp)
        humidity_leds = int((humidity * leds) / max_humidity)

        for led in range(0, leds):
            np[led] = (0, 0, 0)

        for led in range(0, temp_leds + 1):
            np[led] = (100, 0, 0)
        np.write()
        time.sleep_ms(2000)

        for led in range(0, leds):
            np[led] = (0, 0, 0)

        for led in range(0, humidity_leds + 1):
            np[led] = (0, 0, 100)
        np.write()
        time.sleep_ms(2000)


# ## K.I.T.T. Style Forward and Backward


def kitt(leds, np):
    kitt_led = [(180, 0, 0), (140, 0, 0), (100, 0, 0), (60, 0, 0), (20, 0, 0)]

    erase_all(leds, np)

    while True:
        for led in range(0, leds + len(kitt_led)):
            _kitt(leds, led, kitt_led, np)
            time.sleep_ms(500)
        for led in reversed(range(0, leds + len(kitt_led))):
            _kitt(leds, led, kitt_led, np)
            time.sleep_ms(500)


def _kitt(leds, led, kitt, np):
    kitt_leds = min(len(kitt), led)

    for i in range(0, kitt_leds):
        if 0 < led - i < leds:
            np[led - i] = kitt[i]

    np.write()

    for i in range(0, kitt_leds):
        if 0 < led - i < leds:
            np[led - i] = (0, 0, 0)


# ## Counts binary on the LED strip


def binary_light(leds, np):

    for i in range(0, 2 ** (leds - 1)):
        _binary_light(leds, np, i)
        time.sleep_ms(100)


def _binary_light(leds, np, value):
    very_low_light, low_light, high_light = color_picker(random_color())

    erase_all(leds, np)
    binary_representation = [x for x in "{0:b}".format(value)]
    binary_representation.reverse()
    for led, value in enumerate(binary_representation):
        if value == "1":
            np[led] = high_light

    np.write()


# ## Increase


def glow(leds, np):
    erase_all(leds, np)
    for red in range(0, 255):
        for green in range(0, 255):
            for blue in range(0, 255):
                led = (red + green + blue) % leds
                np[led] = (red, green, blue)
                np.write()
                time.sleep_ms(10)


# ## Receive something via TCP
#
# Connect with telnet to the NodeMCU (check port in the code) and write integers to the console. The LED strip will
# show them as binary encoded light


def simple_tcp(leds, np):
    addr = socket.getaddrinfo("0.0.0.0", 1023)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Listening on {}".format(addr))

    while True:
        cl, addr = s.accept()
        print("Client connected")
        cl_file = cl.makefile("rwb", 0)
        while True:
            line = cl_file.readline()
            if not line or line == b"\r\n":
                break
            line = line.decode("utf-8").rstrip()
            try:
                if line == "glow":
                    fn = glow
                elif line == "binary":
                    fn = binary_light
                elif line == "kitt":
                    fn = kitt
                elif line == "sensor":
                    fn = sensor
                else:
                    print("Unknown")
                    continue
                break
            except:
                pass
        cl.close()
        print("Disconnected")
        fn(leds, np)


def light(leds):
    np = neopixel.NeoPixel(machine.Pin(4), leds)
    for i in range(0, leds):
        np[i] = (0, 10, 0)
        np.write()

    print("Starting")
    simple_tcp(leds, np)


light(60)
