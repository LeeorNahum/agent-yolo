@echo off
setlocal DisableDelayedExpansion
if not exist "%~dp0claudexyolo.exe" goto checkout
"%~dp0claudexyolo.exe" %*
exit /b %errorlevel%
:checkout
"%~dp0..\dist\claudexyolo.exe" %*
exit /b %errorlevel%
