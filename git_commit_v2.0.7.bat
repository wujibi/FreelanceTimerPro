@echo off
echo ========================================
echo Time Tracker Pro - Git Commit v2.0.7
echo ========================================
echo.

cd /d "%~dp0"

echo Adding all changes...
git add .

echo.
echo Committing with message...
git commit -m "v2.0.7 - Critical bug fixes: Email template save + Task deletion + HTML preview"

echo.
echo Pushing to GitHub...
git push origin master

echo.
echo ========================================
echo Done! Changes pushed to GitHub.
echo ========================================
pause
