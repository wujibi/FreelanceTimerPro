@echo off
echo ========================================
echo Git Commit - Freelance Timer Pro v2.0.8
echo ========================================
echo.
echo Changes:
echo - Theme system implemented (modular themes/)
echo - Live theme switcher in Company Info tab
echo - Theme persistence (saves to database)
echo - App renamed: Time Tracker Pro -^> Freelance Timer Pro
echo - Documentation: THEME_SWITCHER_GUIDE.md, APP_RENAME_GUIDE.md
echo.
pause

cd /d "%~dp0"

echo.
echo Adding all changes...
git add .

echo.
echo Committing...
git commit -m "v2.0.8: Theme system + rebranding - Modular themes, live switcher, renamed to Freelance Timer Pro"

echo.
echo Pushing to GitHub...
git push

echo.
echo ========================================
echo Done! Check output above for errors.
echo ========================================
pause
