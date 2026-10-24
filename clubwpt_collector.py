"""
ClubWPT Gold Collector & F8 On-Demand Coach
-------------------------------------------
Controls:
• [F8]: ANALYZE THIS HAND! (Captures table & alerts the AI agent in chat to do a full breakdown)
• [F9]: SILENT RECORD (Archives the hand to disk silently with a single quiet chime, no chat analysis)
• Auto-capture runs silently in the background.
"""

import datetime
import glob
import os
import re
import threading
import time
import winsound

import psutil
import win32gui
import win32process
from PIL import ImageDraw, ImageGrab, ImageStat

SAVE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "hands", "raw", "clubwpt"
)
os.makedirs(SAVE_DIR, exist_ok=True)
LOG_PATH = os.path.join(SAVE_DIR, "screenshot_log.txt")
CAPTURE_LOCK = threading.Lock()


def print_existing_catalog():
    """Show the most recent captures, using recorded metadata when available."""
    records = {}
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, encoding="utf-8") as log:
            for line in log:
                fields = line.rstrip("\n").split("\t")
                if len(fields) == 4:
                    records[fields[3]] = fields[:3]
    files = [
        f
        for f in glob.glob(os.path.join(SAVE_DIR, "*"))
        if os.path.isfile(f) and f.lower().endswith((".png", ".webp", ".jpg", ".jpeg"))
    ]
    files.sort(key=os.path.getmtime)
    print("\n" + "=" * 68)
    print(f"RECENT SCREENSHOTS ({len(files)} total; showing latest 15)")
    if not files:
        print("  No previous screenshots in archive yet.")
    for path in files[-15:]:
        name = os.path.basename(path)
        if name in records:
            stamp, mode, table_id = records[name]
        else:
            match = re.search(r"_(\d{8}_\d{6})(?:_\d{6})?\.[^.]+$", name)
            captured_at = (
                datetime.datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
                if match
                else datetime.datetime.fromtimestamp(os.path.getmtime(path))
            )
            stamp = captured_at.strftime("%Y-%m-%d %I:%M:%S %p")
            lower = name.lower()
            mode = (
                "MANUAL F8"
                if "analyze" in lower
                else "MANUAL F9"
                if "f9" in lower
                else "AUTO DEAL"
                if "auto_deal" in lower
                else "AUTO FLOP"
                if "auto_flop" in lower
                else "AUTO TURN"
                if "auto_turn" in lower
                else "AUTO RIVER"
                if "auto_river" in lower
                else "AUTO ACTION"
                if "auto_action" in lower
                else "UNKNOWN (legacy AUTO/MANUAL)"
            )
            table_id = "legacy"
        print(f"  [{stamp}] [{mode} | {table_id}] {name}")
    print("=" * 68 + "\n", flush=True)


def get_active_or_focused_table():
    """
    Finds all active ClubWPT tables.
    Returns the table currently in focus, or the one with the highest priority.
    Supports multi-tabling across up to 4+ tables.
    """
    club_pids = set()
    for p in psutil.process_iter(["name", "pid"]):
        try:
            if "clubwpt" in p.info["name"].lower():
                club_pids.add(p.info["pid"])
        except Exception:
            pass

    tables = []
    fg_hwnd = win32gui.GetForegroundWindow()

    def enum_cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]
            title = win32gui.GetWindowText(hwnd)
            is_clubwpt = pid in club_pids
            is_poker_title = any(
                k in title.lower()
                for k in ["ring game", "tournament", "nlhe", "clubwpt", "chips"]
            )
            if (is_clubwpt or is_poker_title) and w > 400 and h > 300:
                is_focused = hwnd == fg_hwnd
                # Extract clean table ID from title (e.g. "HL3990" or "Freeroll")
                table_id = "Table"
                if "|" in title:
                    table_id = title.split("|")[-1].strip().replace(" ", "_")
                elif "tournament" in title.lower():
                    table_id = "Tourney"
                tables.append(
                    {
                        "hwnd": hwnd,
                        "pid": pid,
                        "rect": rect,
                        "title": title,
                        "table_id": table_id,
                        "is_focused": is_focused,
                    }
                )
        return True

    try:
        win32gui.EnumWindows(enum_cb, None)
    except Exception:
        pass

    if not tables:
        return None

    # If currently focused window is a table, prioritize it
    focused = [t for t in tables if t["is_focused"]]
    if focused:
        return focused[0]

    # Otherwise return the largest table
    tables.sort(
        key=lambda t: (t["rect"][2] - t["rect"][0]) * (t["rect"][3] - t["rect"][1]),
        reverse=True,
    )
    return tables[0]


