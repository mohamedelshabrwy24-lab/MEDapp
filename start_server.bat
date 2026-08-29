@echo off
title MedRef Secure Gateway Server
cd /d "%~dp0"
echo =======================================================
echo   Starting MedRef Secure Gateway Server (Phase 1)...
echo =======================================================
python server.py
pause
