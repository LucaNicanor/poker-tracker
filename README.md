# ClubWPT Gold Real-Time Poker Assistant & Auto Tracker

A lightweight, non-intrusive poker analysis and tracking toolkit for ClubWPT Gold. Automatically tracks all streets (Deal, Flop, Turn, River), provides 1-click on-demand GTO hand analysis via hotkeys, and organizes hands locally without transmitting private credentials.

---

## Features

* **Multi-Street Auto-Capture (`clubwpt_collector.py`)**:
  * Auto-detects table windows and automatically captures Deal, Flop, Turn, and River states in real-time.
  * Preserves sharp WebP captures with zero table lag.
* **Instant GTO & Live Coach (`f8_poker_agent.py`)**:
  * **F8 Hotkey:** 1-click snapshot analysis with instant preflop heuristics (0.05s response time) and background AI analysis.
  * **F9 Hotkey:** Instant hand bookmarking for big pots and cooler reviews.
* **Hand Inbox & Local Viewer (`server.js`)**:
  * Run a local dashboard at `http://127.0.0.1:3316` to view, catalog, and review previous hand histories.
* **Privacy by Default**:
  * All hand captures, opponent notes, and screenshots are stored strictly locally in `hands/raw/` and excluded from git version control.

---

## Quick Start (For Friends)

### 1. Requirements
* Windows 10 or 11
* Python 3.10+
* (Optional) Node.js 18+ for the local web inbox

### 2. Setup
Install required Python libraries:
```bash
pip install -r requirements.txt
```

### 3. Launching
* **Start Auto-Tracker & Hotkeys:**
  Double-click `run_collector.bat` (or run `python clubwpt_collector.py`).
  * While playing on ClubWPT Gold:
    * Press **F8** at any time to analyze the current table action and get GTO advice.
    * Press **F9** at any time to bookmark an important hand for post-session review.
* **Start Background Live Coach:**
  Double-click `run_f8_analyst.bat` (or run `python f8_poker_agent.py`).
* **Start Local Hand Inbox:**
  Double-click `server.js` or run `npm start`, then open `http://127.0.0.1:3316`.

---

## File Structure

* `clubwpt_collector.py` - Background screen grabber and hotkey listener.
* `f8_poker_agent.py` - Real-time poker analysis engine.
* `poker_coach.py` - Preflop GTO range charts and heuristics.
* `server.js` & `index.html` - Local hand history inbox and viewer.
* `run_collector.bat` - 1-click launcher for the screen collector.
* `run_f8_analyst.bat` - 1-click launcher for the live coach.
* `clear_f8_queue.bat` - Clears pending background vision queues.
