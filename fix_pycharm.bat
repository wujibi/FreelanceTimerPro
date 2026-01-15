@echo off
REM Fix PyCharm configuration after folder rename
REM This script updates .idea configuration files to use new path

echo ================================================
echo PyCharm Configuration Fix
echo ================================================
echo.
echo This will update PyCharm configuration files to use the new folder path:
echo OLD: App Projects\TimeTrackerProV2
echo NEW: AppProjects\TimeTrackerProV2
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Step 1: Backing up .idea folder...
if exist ".idea_backup" (
    echo   Removing old backup...
    rmdir /s /q ".idea_backup"
)
xcopy /E /I /Y ".idea" ".idea_backup" > nul
echo   ✓ Backup created at .idea_backup
echo.

echo Step 2: Close PyCharm if it's running...
echo   Please close PyCharm now if it's open!
pause

echo.
echo Step 3: The easiest fix is to delete .idea and let PyCharm recreate it...
echo   Would you like to delete the .idea folder? (PyCharm will recreate it)
echo   Your backup is safe in .idea_backup
echo.
set /p DELETE_IDEA="Delete .idea folder? (y/n): "

if /i "%DELETE_IDEA%"=="y" (
    echo   Deleting .idea folder...
    rmdir /s /q ".idea"
    echo   ✓ .idea folder deleted
    echo.
    echo   Next steps:
    echo   1. Open this project in PyCharm
    echo   2. PyCharm will recreate .idea with correct paths
    echo   3. Configure Python interpreter:
    echo      File → Settings → Project → Python Interpreter
    echo      Select: .venv\Scripts\python.exe in this folder
    echo.
) else (
    echo   .idea folder kept. You can manually fix paths in:
    echo   - .idea\misc.xml
    echo   - .idea\TimeTrackerProV2.iml
    echo.
)

echo.
echo ================================================
echo Fix Complete!
echo ================================================
echo.
echo Backup location: .idea_backup
echo.
pause
