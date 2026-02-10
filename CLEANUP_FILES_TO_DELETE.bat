@echo off
REM ========================================
REM CLEANUP SCRIPT - V2.0.9 Production Prep
REM Delete obsolete theme and doc files
REM ========================================

echo.
echo ========================================
echo   Freelance Timer Pro - File Cleanup
echo   Version 2.0.9 Production Prep
echo ========================================
echo.
echo This script will DELETE the following files:
echo.
echo OBSOLETE THEMES (6 files):
echo   - themes\balanced_navy.py
echo   - themes\burnt_orange.py (old version)
echo   - themes\deep_navy_pro.py
echo   - themes\light_navy_pro.py
echo   - themes\sage_professional.py
echo   - themes\warm_professional.py
echo.
echo TEMP DOCUMENTATION (10 files):
echo   - ADD_ALTERNATING_ROWS.md
echo   - ALTERNATING_ROWS_COMPLETE.md
echo   - ALTERNATING_ROWS_READY.md
echo   - FINAL_COLOR_FIXES.md
echo   - GROUP_HEADING_FIX_INSTRUCTIONS.md
echo   - LIGHT_THEME_ADDED.md
echo   - THEME_CLEANUP_INSTRUCTIONS.md
echo   - THEME_COMPARISON_GUIDE.md
echo   - THEME_SWITCHER_GUIDE.md
echo   - "Time Tracker Pro V2 - Theme-Stylesheet System Implementation.md"
echo.
echo KEEPING (Reference):
echo   + BURNT_ORANGE_COLOR_MAP.html (for future Theme Customizer)
echo.
echo ========================================
echo.
set /p CONFIRM="Are you sure you want to DELETE these files? (yes/no): "

if /i NOT "%CONFIRM%"=="yes" (
    echo.
    echo Cleanup cancelled. No files deleted.
    echo.
    pause
    exit /b
)

echo.
echo Deleting obsolete theme files...

del /f "themes\balanced_navy.py" 2>nul && echo   [OK] balanced_navy.py
del /f "themes\burnt_orange.py" 2>nul && echo   [OK] burnt_orange.py
del /f "themes\deep_navy_pro.py" 2>nul && echo   [OK] deep_navy_pro.py
del /f "themes\light_navy_pro.py" 2>nul && echo   [OK] light_navy_pro.py
del /f "themes\sage_professional.py" 2>nul && echo   [OK] sage_professional.py
del /f "themes\warm_professional.py" 2>nul && echo   [OK] warm_professional.py

echo.
echo Deleting temp documentation files...

del /f "ADD_ALTERNATING_ROWS.md" 2>nul && echo   [OK] ADD_ALTERNATING_ROWS.md
del /f "ALTERNATING_ROWS_COMPLETE.md" 2>nul && echo   [OK] ALTERNATING_ROWS_COMPLETE.md
del /f "ALTERNATING_ROWS_READY.md" 2>nul && echo   [OK] ALTERNATING_ROWS_READY.md
del /f "FINAL_COLOR_FIXES.md" 2>nul && echo   [OK] FINAL_COLOR_FIXES.md
del /f "GROUP_HEADING_FIX_INSTRUCTIONS.md" 2>nul && echo   [OK] GROUP_HEADING_FIX_INSTRUCTIONS.md
del /f "LIGHT_THEME_ADDED.md" 2>nul && echo   [OK] LIGHT_THEME_ADDED.md
del /f "THEME_CLEANUP_INSTRUCTIONS.md" 2>nul && echo   [OK] THEME_CLEANUP_INSTRUCTIONS.md
del /f "THEME_COMPARISON_GUIDE.md" 2>nul && echo   [OK] THEME_COMPARISON_GUIDE.md
del /f "THEME_SWITCHER_GUIDE.md" 2>nul && echo   [OK] THEME_SWITCHER_GUIDE.md
del /f "Time Tracker Pro V2 - Theme-Stylesheet System Implementation.md" 2>nul && echo   [OK] Theme System Implementation.md

echo.
echo ========================================
echo   Cleanup Complete!
echo ========================================
echo.
echo Remaining production files:
echo   + 3 Burnt Orange theme variants (pro, v2, v3)
echo   + Professional Gray theme
echo   + Dark Mode theme
echo   + BURNT_ORANGE_COLOR_MAP.html (reference)
echo   + All production documentation
echo.
echo Your app is now tidy and production-ready!
echo.
pause
