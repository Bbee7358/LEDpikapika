# boot.py  (Picoのルートに置く)
import time
from machine import Pin

# 1) USBが安定する猶予
time.sleep(0.5)

# 2) セーフモード（GP15をGNDで起動）
SAFE = Pin(15, Pin.IN, Pin.PULL_UP)

if not SAFE.value():
    print("SAFE MODE: main.py will NOT start. (GP15=GND)")
    while True:
        time.sleep(1)

# 3) 追加：起動直後2秒だけ“開発ウィンドウ”
#    （この間にVS Codeで接続→アップロードが可能）
print("BOOT: 2s dev window... (press Ctrl+C to stay in REPL)")
t0 = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), t0) < 2000:
    time.sleep(0.05)

# boot.py はここで終わり、次に main.py が実行される
