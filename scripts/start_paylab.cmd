@echo off
setlocal
cd /d "%~dp0.."
python scripts\paylab.py doctor
if errorlevel 1 exit /b %errorlevel%
echo Open http://127.0.0.1:8080
python scripts\paylab.py serve --port 8080
