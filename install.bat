@echo off
chcp 65001 >nul
echo 🤖 TOKOPEDIA SCRAPER - INSTALLATION SCRIPT
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python tidak ditemukan. Silakan install Python 3.8+ terlebih dahulu.
    echo Download dari: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python ditemukan:
python --version

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip tidak ditemukan. Silakan install pip terlebih dahulu.
    pause
    exit /b 1
)

echo ✅ pip ditemukan:
pip --version

REM Create virtual environment
echo.
echo 🔧 Membuat virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 🔧 Upgrade pip...
python -m pip install --upgrade pip

REM Install requirements
echo 🔧 Install dependensi...
pip install -r requirements.txt

REM Test installation
echo.
echo 🧪 Testing instalasi...
python -c "import selenium, undetected_chromedriver, requests, pandas, bs4; print('✅ Semua dependensi berhasil diinstall!')"

if errorlevel 1 (
    echo.
    echo ❌ INSTALASI GAGAL!
    echo Silakan coba lagi atau hubungi developer.
    pause
    exit /b 1
) else (
    echo.
    echo 🎉 INSTALASI BERHASIL!
    echo ======================
    echo.
    echo 📋 Cara menjalankan scraper:
    echo    1. Aktifkan virtual environment: venv\Scripts\activate.bat
    echo    2. Jalankan scraper: python tokopedia_scraper_improved.py
    echo.
    echo 📚 Dokumentasi lengkap ada di file README.md
    echo.
    echo ⚠️  PERINGATAN:
    echo    • Gunakan scraper dengan bijak dan bertanggung jawab
    echo    • Patuhi Terms of Service Tokopedia
    echo    • Jangan melakukan scraping berlebihan
    echo.
    pause
)