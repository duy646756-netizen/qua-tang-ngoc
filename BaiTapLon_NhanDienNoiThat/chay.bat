@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Nhan dien do noi that

where py >/dev/null 2>/dev/null && (set PY=py) || (set PY=python)

%PY% -c "import ultralytics" >/dev/null 2>nul
if errorlevel 1 (
  echo.
  echo   Lan dau chay: dang cai thu vien, viec nay mat vai phut...
  echo.
  %PY% -m pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo   Cai that bai. Hay kiem tra ket noi mang roi chay lai.
    pause
    exit /b 1
  )
)

echo   Dang mo phan mem...
%PY% app.py
if errorlevel 1 pause
