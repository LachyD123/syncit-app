@echo off
cd %~dp0
echo Current directory: %cd%
echo Installing Python requirements...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 pause
echo Installation complete.
pause