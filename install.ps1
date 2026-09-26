param([string[]] $Names)
$ErrorActionPreference = 'Stop'
& "$PSScriptRoot\build.ps1"
$wrappers = @(Import-Csv -LiteralPath "$PSScriptRoot\wrappers.csv")
foreach ($name in $Names) {
    if ($name -notin $wrappers.Name) { throw "Unknown wrapper: $name" }
}
function Install-Launcher([string] $Source, [string] $Destination) {
    # Windows locks a running executable against overwrite and delete but normally allows
    # renaming it, so stage the new copy, move the old one aside, and swap. Each install tries
    # to delete set-aside copies, which succeeds once nothing runs from them.
    $id = [guid]::NewGuid().ToString('N')
    $staged = "$Destination.$id.new"
    $aside = "$Destination.$id.old"
    try {
        Copy-Item -LiteralPath $Source -Destination $staged
        if (Test-Path -LiteralPath $Destination) {
            try { Move-Item -LiteralPath $Destination -Destination $aside }
            catch {
                # -2147024864 is HRESULT 0x80070020, ERROR_SHARING_VIOLATION: a handle without delete sharing.
                $advice = if ($_.Exception.HResult -eq -2147024864) { ' Another program has the file open. Close that program, or wait for a scan to finish, then rerun install.ps1.' } else { '' }
                throw "Cannot replace $Destination. $($_.Exception.Message)$advice"
            }
        }
        try { Move-Item -LiteralPath $staged -Destination $Destination }
        catch {
            if (!(Test-Path -LiteralPath $aside)) { throw "Cannot install $Destination. $($_.Exception.Message)" }
            Move-Item -LiteralPath $aside -Destination $Destination
            throw "Cannot install $Destination. The previous launcher was restored. $($_.Exception.Message)"
        }
    }
    finally { Remove-Item -LiteralPath $staged -Force -ErrorAction SilentlyContinue }
    $leftover = '^' + [regex]::Escape((Split-Path -Leaf $Destination)) + '\.[0-9a-f]{32}\.(old|new)$'
    Get-ChildItem -LiteralPath (Split-Path -Parent $Destination) -File | Where-Object { $_.Name -match $leftover } |
        ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue }
}
$bin = Join-Path $env:USERPROFILE '.local\bin'
$share = Join-Path $env:USERPROFILE '.local\share\agent-yolo'
New-Item -ItemType Directory -Force -Path $bin, $share | Out-Null
$installed = @()
foreach ($wrapper in $wrappers) {
    $name = $wrapper.Name
    $native = Get-Command "$($wrapper.Command).exe" -CommandType Application -ErrorAction SilentlyContinue
    $existing = (Test-Path -LiteralPath "$bin\$name.cmd") -or (Test-Path -LiteralPath "$bin\$name.exe")
    if ($Names.Count -gt 0) { if ($name -notin $Names) { continue } }
    elseif (!$native -and !$existing) { continue }
    $target = New-Item -ItemType Directory -Force -Path "$share\$name"
    Install-Launcher "$PSScriptRoot\dist\$name.exe" "$target\$name.exe"
    Copy-Item -LiteralPath "$PSScriptRoot\$name\$name.cmd" -Destination "$target\$name.cmd" -Force
    Install-Launcher "$PSScriptRoot\dist\$name.exe" "$bin\$name.exe"
    # Update existing shims too, so an explicit .cmd invocation cannot reach stale code.
    if (Test-Path -LiteralPath "$bin\$name.cmd") {
        Copy-Item -LiteralPath "$PSScriptRoot\$name\$name.cmd" -Destination "$bin\$name.cmd" -Force
    }
    $key = "HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths\$name.exe"
    New-Item -Path $key -Force | Out-Null
    Set-Item -LiteralPath $key -Value "$bin\$name.exe"
    $installed += $name
    if (!$native) { Write-Warning "$name installed, but $($wrapper.Command).exe is missing. A batch-only CLI cannot meet the argument and directory contract." }
}
$parts = @([Environment]::GetEnvironmentVariable('Path', 'User') -split ';' | Where-Object { $_.Trim() })
if (!($parts | Where-Object { $_.Trim().Trim('"').TrimEnd('\') -ieq $bin })) {
    [Environment]::SetEnvironmentVariable('Path', (($parts + $bin) -join ';'), 'User')
}
# App Paths takes effect immediately for Explorer without restarting it.
if (!('EnvironmentNotification' -as [type])) { Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class EnvironmentNotification {
    [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern IntPtr SendMessageTimeout(IntPtr window, uint message, UIntPtr wparam, string lparam, uint flags, uint timeout, out UIntPtr result);
}
'@
}
$result = [UIntPtr]::Zero
[EnvironmentNotification]::SendMessageTimeout([IntPtr]0xffff, 0x1a, [UIntPtr]::Zero, 'Environment', 2, 5000, [ref]$result) | Out-Null
Copy-Item -LiteralPath "$PSScriptRoot\VERSION", "$PSScriptRoot\wrappers.csv" -Destination $share -Force
Write-Output "Installed: $($installed -join ', ') in $bin"