def capture_table(is_f8_request=False, reason="silent"):
    table = get_active_or_focused_table()

    table_id = table["table_id"] if table else "Table"
    capture_type = (
        "MANUAL F8"
        if is_f8_request
        else "MANUAL F9"
        if "f9" in reason.lower()
        else "AUTO FLOP"
        if "flop" in reason.lower()
        else "AUTO TURN"
        if "turn" in reason.lower()
        else "AUTO RIVER"
        if "river" in reason.lower()
        else "AUTO ACTION"
        if "action" in reason.lower()
        else "AUTO DEAL"
    )
    prefix = "analyze_hand" if is_f8_request else "clubwpt_hand"
    prefix += "_" + capture_type.lower().replace(" ", "_")

    if table:
        rect = table["rect"]
    else:
        fg_hwnd = win32gui.GetForegroundWindow()
        rect = win32gui.GetWindowRect(fg_hwnd)

    bbox = (max(0, rect[0]), max(0, rect[1]), rect[2], rect[3])

    try:
        with CAPTURE_LOCK:
            captured_at = datetime.datetime.now().astimezone()
            timestamp = captured_at.strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{prefix}_{table_id}_{timestamp}.webp"
            filepath = os.path.join(SAVE_DIR, filename)
            img = ImageGrab.grab(bbox=bbox, all_screens=True)

        # Stamp timestamp directly on the image corner (visible on the screenshot)
        draw = ImageDraw.Draw(img)
        ts_display = captured_at.strftime("%Y-%m-%d %I:%M:%S.%f %p %z")
        label = f"[{ts_display} | {capture_type} | {table_id}]"
        # Draw dark badge in bottom-left
        badge_width = draw.textbbox((0, 0), label)[2] + 22
        draw.rectangle(
            [10, img.height - 35, badge_width, img.height - 10], fill=(0, 0, 0)
        )
        draw.text((16, img.height - 30), label, fill=(255, 255, 255))

        # WebP compression at quality 85 preserves razor sharp cards and text
        temp_filepath = filepath + '.tmp'
        img.save(temp_filepath, 'WEBP', quality=85, method=6)
        os.replace(temp_filepath, filepath)

        time_str = captured_at.strftime("%I:%M:%S.%f %p")
        with CAPTURE_LOCK:
            print(
                f"[{time_str}] [{capture_type} | {table_id}] Saved: {filename}",
                flush=True,
            )
            try:
                with open(LOG_PATH, "a", encoding="utf-8") as log:
                    log.write(f"{ts_display}\t{capture_type}\t{table_id}\t{filename}\n")
            except OSError as exc:
                print(f"[!] Screenshot saved but log append failed: {exc}", flush=True)
        if is_f8_request:
            winsound.Beep(1600, 150)
        elif "f9" in reason.lower():
            winsound.Beep(1100, 100)

        return img
    except Exception as e:
        print(f"[-] Capture error: {e}")
        return None


def check_cards_present(img):
    if img is None:
        return False
    w, h = img.size
    crop_box = (int(w * 0.48), int(h * 0.62), int(w * 0.56), int(h * 0.73))
    patch = img.crop(crop_box)
    stat = ImageStat.Stat(patch)
    mean_brightness = sum(stat.mean) / len(stat.mean)
    max_brightness = max([stat.extrema[i][1] for i in range(len(stat.extrema))])
    return max_brightness > 190 and mean_brightness > 60


