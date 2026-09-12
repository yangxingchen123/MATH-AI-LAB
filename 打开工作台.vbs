Option Explicit
Dim sh, fso, root, cmd
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = root
cmd = "cmd /c tools\qt_workbench\launch.cmd"
sh.Run cmd, 0, False
