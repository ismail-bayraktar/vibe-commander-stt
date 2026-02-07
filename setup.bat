@echo off
title VD Speech-to-Text Setup
color 0A

echo.
echo  ====================================================
echo.
echo   ##   ## #####
echo   ##   ## ##  ##
echo    ## ##  ##  ##
echo    ## ##  ##  ##
echo     ###   #####
echo.
echo   V I B E   C O M M A N D E R
echo   Speech-to-Text Setup
echo  ====================================================
echo.

:: ---- Python kontrol ----
echo  [1/4] Python kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [!] Python bulunamadi.
    echo.
    echo  Otomatik yuklensin mi?
    echo  [E] Evet   [H] Hayir, kendim kuracagim
    echo.
    choice /c EH /n /m "  Secim: "
    if errorlevel 2 (
        echo.
        echo  python.org/downloads adresinden Python 3.10+ indirin.
        echo  Kurulumda "Add to PATH" secenegini tiklayin!
        echo.
        pause
        exit /b 1
    )
    echo.
    echo  Python yukleniyor...
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo.
        echo  [HATA] Otomatik kurulum basarisiz.
        echo  python.org/downloads adresinden manuel kurun.
        pause
        exit /b 1
    )
    echo.
    echo  [OK] Python kuruldu. Bu scripti TEKRAR calistirin.
    pause
    exit /b 0
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo         Python %PYVER% bulundu.

:: ---- Paketler ----
echo.
echo  [2/4] Paketler yukleniyor...
echo.
pip install -r "%~dp0requirements.txt" --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo.
    echo  [HATA] Paket kurulumu basarisiz. Interneti kontrol edin.
    pause
    exit /b 1
)
echo         Tum paketler yuklendi.

:: ---- Masaustu kisayolu ----
echo.
echo  [3/4] Masaustu kisayolu olusturuluyor...

set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\VD Speech-to-Text.lnk"
set "SCRIPT=%~dp0start_vd.pyw"

powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = 'pythonw.exe'; $s.Arguments = '\"%SCRIPT%\"'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'VD Speech-to-Text'; $s.Save()" >nul 2>&1

if exist "%SHORTCUT%" (
    echo         Masaustune kisayol eklendi.
) else (
    echo         Kisayol olusturulamadi ama sorun degil.
)

:: ---- Bitis ----
echo.
echo  [4/4] Kurulum tamamlandi!
echo.
echo  ====================================================
echo.
echo   Nasil kullanilir:
echo.
echo     1. Masaustundeki kisayola tikla
echo        (veya: python speech_to_text.py)
echo.
echo     2. Ilk acilista model indirilir (~250 MB)
echo.
echo     3. Mouse yan tusuna bas = kayit baslar
echo        Tekrar bas = metin yapistir
echo.
echo     4. Sag tik = ayarlar menusu
echo.
echo  ====================================================
echo.
echo  [E] Simdi baslat   [H] Kapat
echo.
choice /c EH /n /m "  Secim: "
if errorlevel 2 (
    exit /b 0
)
echo.
echo  Baslatiliyor...
start "" pythonw.exe "%SCRIPT%"
