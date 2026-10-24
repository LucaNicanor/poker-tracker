@echo off
title Clear F8 Analysis Queue
cd /d "%~dp0"
echo ============================================================
echo  Clearing pending F8 hand captures from analysis queue...
echo ============================================================
python f8_poker_agent.py --clear-queue
pause
