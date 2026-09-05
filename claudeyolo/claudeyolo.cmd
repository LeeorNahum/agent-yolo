@echo off
setlocal DisableDelayedExpansion
if not exist "%~dp0claudeyolo.exe" goto checkout
"%~dp0claudeyolo.exe" %*
exit /b %errorlevel%
:checkout
"%~dp0..\dist\claudeyolo.exe" %*
exit /b %errorlevel%
