@echo off
setlocal EnableExtensions DisableDelayedExpansion

rem Run from the directory containing this script.
rem pushd also supports a UNC directory.
pushd "%~dp0"
if errorlevel 1 exit /b 1

set "VDIR=%USERPROFILE%\dnd"
set "VENV_PYTHON=%VDIR%\Scripts\python.exe"

if not exist "%VENV_PYTHON%" goto create_venv
if not exist "%VDIR%\Scripts\activate.bat" goto create_venv
goto install_dependencies

:create_venv
rem Prefer the Python launcher.
py -3.14 -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 14) else 1)" >nul 2>&1
if not errorlevel 1 goto create_with_py

rem Fall back to Python 3.14 on PATH.
python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 14) else 1)" >nul 2>&1
if not errorlevel 1 goto create_with_python

>&2 echo ERROR: Python 3.14 was not found.
>&2 echo Make it available through py -3.14 or python on PATH.
set "EXIT_CODE=1"
goto finish

:create_with_py
py -3.14 -m venv "%VDIR%"
if errorlevel 1 goto failed
goto install_dependencies

:create_with_python
python -m venv "%VDIR%"
if errorlevel 1 goto failed

:install_dependencies
"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto failed

"%VENV_PYTHON%" -m pip install ^
    "fastapi>=0.115" ^
    "uvicorn[standard]>=0.30" ^
    "PyYAML>=6.0" ^
    python-multipart
if errorlevel 1 goto failed

"%VENV_PYTHON%" scrying_glass_server.py --config config.yaml
set "EXIT_CODE=%ERRORLEVEL%"
goto finish

:failed
set "EXIT_CODE=%ERRORLEVEL%"
>&2 echo ERROR: Launcher command failed with exit code %EXIT_CODE%.

:finish
popd
endlocal & exit /b %EXIT_CODE%