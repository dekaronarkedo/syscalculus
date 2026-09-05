@echo off
title SysCalculus - 1-Click Live Global Cloudflare Tunnel
color 0A
echo ===============================================================================
echo            SYSCALCULUS - GLOBAL CLOUDFLARE CANLI YAYIN MOTORU ($0)
echo ===============================================================================
echo.
echo [1/2] SysCalculus Sunucusu ve Otonom Ajanlar Kontrol Ediliyor...
netstat -ano | findstr :3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Yerel sunucu baslatiliyor...
    start /b python main.py
    timeout /t 3 >nul
) else (
    echo [OK] Yerel sunucu zaten aktif.
)

echo.
echo [2/2] Cloudflare Global Anycast Edge Baglantisi Kuruluyor...
echo.
echo *******************************************************************************
echo  TEBRIKLER! Siten Tum Dunyada Canli Yayina Aliniyor...
echo  Ekranda belirecek 'https://....trycloudflare.com' linkine tiklayarak
echo  dunyanin herhangi bir yerinden veya cep telefonundan hemen girebilirsin!
echo *******************************************************************************
echo.
.\cloudflared.exe tunnel --url http://localhost:3000
pause
