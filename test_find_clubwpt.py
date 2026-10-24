import psutil
import win32gui
import win32process


def find_clubwpt_tables():
    club_pids = set()
    for p in psutil.process_iter(["name", "pid"]):
        try:
            if "clubwpt" in p.info["name"].lower():
                club_pids.add(p.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    print(f"ClubWPT PIDs: {club_pids}")

    tables = []

    def enum_cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid in club_pids:
                rect = win32gui.GetWindowRect(hwnd)
                w = rect[2] - rect[0]
                h = rect[3] - rect[1]
                title = win32gui.GetWindowText(hwnd)
                if w > 500 and h > 400:
                    tables.append((hwnd, pid, rect, title, w * h))
        return True

    try:
        win32gui.EnumWindows(enum_cb, None)
    except Exception as exc:
        print(f"[!] Window enumeration error: {exc}")

    tables.sort(key=lambda x: x[4], reverse=True)
    return tables


if __name__ == "__main__":
    t = find_clubwpt_tables()
    print("Found tables:", t)
