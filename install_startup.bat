@echo off
echo ================================================
echo   VD Speech-to-Text - Windows Baslangic Ayari
echo ================================================
echo.

set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT=%STARTUP%\VD Speech-to-Text.lnk
set SCRIPT=%~dp0start_vd.pyw

:: PowerShell ile kisayol olustur
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = 'pythonw.exe'; $s.Arguments = '\"%SCRIPT%\"'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'VD Speech-to-Text'; $s.Save()"

if exist "%SHORTCUT%" (
    echo.
    echo [OK] Windows baslangicinina eklendi!
    echo Her acilista otomatik calisacak.
    echo.
    echo Kaldirmak icin: remove_startup.bat
) else (
    echo [HATA] Kisayol olusturulamadi.
)

echo.
pause
