import time
import sys
from machine import Pin
import neopixel

# ==== 入力監視（poll優先）====
try:
    import uselect as select
except ImportError:
    import select

# ===== 設定 =====
PIN0 = 0
NUM0 = 240

PIN1 = 1
NUM1 = 240

TOTAL = NUM0 + NUM1
FRAME_LEN = 3 * TOTAL

DEFAULT_R, DEFAULT_G, DEFAULT_B = 20, 0, 0  # 起動時デフォルト点灯（赤20/255）

# オンボードLED
try:
    onboard = Pin("LED", Pin.OUT)
except Exception:
    onboard = Pin(25, Pin.OUT)

# 救出ピン（PULL_UPで浮きを潰す。LOWでSAFE）
SAFE = Pin(15, Pin.IN, Pin.PULL_UP)

# SAFE = LOW → 救出モード（USB触らず点滅だけ）
if SAFE.value() == 0:
    while True:
        onboard.toggle()
        time.sleep(0.15)

# 通常起動の合図：2回だけ点滅
for _ in range(2):
    onboard.value(1); time.sleep(0.08)
    onboard.value(0); time.sleep(0.08)

# ===== NeoPixel 2系統 =====
np0 = neopixel.NeoPixel(Pin(PIN0, Pin.OUT), NUM0)
np1 = neopixel.NeoPixel(Pin(PIN1, Pin.OUT), NUM1)

def fill_all(r, g, b):
    for i in range(NUM0):
        np0[i] = (r, g, b)
    for i in range(NUM1):
        np1[i] = (r, g, b)
    np0.write()
    np1.write()

def apply_frame(payload: bytes):
    # payload length must be FRAME_LEN = 3*(NUM0+NUM1)
    # payload layout: [GP0 RGB...][GP1 RGB...]
    j = 0

    # GP0
    for i in range(NUM0):
        r = payload[j]; g = payload[j+1]; b = payload[j+2]
        np0[i] = (r, g, b)
        j += 3

    # GP1
    for i in range(NUM1):
        r = payload[j]; g = payload[j+1]; b = payload[j+2]
        np1[i] = (r, g, b)
        j += 3

    np0.write()
    np1.write()

# ---- 起動直後の不安定対策 ----
time.sleep(0.8)
fill_all(0,0,0); time.sleep_ms(30)
fill_all(DEFAULT_R, DEFAULT_G, DEFAULT_B); time.sleep_ms(30)
fill_all(DEFAULT_R, DEFAULT_G, DEFAULT_B); time.sleep_ms(30)

# ===== 受信パーサ（状態機械）=====
# packet: 'N''P' + len(lo,hi) + payload + checksum(xor of payload)
S_WAIT_N  = 0
S_WAIT_P  = 1
S_LEN_0   = 2
S_LEN_1   = 3
S_PAYLOAD = 4
S_CSUM    = 5

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

# pollが使える環境ならpoll優先（sys.stdinをselectするより安定しがち）
use_poll = hasattr(select, "poll")
if use_poll:
    poller = select.poll()
    try:
        poller.register(sys.stdin, select.POLLIN)
    except Exception:
        # 環境によってはbuffer側を登録した方が通ることがある
        poller.register(stdin_buf, select.POLLIN)

while True:
    # ---- 受信（非ブロッキング）----
    try:
        has_data = False

        if use_poll:
            # poll() は [ (obj, event), ... ] が返る
            ev = poller.poll(0)
            has_data = bool(ev)
        else:
            r, _, _ = select.select([sys.stdin], [], [], 0)
            has_data = bool(r)

        if has_data:
            data = stdin_buf.read(64)  # 小さめでOK（途切れても状態機械で復帰）
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
                        if need_len != FRAME_LEN:
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
                        if csum == (xor_sum & 0xFF):
                            apply_frame(payload)
                        reset_parser()

    except Exception:
        # 受信周りが落ちてもLED出力は止めたくないので握り潰す
        pass

    # ---- 生存確認LED ----
    now = time.ticks_ms()
    if time.ticks_diff(now, last_blink) >= blink_period:
        last_blink = now
        onboard_state ^= 1
        onboard.value(onboard_state)

    time.sleep(0.001)
