@echo off
chcp 65001 >nul 2>&1
title VD Speech-to-Text Kurulum
color 0A

echo.
echo  ╔══════════════════════════════════════╗
echo  ║   VD Speech-to-Text  -  Kurulum      ║
echo  ╚══════════════════════════════════════╝
echo.

:: ---- Python kontrol ----
echo [1/4] Python kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [!] Python bulunamadi.
    echo.
    echo  Otomatik yuklensin mi? (winget gerekli^)
    echo.
    choice /c EH /m "  [E] Evet  [H] Hayir, kendim kuracagim"
    if errorlevel 2 (
        echo.
        echo  python.org/downloads adresinden Python 3.10+ indirin.
        echo  Kurulumda "Add to PATH" tiklayin!
        echo.
        pause
        exit /b 1
    )
    echo.
    echo  Python yukleniyor (bu 1-2 dakika surebilir^)...
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo.
        echo  [HATA] Otomatik kurulum basarisiz.
        echo  python.org/downloads adresinden manuel kurun.
        pause
        exit /b 1
    )
    echo.
    echo  [OK] Python kuruldu. Lutfen bu scripti TEKRAR calistirin.
    pause
    exit /b 0
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo        Python %PYVER% bulundu.

:: ---- Paketler ----
echo.
echo [2/4] Paketler yukleniyor (ilk seferde biraz surer)...
echo.
pip install -r "%~dp0requirements.txt" --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo.
    echo  [HATA] Paket kurulumu basarisiz. Interneti kontrol edin.
    pause
    exit /b 1
)
echo        Tum paketler yuklendi.

:: ---- Masaustu kisayolu ----
echo.
echo [3/4] Masaustu kisayolu olusturuluyor...

set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT=%DESKTOP%\VD Speech-to-Text.lnk
set SCRIPT=%~dp0start_vd.pyw

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = 'pythonw.exe'; $s.Arguments = '\"%SCRIPT%\"'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'VD Speech-to-Text'; $s.Save()" >nul 2>&1

if exist "%SHORTCUT%" (
    echo        Masaustune kisayol eklendi.
) else (
    echo        Kisayol olusturulamadi (sorun degil, elle calistirabilirsiniz^).
)

:: ---- Bitis ----
echo.
echo [4/4] Kurulum tamamlandi!
echo.
echo  ╔══════════════════════════════════════╗
echo  ║                                      ║
echo  ║   Masaustundeki kisayoldan baslat    ║
echo  ║   veya: python speech_to_text.py     ║
echo  ║                                      ║
echo  ║   Ilk acilista model indirilir       ║
echo  ║   (~250 MB, bir kere)                ║
echo  ║                                      ║
echo  ║   Sag tik menu:                      ║
echo  ║     - Dil degistir (TR/EN)           ║
echo  ║     - Mikrofon sec                   ║
echo  ║     - Kisayol ayarla                 ║
echo  ║     - Windows ile baslat             ║
echo  ║                                      ║
echo  ╚══════════════════════════════════════╝
echo.
choice /c EH /m "  Simdi baslat? [E] Evet  [H] Hayir"
if errorlevel 2 (
    exit /b 0
)
echo.
echo  Baslatiliyor...
start "" pythonw.exe "%SCRIPT%"
