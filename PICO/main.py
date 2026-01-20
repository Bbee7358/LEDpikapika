import machine
import neopixel
import sys

PIN_A = machine.Pin(2)
PIN_B = machine.Pin(3)

NUM = 240

np_a = neopixel.NeoPixel(PIN_A, NUM)
np_b = neopixel.NeoPixel(PIN_B, NUM)

BUF_LEN = 480 * 3

while True:
    data = sys.stdin.buffer.read(BUF_LEN)
    if not data or len(data) < BUF_LEN:
        continue

    for i in range(NUM):
        np_a[i] = (data[i*3], data[i*3+1], data[i*3+2])

    base = NUM * 3
    for i in range(NUM):
        np_b[i] = (
            data[base + i*3],
            data[base + i*3+1],
            data[base + i*3+2]
        )

    np_a.write()
    np_b.write()
