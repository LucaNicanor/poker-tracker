"""
Waits ONLY for F8 analysis requests (files matching analyze_hand_*.png).
F9 silent records and background auto-records are ignored by this listener,
so the chat is NEVER spammed unless the user explicitly presses F8!
"""

import glob
import os
import sys
import time

WATCH_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "hands", "raw", "clubwpt"
)
os.makedirs(WATCH_DIR, exist_ok=True)


def get_existing():
    return set(glob.glob(os.path.join(WATCH_DIR, "analyze_hand_*.*")))


def main():
    existing = get_existing()
    print(f"Waiting for F8 analysis trigger in {WATCH_DIR}...", flush=True)

    while True:
        time.sleep(0.4)
        current = get_existing()
        new_files = current - existing
        if new_files:
            latest = max(new_files, key=os.path.getmtime)
            print(f"F8_ANALYZE:{latest}", flush=True)
            sys.exit(0)


if __name__ == "__main__":
    main()
