@echo off
REM Git commands for v2.0.4 update - January 21, 2026
REM Run this from the TimeTrackerProV2 directory

echo ========================================
echo Time Tracker Pro v2.0.4 - Git Push
echo ========================================
echo.

REM Change to project directory
cd /d "C:\Users\briah\OneDrive\TypingMind\ClaudeWorkspace\AppProjects\TimeTrackerProV2"

echo Step 1: Check current status...
git status
echo.
echo.

pause
echo.

echo Step 2: Add all changed files...
git add .
echo Files staged for commit.
echo.

pause
echo.

echo Step 3: Commit with message...
git commit -m "Version 2.0.4 - Fixed time entry edit + Invoice tab grouping" -m "- Fixed: Time entry edit bug with global tasks (simplified query)" -m "- Added: Invoice tab hierarchical grouping (Project → Task → Entry)" -m "- Fixed: Select/Deselect All buttons work with hierarchy" -m "- Updated: Documentation (CHANGELOG, CURRENT_STATUS, TIMETRACKER_CONTEXT)"
echo.
echo Commit complete!
echo.

pause
echo.

echo Step 4: Push to GitHub...
git push origin master
echo.
echo Push complete!
echo.

pause
echo.
echo ========================================
echo All done! Changes pushed to GitHub.
echo ========================================
pause
