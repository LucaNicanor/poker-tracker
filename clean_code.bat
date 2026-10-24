@echo off
setlocal
echo ================================================================
echo           CLEAN CODE AUDIT, FORMAT & TEST SUITE
echo ================================================================

echo.
echo [*] Step 1: Formatting code with Ruff...
python -m ruff format gpt_poker_analyst.py test_gpt_poker_analyst.py clubwpt_collector.py poker_coach.py auto_snapshot_analyzer.py opponent_profiler.py

echo.
echo [*] Step 2: Running Ruff Clean Code linter...
python -m ruff check gpt_poker_analyst.py test_gpt_poker_analyst.py --select E,F,I,D,B --ignore D203,D213

echo.
echo [*] Step 3: Running Python unit tests...
python -m unittest test_gpt_poker_analyst.py -v

echo.
echo [*] Step 4: Running Node inbox unit tests...
node --test inbox.test.js

echo.
echo ================================================================
echo           ALL CLEAN CODE CHECKS COMPLETED!
echo ================================================================
pause
