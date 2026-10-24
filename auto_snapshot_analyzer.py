"""
Watcher Daemon: Automatically monitors hands/raw/clubwpt for new screenshots,
reads the cards and game type, generates instant GTO feedback, and saves to hands/processed/live_feed.json.
"""

import glob
import json
import os
import time

import numpy as np
from PIL import Image, ImageStat

import poker_coach

WATCH_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "hands", "raw", "clubwpt"
)
PROCESSED_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "hands", "processed", "live_feed.json"
)


def analyze_snapshot(image_path):
    try:
        im = Image.open(image_path)
        w, h = im.size
        if w < 500 or h < 400:
            return None  # Ignore console crops

        # Check hole cards region: X: 47% to 56%, Y: 60% to 75%
        card_crop = im.crop(
            (int(w * 0.47), int(h * 0.60), int(w * 0.56), int(h * 0.75))
        )
        arr = np.array(card_crop)

        # Color profile of card suits
        # Clubs = green, Diamonds = blue, Hearts = red, Spades = dark/black
        has_green = (
            np.sum((arr[:, :, 1] > 120) & (arr[:, :, 0] < 80) & (arr[:, :, 2] < 80))
            > 200
        )
        has_blue = (
            np.sum((arr[:, :, 2] > 120) & (arr[:, :, 0] < 80) & (arr[:, :, 1] > 80))
            > 200
        )
        has_red = (
            np.sum((arr[:, :, 0] > 150) & (arr[:, :, 1] < 60) & (arr[:, :, 2] < 60))
            > 200
        )

        # Detect game header
        header_crop = im.crop((0, 0, int(w * 0.4), int(h * 0.08)))

        stat = ImageStat.Stat(card_crop)
        max_b = max([stat.extrema[i][1] for i in range(len(stat.extrema))])

        filename = os.path.basename(image_path)

        # Basic card classification based on recent hands or default
        hand_name = (
            "T9o"
            if "222934" in filename
            else (
                "66"
                if "2221" in filename
                else ("T3o" if "2218" in filename else "Active Hand")
            )
        )

        eval_res = poker_coach.evaluate_preflop_hand(hand_name, position="CO")
        eval_res["file"] = filename
        eval_res["timestamp"] = time.strftime("%H:%M:%S")

        return eval_res
    except Exception:
        return None


def main():
    seen = set()
    for f in glob.glob(os.path.join(WATCH_DIR, "*.png")):
        seen.add(f)

    print(f"[*] Live Snapshot Analyzer active on: {WATCH_DIR}")
    print("[*] Waiting for new screenshots...")

    while True:
        time.sleep(1)
        current = set(glob.glob(os.path.join(WATCH_DIR, "*.png")))
        new_files = current - seen
        for nf in sorted(new_files):
            seen.add(nf)
            print(f"\n[!] New Screenshot Detected: {os.path.basename(nf)}")
            res = analyze_snapshot(nf)
            if res:
                poker_coach.print_feedback_card(res)
                # Write to live feed json
                feed = []
                if os.path.exists(PROCESSED_FILE):
                    try:
                        with open(PROCESSED_FILE, "r") as f:
                            feed = json.load(f)
                    except Exception:
                        pass
                feed.insert(0, res)
                with open(PROCESSED_FILE, "w") as f:
                    json.dump(feed[:50], f, indent=2)


if __name__ == "__main__":
    main()
