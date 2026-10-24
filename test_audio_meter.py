from pycaw.pycaw import AudioUtilities, IAudioMeterInformation


def check_clubwpt_audio():
    sessions = AudioUtilities.GetAllSessions()
    found = False
    for s in sessions:
        if s.Process and "clubwpt" in s.Process.name().lower():
            found = True
            meter = s._ctl.QueryInterface(IAudioMeterInformation)
            peak = meter.GetPeakValue()
            print(
                f"[Audio] PID {s.Process.pid} ({s.Process.name()}): Peak = {peak:.4f}"
            )
    if not found:
        print("[Audio] No ClubWPT audio session currently active.")


if __name__ == "__main__":
    print("Testing Audio Session Detection:")
    check_clubwpt_audio()