def count_board_cards(img):
    """
    Counts how many community cards are currently dealt on the board:
    0 = Preflop (no board cards)
    3 = Flop
    4 = Turn
    5 = River
    """
    if img is None:
        return 0
    w, h = img.size
    # 5 community card slots across the center of the table
    slots = [
        (0.35, 0.41),  # Flop 1
        (0.41, 0.47),  # Flop 2
        (0.47, 0.53),  # Flop 3
        (0.53, 0.60),  # Turn 4
        (0.60, 0.67),  # River 5
    ]
    board_count = 0
    for x1, x2 in slots:
        crop = img.crop((int(w * x1), int(h * 0.40), int(w * x2), int(h * 0.54)))
        stat = ImageStat.Stat(crop)
        max_b = max([stat.extrema[i][1] for i in range(len(stat.extrema))])
        mean_b = sum(stat.mean) / len(stat.mean)
        if max_b > 200 and mean_b > 65:
            board_count += 1
    return board_count


def monitor_loop(stop_event):
    cards_dealt_state = False
    last_board_cards = 0

    while not stop_event.is_set():
        time.sleep(0.5)
        table = get_active_or_focused_table()
        if not table:
            continue
        rect = table["rect"]
        bbox = (max(0, rect[0]), max(0, rect[1]), rect[2], rect[3])

        try:
            sample = ImageGrab.grab(bbox=bbox, all_screens=True)
        except Exception:
            continue

        cards_present = check_cards_present(sample)
        board_cards = count_board_cards(sample)

        # 1. Preflop deal detection
        if not cards_dealt_state and cards_present:
            cards_dealt_state = True
            last_board_cards = 0
            capture_table(is_f8_request=False, reason="auto_deal")

        # 2. Multi-street community board progression
        elif cards_dealt_state or board_cards > 0:
            if board_cards >= 3 and last_board_cards < 3:
                last_board_cards = 3
                capture_table(is_f8_request=False, reason="auto_flop")
            elif board_cards >= 4 and last_board_cards < 4:
                last_board_cards = 4
                capture_table(is_f8_request=False, reason="auto_turn")
            elif board_cards == 5 and last_board_cards < 5:
                last_board_cards = 5
                capture_table(is_f8_request=False, reason="auto_river")

        # 3. Hand reset (table swept clean for next deal)
        if not cards_present and board_cards == 0:
            cards_dealt_state = False
            last_board_cards = 0


def main():
    print_existing_catalog()
    print("=" * 64)
    print(" ♠️ CLUBWPT GOLD RECORDER & MULTI-STREET TRACKER ♣️")
    print("=" * 64)
    print(" • AUTO: Automatically records all streets (Deal, Flop, Turn, River)")
    print(" • [F8]: ANALYZE HAND! (Wakes up AI agent in chat for deep breakdown)")
    print(" • [F9]: SILENT ARCHIVE (Saves hand quietly, no chat interruption)")
    print(" • Single, clean confirmation tone (No repeated beeps)")
    print(" • Type 'q' + Enter to quit")
    print("=" * 64)

    try:
        import keyboard

        keyboard.add_hotkey(
            "F8", lambda: capture_table(is_f8_request=True, reason="F8_Analyze")
        )
        keyboard.add_hotkey(
            "F9", lambda: capture_table(is_f8_request=False, reason="F9_Silent")
        )
        print("[*] Hotkeys [F8] (Analyze in Chat) and [F9] (Silent Save) are ACTIVE!")
    except Exception as e:
        print(f"[!] Hotkey error: {e}")

    stop_event = threading.Event()
    t = threading.Thread(target=monitor_loop, args=(stop_event,), daemon=True)
    t.start()

    try:
        while True:
            cmd = input().strip().lower()
            if cmd == "c":
                capture_table(is_f8_request=True, reason="Console_Analyze")
            elif cmd in ["q", "exit"]:
                break
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        stop_event.set()
        print("\nRecorder stopped.")


if __name__ == "__main__":
    main()
