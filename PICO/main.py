import time
from machine import Pin

# ===== 起動待ち（REPL・シリアル安定化）=====
time.sleep(2)
print("PICO BOOTED")

# ===== オンボードLED =====
led = Pin("LED", Pin.OUT)

# ===== メインループ =====
while True:
    led.toggle()          # LED点滅
    print("tick")         # ログ出力
    time.sleep(1.0)       # 1秒周期
