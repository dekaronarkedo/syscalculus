@echo off
title SysCalculus - Automated GitHub & Cloud Deployment
color 0A

echo ===============================================================================
echo            RUNTIMEZERO - 1-CLICK AUTOMATED GITHUB & CLOUD PUBLISHER
echo ===============================================================================
echo.
echo [1/3] Git repository is initialized and all 37 platform files are committed.
echo.
echo Lutfen GitHub'da actigin bos repository'nin HTTPS linkini buraya yapistir:
echo (Ornek: https://github.com/KULLANICI_ADIN/syscalculus.git)
echo.
set /p REPO_URL="GitHub Repo URL: "

if "%REPO_URL%"=="" (
    echo [HATA] Link girmedin baba! Lutfen gecerli bir GitHub linki gir.
    pause
    exit /b 1
)

echo.
echo [2/3] GitHub uzak sunucusu (origin) baglaniyor...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
git branch -M main

echo.
echo [3/3] Kodlar ve 24/7 Otonom Is Akislari GitHub'a gonderiliyor...
echo (Eger tarayici acilirsa 'Authorize Git Credential Manager' butonuna 1 kez tikla)
echo.
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ===============================================================================
    echo [BASARILI] TEBRIKLER BABA! Kodlar ve 24/7 Otonom Sistem GitHub'a Yuklendi!
    echo ===============================================================================
    echo.
    echo Simdi Cloudflare Pages panelini aciyorum...
    echo Tek yapacagin sey: 'Create application' -> 'Pages' -> 'Connect to Git' deyip
    echo bu repoyu secmek.
    echo.
    timeout /t 3 >nul
    start https://dash.cloudflare.com/?to=/:account/pages
) else (
    echo.
    echo [UYARI] Push sirasinda bir sorun olustu. Lutfen linki ve yetkini kontrol et.
)

echo.
pause
