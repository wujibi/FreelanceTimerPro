Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get script location
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Get desktop path
strDesktop = objShell.SpecialFolders("Desktop")

' Create shortcut
Set objShortcut = objShell.CreateShortcut(strDesktop & "\TimeTracker Pro.lnk")
objShortcut.TargetPath = "pythonw.exe"
objShortcut.Arguments = Chr(34) & strScriptPath & "\main.py" & Chr(34)
objShortcut.WorkingDirectory = strScriptPath
objShortcut.Description = "TimeTracker Pro - Payment Tracking"
objShortcut.Save

MsgBox "Desktop shortcut created successfully!", vbInformation, "TimeTracker Pro"
