import time
from machine import Pin

time.sleep(2)
boot_time = time.time()
print("PICO BOOTED")

led = Pin("LED", Pin.OUT)

while True:
    led.toggle()

    elapsed = int(time.time() - boot_time)
    print(f"tick : {elapsed} sec")

    time.sleep(1.0)
