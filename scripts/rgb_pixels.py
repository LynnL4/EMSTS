
import time
import signal
import threading
from pixel_ring import apa102
from gpiozero import LED
try:
    import queue as Queue
except ImportError:
    import Queue as Queue


class RGBLedPattern(object):
    def __init__(self, show=None, number=12):
        self.pixels_number = number
        self.pixels = [0] * 4 * number

        if not show or not callable(show):
            def dummy(data):
                pass
            show = dummy

        self.show = show
        self.stop = False

        self.COLOR_R = [0, 24,  0,  0] * self.pixels_number
        self.COLOR_G = [0,  0, 24,  0] * self.pixels_number
        self.COLOR_B = [0,  0,  0, 24] * self.pixels_number

    def wakeup(self, direction=0):
        pass

    def listen(self):
        pass

    def think(self):
        counter = 0
        while not self.stop:
            if counter == 0:  self.show(self.COLOR_R)
            if counter == 10: self.show(self.COLOR_G)
            if counter == 20: self.show(self.COLOR_B)
            time.sleep(0.1)
            counter = counter + 1
            if counter >= 30: counter = 0

    def speak(self):
        pass

    def off(self):
        self.show([0] * 4 * 12)

class Pixels:
    PIXELS_N = 12

    def __init__(self, pattern=RGBLedPattern):
        self.pattern = pattern(show=self.show)

        self.dev = apa102.APA102(num_led=self.PIXELS_N)
        
        self.power = LED(5)
        self.power.on()

        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

        self.last_direction = None

    def wakeup(self, direction=0):
        self.last_direction = direction
        def f():
            self.pattern.wakeup(direction)

        self.put(f)

    def listen(self):
        if self.last_direction:
            def f():
                self.pattern.wakeup(self.last_direction)
            self.put(f)
        else:
            self.put(self.pattern.listen)

    def think(self):
        self.put(self.pattern.think)

    def speak(self):
        self.put(self.pattern.speak)

    def off(self):
        self.put(self.pattern.off)

    def put(self, func):
        self.pattern.stop = True
        self.queue.put(func)

    def _run(self):
        while True:
            func = self.queue.get()
            self.pattern.stop = False
            func()

    def show(self, data):
        for i in range(self.PIXELS_N):
            self.dev.set_pixel(i, int(data[4*i + 1]), int(data[4*i + 2]), int(data[4*i + 3]))

        self.dev.show()


pixels = Pixels()
led_en = 0


def sigusr1_handler(signum, frame):
    global led_en
    led_en = 1

def sigusr2_handler(signum, frame):
    global led_en
    pixels.off()
    led_en = 0


if __name__ == '__main__':
    signal.signal(signal.SIGUSR1, sigusr1_handler)
    signal.signal(signal.SIGUSR2, sigusr2_handler)

    fo = open("handler-installed", "w")
    print("start __main__", file=fo)
    fo.close()

    while True:
        time.sleep(0.1)
        if not led_en: continue

        try:
            pixels.think()
            time.sleep(3)
        except KeyboardInterrupt:
            break


    pixels.off()
    time.sleep(1)

