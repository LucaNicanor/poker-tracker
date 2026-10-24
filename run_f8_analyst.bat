@echo off
title F8 Poker Hand Intelligence Agent
cd /d "%~dp0"
echo ============================================================
echo  Starting F8 Poker Hand Intelligence Agent (Real-Time Watch)...
echo  Press [F8] in ClubWPT to trigger on-demand AI hand analysis.
echo ============================================================
python f8_poker_agent.py --watch
pause
