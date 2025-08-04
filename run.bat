@echo off
echo Starting Backend and Frontend Applications...

REM Initialize conda for this session
call "%USERPROFILE%\miniconda3\Scripts\activate.bat"

REM Start backend server in new Anaconda prompt window
start "Backend Server" cmd /k "call %USERPROFILE%\miniconda3\Scripts\activate.bat && conda activate legal && cd backend && uvicorn main:app --reload"

REM Start frontend application in new Anaconda prompt window  
start "Frontend App" cmd /k "call %USERPROFILE%\miniconda3\Scripts\activate.bat && conda activate legal && streamlit run app.py"

echo Both applications are starting...
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:8501
<<<<<<< HEAD
pause
=======
<<<<<<< HEAD
pause
=======
pause