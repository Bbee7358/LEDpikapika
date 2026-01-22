# # boot.py
# import time
# from machine import Pin

# SAFE = Pin(15, Pin.IN)  # 外付けプルアップ

# # 本体LED
# try:
#     led = Pin("LED", Pin.OUT)
# except:
#     led = Pin(25, Pin.OUT)

# # USBが安定するまで待つ
# time.sleep(0.5)

# # SAFEがLOWなら救出モード（main.pyを起動しない）
# if SAFE.value() == 0:
#     # 速い点滅で「救出中」を示す（printなし）
#     while True:
#         led.toggle()
#         time.sleep(0.1)

# # 通常起動の合図：2回だけ点滅
# for _ in range(2):
#     led.value(1)
#     time.sleep(0.08)
#     led.value(0)
#     time.sleep(0.08)

# # ここで終わる → main.py が起動する

