#!/bin/bash

echo "🤖 TOKOPEDIA SCRAPER - INSTALLATION SCRIPT"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 tidak ditemukan. Silakan install Python 3.8+ terlebih dahulu."
    exit 1
fi

echo "✅ Python 3 ditemukan: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 tidak ditemukan. Silakan install pip terlebih dahulu."
    exit 1
fi

echo "✅ pip3 ditemukan: $(pip3 --version)"

# Check if Chrome is installed
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "⚠️  Google Chrome tidak ditemukan."
    echo "   Silakan install Google Chrome terlebih dahulu:"
    echo "   Ubuntu/Debian: sudo apt install google-chrome-stable"
    echo "   CentOS/RHEL: sudo yum install google-chrome-stable"
    echo "   macOS: brew install --cask google-chrome"
    echo ""
    read -p "Lanjutkan instalasi? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Google Chrome ditemukan"
fi

# Create virtual environment
echo ""
echo "🔧 Membuat virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Mengaktifkan virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🔧 Upgrade pip..."
pip install --upgrade pip

# Install requirements
echo "🔧 Install dependensi..."
pip install -r requirements.txt

# Test installation
echo ""
echo "🧪 Testing instalasi..."
python3 -c "
try:
    import selenium
    import undetected_chromedriver
    import requests
    import pandas
    import bs4
    print('✅ Semua dependensi berhasil diinstall!')
except ImportError as e:
    print(f'❌ Error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 INSTALASI BERHASIL!"
    echo "======================"
    echo ""
    echo "📋 Cara menjalankan scraper:"
    echo "   1. Aktifkan virtual environment: source venv/bin/activate"
    echo "   2. Jalankan scraper: python tokopedia_scraper_improved.py"
    echo ""
    echo "📚 Dokumentasi lengkap ada di file README.md"
    echo ""
    echo "⚠️  PERINGATAN:"
    echo "   • Gunakan scraper dengan bijak dan bertanggung jawab"
    echo "   • Patuhi Terms of Service Tokopedia"
    echo "   • Jangan melakukan scraping berlebihan"
    echo ""
else
    echo ""
    echo "❌ INSTALASI GAGAL!"
    echo "Silakan coba lagi atau hubungi developer."
    exit 1
fi