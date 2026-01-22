import time
import sys
import select
from machine import Pin
import neopixel

# ===== 設定 =====
NP_PIN = 0
NUM_LEDS = 240            # ← 1基板のLED数に合わせて変更
DEFAULT_R, DEFAULT_G, DEFAULT_B = 20, 0, 0  # 起動時のデフォルト（赤20/255）

try:
    onboard = Pin("LED", Pin.OUT)
except Exception:
    onboard = Pin(25, Pin.OUT)

#救出モード用ピン
SAFE = Pin(15, Pin.IN)  # 外付けプルアップ想定（LOWで救出）

# SAFE = LOW → 救出モード
if SAFE.value() == 0:
    # 高速点滅で「SAFE中」を示す（USBは一切触らない）
    while True:
        onboard.toggle()
        time.sleep(0.15)

# 通常起動の合図：2回だけ点滅
for _ in range(2):
    onboard.value(1); time.sleep(0.08)
    onboard.value(0); time.sleep(0.08)

# ===== NeoPixel =====
np = neopixel.NeoPixel(Pin(NP_PIN, Pin.OUT), NUM_LEDS)

def apply_payload(payload: bytes):
    # payload length must be 3*NUM_LEDS
    # (r,g,b) per led
    j = 0
    for i in range(NUM_LEDS):
        r = payload[j]; g = payload[j+1]; b = payload[j+2]
        np[i] = (r, g, b)
        j += 3
    np.write()

def fill(r, g, b):
    for i in range(NUM_LEDS):
        np[i] = (r, g, b)
    np.write()

# 起動時デフォルト点灯
fill(DEFAULT_R, DEFAULT_G, DEFAULT_B)

# ===== 受信パーサ（状態機械）=====
# packet: 'N''P' + len(lo,hi) + payload + checksum(xor of payload)
S_WAIT_N = 0
S_WAIT_P = 1
S_LEN_0  = 2
S_LEN_1  = 3
S_PAYLOAD = 4
S_CSUM   = 5

state = S_WAIT_N
need_len = 0
payload = bytearray()
xor_sum = 0

def reset_parser():
    global state, need_len, payload, xor_sum
    state = S_WAIT_N
    need_len = 0
    payload = bytearray()
    xor_sum = 0

reset_parser()

# 生存確認点滅
last_blink = time.ticks_ms()
blink_period = 700
onboard_state = 0

stdin_buf = getattr(sys.stdin, "buffer", sys.stdin)

while True:
    # ---- 受信（非ブロッキング）----
    try:
        r, _, _ = select.select([sys.stdin], [], [], 0)
        if r:
            # まとめて読む（環境差があるので少しずつでもOK）
            data = stdin_buf.read(64)
            if data:
                for b in data:
                    if state == S_WAIT_N:
                        if b == ord('N'):
                            state = S_WAIT_P
                    elif state == S_WAIT_P:
                        if b == ord('P'):
                            state = S_LEN_0
                        else:
                            state = S_WAIT_N
                    elif state == S_LEN_0:
                        need_len = b
                        state = S_LEN_1
                    elif state == S_LEN_1:
                        need_len |= (b << 8)
                        # 想定外の長さは捨てる（同期ズレ対策）
                        if need_len <= 0 or need_len > (3 * NUM_LEDS):
                            reset_parser()
                        else:
                            payload = bytearray()
                            xor_sum = 0
                            state = S_PAYLOAD
                    elif state == S_PAYLOAD:
                        payload.append(b)
                        xor_sum ^= b
                        if len(payload) >= need_len:
                            state = S_CSUM
                    elif state == S_CSUM:
                        csum = b
                        if csum == (xor_sum & 0xFF) and need_len == (3 * NUM_LEDS):
                            apply_payload(payload)
                            # print("ACK FRAME")  # ログ欲しければON
                        # 失敗しても次へ同期を取り直す
                        reset_parser()
    except:
        pass

    # ---- 生存確認LED ----
    now = time.ticks_ms()
    if time.ticks_diff(now, last_blink) >= blink_period:
        last_blink = now
        onboard_state ^= 1
        onboard.value(onboard_state)

    time.sleep(0.001)
