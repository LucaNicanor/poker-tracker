import ctypes
import ctypes.wintypes

user32 = ctypes.windll.user32

pids = {23564, 5392, 39072, 32136, 40900, 18744, 25588, 26268, 32300, 38648}
found_hwnds = []


def enum_cb(hwnd, lparam):
    pid = ctypes.wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value in pids:
        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)
        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        is_vis = user32.IsWindowVisible(hwnd)
        if w > 100 and h > 100:
            found_hwnds.append(
                (hwnd, pid.value, is_vis, rect.left, rect.top, w, h, buf.value)
            )
    return True


WNDENUMPROC = ctypes.WINFUNCTYPE(
    ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM
)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

print(f"Found {len(found_hwnds)} windows for ClubWPT:")
for h, p, vis, left, top, w, h_dim, title in found_hwnds:
    print(
        f"HWND: {h} | PID: {p} | Visible: {vis} | Pos: ({left}, {top}) | Size: {w}x{h_dim} | Title: '{title}'"
    )
