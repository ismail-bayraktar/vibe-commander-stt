@echo off
set SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\VD Speech-to-Text.lnk

if exist "%SHORTCUT%" (
    del "%SHORTCUT%"
    echo [OK] Baslangictan kaldirildi.
) else (
    echo Zaten baslangicta degil.
)
pause
