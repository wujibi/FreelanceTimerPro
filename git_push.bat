@echo off
echo ============================================================
echo  FreelanceTimerPro - Git Commit and Push
echo ============================================================
echo.

cd /d "%~dp0"

echo Current changes:
echo.
git status --short
echo.

REM Prompt for commit message
set /p MSG="Enter commit message (or press Enter for default): "
if "%MSG%"=="" set MSG=Update FreelanceTimerPro

echo.
echo [1/3] Staging all changes...
git add -A

echo [2/3] Committing: "%MSG%"
git commit -m "%MSG%"

echo [3/3] Pushing to GitHub...
git push origin master

echo.
echo ============================================================
echo  Done! Changes are now live on GitHub.
echo  https://github.com/wujibi/FreelanceTimerPro
echo ============================================================
echo.
pause
