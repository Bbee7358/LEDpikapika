# main.py
import sys
import time

print("READY")  # Web側がこれを見る

while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline().strip()
        if line == "PING":
            print("PONG")
        else:
            print("UNKNOWN:", line)
    time.sleep(0.01)
