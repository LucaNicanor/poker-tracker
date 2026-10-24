@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo   Pushing ClubWPT Poker Assistant to GitHub
echo ========================================================
echo.

"C:\Program Files\Git\cmd\git.exe" remote -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] No git remote configured yet.
    set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/LucaNicanor/poker-bot.git): "
    "C:\Program Files\Git\cmd\git.exe" remote add origin "%REPO_URL%"
)

echo.
echo Pushing 'main' branch to GitHub...
"C:\Program Files\Git\cmd\git.exe" push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Code published to GitHub! Your friends can now clone it.
) else (
    echo.
    echo [ERROR] Push failed. Make sure the repository exists on GitHub and you have permission.
)

pause
