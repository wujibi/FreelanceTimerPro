@echo off
REM Generic Git Push Script for Time Tracker Pro
REM This script guides you through committing and pushing changes to GitHub

echo ========================================
echo Time Tracker Pro - Git Push Helper
echo ========================================
echo.

REM Change to project directory
cd /d "C:\Users\briah\OneDrive\TypingMind\ClaudeWorkspace\AppProjects\TimeTrackerProV2"

echo Step 1: Current Git Status
echo ========================================
git status
echo.
echo.

set /p CONTINUE="Continue with commit? (y/n): "
if /i not "%CONTINUE%"=="y" goto :END
echo.

echo Step 2: Staging Files
echo ========================================
git add .
echo All changes staged.
echo.
echo.

set /p VERSION="Enter version (e.g., 2.0.6): "
set /p TITLE="Enter brief title (e.g., UI improvements): "
echo.
echo Enter detailed changes (press Enter twice when done):
set /p DETAIL1="- "
set /p DETAIL2="- "
set /p DETAIL3="- "
echo.

echo Step 3: Committing Changes
echo ========================================
if "%DETAIL3%"=="" (
    if "%DETAIL2%"=="" (
        git commit -m "Version %VERSION% - %TITLE%" -m "- %DETAIL1%"
    ) else (
        git commit -m "Version %VERSION% - %TITLE%" -m "- %DETAIL1%" -m "- %DETAIL2%"
    )
) else (
    git commit -m "Version %VERSION% - %TITLE%" -m "- %DETAIL1%" -m "- %DETAIL2%" -m "- %DETAIL3%"
)
echo.
echo Commit complete!
echo.
echo.

set /p PUSH="Push to GitHub now? (y/n): "
if /i not "%PUSH%"=="y" goto :END
echo.

echo Step 4: Pushing to GitHub
echo ========================================
git push origin master
echo.
echo.

echo ========================================
echo SUCCESS! Changes pushed to GitHub.
echo ========================================
goto :END

:END
echo.
pause
