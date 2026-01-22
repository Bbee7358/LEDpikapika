# from machine import Pin
# import time
# import sys

# # LED
# try:
#     led = Pin("LED", Pin.OUT)
# except Exception:
#     led = Pin(25, Pin.OUT)

# # --- USB安定待ち ---
# # WebSerialは open 後しばらく stdout が死んでることがある
# time.sleep(1.5)

# # ダミー出力（捨てられてOK）
# for _ in range(3):
#     try:
#         sys.stdout.write("")
#         sys.stdout.flush()
#     except:
#         pass
#     time.sleep(0.2)

# print("READY")   # ← ここで初めて出す

# while True:
#     try:
#         line = sys.stdin.readline()
#     except Exception:
#         continue

#     if not line:
#         time.sleep(0.01)
#         continue

#     sys.stdout.write("ECHO:" + line)
#     sys.stdout.flush()

#     cmd = line.strip().upper()
#     # if cmd == "TOGGLE":
#         led.value(0 if led.value() else 1)
#         print("OK TOGGLE")
#     elif cmd == "ON":
#         led.value(1)
#         print("OK ON")
#     elif cmd == "OFF":
#         led.value(0)
#         print("OK OFF")






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
