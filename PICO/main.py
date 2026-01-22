import time
import sys
import select
from machine import Pin

# ===== 起動待ち（REPL・シリアル安定化）=====
time.sleep(2)
boot_time = time.time()
print("PICO BOOTED")

# ===== オンボードLED =====
try:
    led = Pin("LED", Pin.OUT)
except Exception:
    led = Pin(25, Pin.OUT)

# ===== 状態 =====
enabled = True          # True: 点滅する / False: 常に消灯
led_state = 0
last_toggle_ms = time.ticks_ms()
period_ms = 1000        # 1秒周期

def set_enabled(v: bool):
    global enabled, led_state
    enabled = v
    if not enabled:
        led_state = 0
        led.value(0)

print("READY  (commands: EN 1 | EN 0 | TOGGLE)")

while True:
    # ---- PCからの入力を非ブロッキングで読む ----
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
    except Exception as e:
        # selectが環境によって例外出すことがあるので落とさない
        pass

    # ---- 点滅ロジック（ループは常に回す）----
    now = time.ticks_ms()
    if enabled and time.ticks_diff(now, last_toggle_ms) >= period_ms:
        last_toggle_ms = now
        led_state ^= 1
        led.value(led_state)

        elapsed = time.time() - boot_time
        print("tick", elapsed)

    # 少しだけ寝かせる（CPU占有防止）
    time.sleep(0.01)
