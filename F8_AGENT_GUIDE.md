# ♠️ F8 Poker Hand Intelligence Agent Guide

The **F8 Hand Intelligence Agent** is a dedicated poker coach and real-time exploitative specialist designed to analyze high-priority, on-demand table captures from **ClubWPT Gold** (and other online tables).

---

## ⚡ How It Works

1. **Press `[F8]` In-Game**:
   While running `run_collector.bat`, press **F8** whenever you are faced with a tough decision or want a full hand breakdown.
   * `clubwpt_collector.py` captures the table and saves an `analyze_hand_manual_f8_*.webp` screenshot.

2. **Autonomous F8 Agent Detection**:
   The dedicated F8 agent (`f8_poker_agent.py` / `run_f8_analyst.bat`) immediately detects the F8 capture.

3. **Frontier Multimodal AI Analysis**:
   * Evaluates the screenshot using **OpenAI GPT-6-Astra** via the authenticated local Codex bridge.
   * Extracts Hero hole cards, position, pot size in BB, stack depths, and betting actions.
   * Scans all table opponents and dynamically updates their profiles in `hands/processed/opponents.json`.
   * Solves the spot using GTO baselines + exploitative adjustments tailored to table opponents.

4. **Instant Coaching Feedback & Persistence**:
   * Displays an immediate, colorized terminal **Coaching Card**.
   * Appends a detailed strategic breakdown into `hands/processed/F8_ANALYSIS_REPORTS.md`.
   * Archives structured JSON telemetry to `hands/processed/f8_analysis_log.json`.
   * Emits a double-tone audio confirmation.

---

## 🚀 Running the F8 Agent

### 1. Real-Time Watch Mode (Recommended)
Double-click `run_f8_analyst.bat` or run:
```powershell
python f8_poker_agent.py --watch
```
*Keeps running silently in the background, waking up instantly whenever you hit `[F8]`.*

### 2. Analyze the Latest F8 Hand On-Demand
```powershell
python f8_poker_agent.py --latest
```

### 3. Analyze All Pending F8 Hands
```powershell
python f8_poker_agent.py --all
```

### 4. Analyze a Specific Screenshot File
```powershell
python f8_poker_agent.py --file "hands/raw/clubwpt/analyze_hand_20261023_224103.png"
```

### 5. Clear the F8 Queue (Start Fresh)
Double-click **`clear_f8_queue.bat`** or run:
```powershell
python f8_poker_agent.py --clear-queue
```
*Marks all existing captures as cleared so future runs don't process old backlogs.*

---

## 💬 In-Chat Antigravity Subagent

You can also invoke the dedicated **`f8-hand-analyst`** subagent directly in Antigravity chat:
- Ask the agent: *"Analyze the latest F8 hand"* or *"Review all F8 captures from tonight's session"*.
- The subagent has direct access to inspect table screenshots, review solver outputs, update opponent notes, and formulate customized exploitative strategies.
