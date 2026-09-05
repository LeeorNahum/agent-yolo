@echo off
setlocal DisableDelayedExpansion
if not exist "%~dp0codexyolo.exe" goto checkout
"%~dp0codexyolo.exe" %*
exit /b %errorlevel%
:checkout
"%~dp0..\dist\codexyolo.exe" %*
exit /b %errorlevel%
