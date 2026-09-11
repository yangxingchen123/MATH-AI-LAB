# Create / refresh PDF2MD.lnk next to project root (install / first setup; not every GUI launch).
param(
    [string]$Root = "",
    [string]$TargetBat = ""
)

$ErrorActionPreference = "Stop"
if (-not $Root) {
    $Root = Split-Path -Parent $PSScriptRoot
}
$Root = (Resolve-Path $Root).Path
$icon = Join-Path $Root "icons\pdf2md.ico"
if (-not (Test-Path -LiteralPath $icon)) {
    Write-Error "Icon not found: $icon"
}

$pyw = Join-Path $Root ".venv\Scripts\pythonw.exe"
$script = Join-Path $Root "run_gui.py"
$vbs = Join-Path $Root "run_gui.vbs"

$lnkPath = Join-Path $Root "PDF2MD.lnk"
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($lnkPath)
if (Test-Path -LiteralPath $pyw) {
    $s.TargetPath = $pyw
    $s.Arguments = "`"$script`""
    $s.WorkingDirectory = $Root
}
elseif (Test-Path -LiteralPath $vbs) {
    $s.TargetPath = "wscript.exe"
    $s.Arguments = "`"$vbs`""
    $s.WorkingDirectory = $Root
}
else {
    if (-not $TargetBat) {
        $candidates = @(
            (Join-Path $Root "启动PDF2MD.bat"),
            (Join-Path $Root "run_gui.bat")
        )
        foreach ($c in $candidates) {
            if (Test-Path -LiteralPath $c) { $TargetBat = $c; break }
        }
    }
    if (-not $TargetBat -or -not (Test-Path -LiteralPath $TargetBat)) {
        Write-Error "pythonw.exe / run_gui.vbs / launcher bat not found under $Root"
    }
    $s.TargetPath = $TargetBat
    $s.Arguments = ""
    $s.WorkingDirectory = $Root
}
$s.WindowStyle = 7
$s.IconLocation = "$icon,0"
$s.Description = "PDF2MD — academic PDF to Markdown"
$s.Save()
Write-Output "Shortcut ready: $lnkPath"
