import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32
count = [0]
all_wins = []


def enum_cb(hwnd, lparam):
    count[0] += 1
    pid = ctypes.wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    buf = ctypes.create_unicode_buffer(512)
    user32.GetWindowTextW(hwnd, buf, 512)
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    all_wins.append(
        (hwnd, pid.value, buf.value, rect.right - rect.left, rect.bottom - rect.top)
    )
    return True


WNDENUMPROC = ctypes.WINFUNCTYPE(
    ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM
)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

print(f"Total windows visited: {count[0]}")
non_empty = [w for w in all_wins if w[2].strip()]
print(f"Non-empty titles: {len(non_empty)}")
for w in non_empty[:20]:
    print(w)
