Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get script location
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Get Start Menu path
strStartMenu = objShell.SpecialFolders("Programs")

' Create shortcut in Start Menu
Set objShortcut = objShell.CreateShortcut(strStartMenu & "\TimeTracker Pro.lnk")
objShortcut.TargetPath = "pythonw.exe"
objShortcut.Arguments = Chr(34) & strScriptPath & "\main.py" & Chr(34)
objShortcut.WorkingDirectory = strScriptPath
objShortcut.Description = "TimeTracker Pro - Payment Tracking"

' Use custom icon if it exists
strIconPath = strScriptPath & "\timetracker.ico"
If objFSO.FileExists(strIconPath) Then
    objShortcut.IconLocation = strIconPath
End If

objShortcut.Save

MsgBox "Start Menu shortcut created!" & vbCrLf & vbCrLf & "You can now pin it to Start or Taskbar", vbInformation, "TimeTracker Pro"
