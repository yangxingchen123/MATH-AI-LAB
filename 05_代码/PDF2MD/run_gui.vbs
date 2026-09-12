' Silent GUI launcher: no console / Windows Terminal window.
Option Explicit
Dim sh, fso, root, pyw, script
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = root
script = root & "\run_gui.py"
pyw = root & "\.venv\Scripts\pythonw.exe"
If fso.FileExists(pyw) Then
  sh.Run """" & pyw & """ """ & script & """", 0, False
Else
  sh.Run "pythonw """ & script & """", 0, False
End If
