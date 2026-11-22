@echo off
setlocal
pushd "%~dp0"
bash deploy.sh %*
set "RESULT=%ERRORLEVEL%"
popd
exit /b %RESULT%
