@echo off
title SysCalculus - Automated GitHub & Cloud Deployment
color 0A

echo ===============================================================================
echo            SYSCALCULUS - 1-CLICK AUTOMATED GITHUB & CLOUD PUBLISHER
echo ===============================================================================
echo.
echo [1/2] Hedef Depo Baglaniyor: https://github.com/dekaronarkedo/syscalculus.git
git remote remove origin >nul 2>&1
git remote add origin https://github.com/dekaronarkedo/syscalculus.git
git branch -M main

echo.
echo [2/2] Kodlar ve 24/7 Otonom Is Akislari GitHub'a gonderiliyor...
echo (Eger tarayici veya onay penceresi acilirsa 'Authorize' veya 'Sign in' butonuna 1 kez tikla)
echo.
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ===============================================================================
    echo [BASARILI] TEBRIKLER BABA! Kodlar ve 24/7 Otonom Sistem GitHub'a Yuklendi!
    echo ===============================================================================
    echo.
    echo Simdi Cloudflare Pages panelini aciyorum...
    echo Tek yapacagin sey: 'Create application' -^> 'Pages' -^> 'Connect to Git' deyip
    echo 'syscalculus' reposunu secmek.
    echo.
    timeout /t 3 >nul
    start https://dash.cloudflare.com/?to=/:account/pages
) else (
    echo.
    echo [HATA] Gonderme basarisiz oldu. Lutfen internet baglantini ve onayi kontrol et.
)

pause
