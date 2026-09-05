$ErrorActionPreference = 'Stop'
$compiler = "$env:SystemRoot\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (!(Test-Path -LiteralPath $compiler)) { $compiler = "$env:SystemRoot\Microsoft.NET\Framework\v4.0.30319\csc.exe" }
if (!(Test-Path -LiteralPath $compiler)) { throw 'The Windows .NET Framework C# compiler is required.' }
$version = (Get-Content -LiteralPath "$PSScriptRoot\VERSION" -Raw).Trim()
if ($version -notmatch '^\d+\.\d+\.\d+$') { throw 'VERSION must be MAJOR.MINOR.PATCH.' }
$dist = New-Item -ItemType Directory -Force -Path "$PSScriptRoot\dist"
foreach ($wrapper in Import-Csv -LiteralPath "$PSScriptRoot\wrappers.csv") {
    if ($wrapper.Name -notmatch '^[a-z]+yolo$' -or $wrapper.Command -notmatch '^[a-z]+$' -or $wrapper.Permission -notmatch '^--[a-z-]+$') { throw 'Invalid wrapper manifest.' }
    $metadata = @"
using System.Reflection;
[assembly: AssemblyVersion("$version")]
[assembly: AssemblyFileVersion("$version")]
[assembly: AssemblyInformationalVersion("$version")]
[assembly: AssemblyProduct("agent-yolo")]
internal static class Wrapper {
    internal const string Name = "$($wrapper.Name)";
    internal const string Command = "$($wrapper.Command)";
    internal const string Permission = "$($wrapper.Permission)";
}
"@
    $source = Join-Path $dist "$($wrapper.Name).cs"
    [IO.File]::WriteAllText($source, $metadata)
    & $compiler /nologo /target:exe /optimize+ /warnaserror+ "/out:$dist\$($wrapper.Name).exe" "$PSScriptRoot\launcher.cs" $source
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $($wrapper.Name)" }
}
Write-Output "Built agent-yolo $version in $dist"
