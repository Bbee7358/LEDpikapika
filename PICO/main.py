import time
import sys
import select
from machine import Pin
import neopixel

# ===== 起動待ち（REPL・シリアル安定化）=====
time.sleep(2)
print("PICO BOOTED")

# ===== オンボードLED（生存確認用）=====
try:
    onboard = Pin("LED", Pin.OUT)
except Exception:
    onboard = Pin(25, Pin.OUT)

# ===== NeoPixel設定（GP0）=====
NP_PIN = 0
NUM_LEDS = 240        # ← 1基板のLED数に合わせて変更
R_ON = 20             # 20/255
G_ON = 0
B_ON = 0

np = neopixel.NeoPixel(Pin(NP_PIN, Pin.OUT), NUM_LEDS)

# ===== 状態 =====
enabled = True  # デフォルトON

def fill_color(r, g, b):
    for i in range(NUM_LEDS):
        np[i] = (r, g, b)
    np.write()

def set_enabled(v: bool):
    global enabled
    enabled = v
    if enabled:
        fill_color(R_ON, G_ON, B_ON)
    else:
        fill_color(0, 0, 0)

# 初期状態反映（デフォルト点灯）
set_enabled(True)

print("READY (commands: EN 1 | EN 0 | TOGGLE)")

# オンボードLEDは「生存確認」でゆっくり点滅
last_blink = time.ticks_ms()
blink_period = 1000
onboard_state = 0

while True:
    # ---- PCからの入力（非ブロッキング）----
    try:
        r, _, _ = select.select([sys.stdin], [], [], 0)
        if r:
            line = sys.stdin.readline()
            if line:
                line = line.strip()
                if line == "EN 1":
                    set_enabled(True)
                    print("ACK EN 1")
                elif line == "EN 0":
                    set_enabled(False)
                    print("ACK EN 0")
                elif line == "TOGGLE":
                    set_enabled(not enabled)
                    print("ACK TOGGLE ->", 1 if enabled else 0)
                else:
                    print("ERR unknown:", line)
    except:
        pass

    # ---- 生存確認点滅（オンボード）----
    now = time.ticks_ms()
    if time.ticks_diff(now, last_blink) >= blink_period:
        last_blink = now
        onboard_state ^= 1
        onboard.value(onboard_state)

    time.sleep(0.01)
