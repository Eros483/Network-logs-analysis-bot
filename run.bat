@echo off
echo Starting Backend and Frontend Applications...

REM Start backend server with conda activation
start "Backend Server" cmd /k "call %USERPROFILE%\miniconda3\Scripts\activate.bat && conda activate legal && cd /d %~dp0 && python -m uvicorn backend.main:app --reload"

REM Wait before starting frontend
timeout /t 3 /nobreak >nul

REM Start frontend with conda activation
start "Frontend App" cmd /k "call %USERPROFILE%\miniconda3\Scripts\activate.bat && conda activate legal && cd /d %~dp0 && python -m streamlit run app.py"

echo Both applications are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:8501
pause