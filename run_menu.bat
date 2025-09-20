@echo off
cd /d %~dp0

REM Khởi tạo
set PYTHON_PATH=
set PYTHONW_PATH=

REM Đọc từ config.txt (nếu có)
if exist "config.txt" (
    for /f "tokens=1,2 delims==" %%a in ('findstr /C:"PYTHON_PATH=" config.txt') do (
        set "CONFIG_PYTHON=%%b"
    )
)

REM Nếu có path từ config thì kiểm tra
if defined CONFIG_PYTHON (
    if exist "%CONFIG_PYTHON%" (
        set "PYTHON_PATH=%CONFIG_PYTHON%"
        for %%i in ("%CONFIG_PYTHON%") do (
            set "PYTHONW_PATH=%%~dpniw.exe"
        )
        if not defined PYTHONW_PATH (
            echo Canh bao: pythonw.exe khong tim thay, su dung python.exe thay the
            set "PYTHONW_PATH=%PYTHON_PATH%"
        )
    ) else (
        echo Canh bao: Khong tim thay Python theo config: %CONFIG_PYTHON%
        echo Su dung Python he thong...
        goto :check_system_python
    )
) else (
    goto :check_system_python
)
goto :run_all

:check_system_python
REM Kiểm tra Python hệ thống
for /f "delims=" %%i in ('where python 2^>nul') do (
    if exist "%%i" (
        set "PYTHON_PATH=%%i"
        goto :found_python
    )
)

:found_python
REM Tìm pythonw.exe cùng thư mục
for %%i in ("%PYTHON_PATH%") do (
    set "PYTHONW_PATH=%%~dpi%%~niw.exe"
)

if not defined PYTHON_PATH (
    echo ========================================
    echo   LOI: Python khong duoc tim thay!
    echo ========================================
    exit /b 1
)

if not defined PYTHONW_PATH (
    echo Canh bao: pythonw.exe khong tim thay, su dung python.exe thay the
    set "PYTHONW_PATH=%PYTHON_PATH%"
)

:run_all

REM Run monitor với pythonw
for %%i in ("%~dp0\.") do set "BATCH_FOLDER=%%~nxi"
start "%BATCH_FOLDER%" /min "%PYTHONW_PATH%" cleaup.py

REM Run main script
"%PYTHON_PATH%" index.py %*
echo ========================================
echo   Dong sau 5 giay...
echo ========================================
timeout /t 5 >nul
exit /b
