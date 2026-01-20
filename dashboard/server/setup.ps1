# Quick Setup Script for Windows

Write-Host "🚀 Animal Detection Backend - Quick Setup" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check Python
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Setup environment file
Write-Host ""
Write-Host "⚙️  Setting up environment..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists" -ForegroundColor Yellow
} else {
    Copy-Item .env.example .env
    Write-Host "✅ .env file created - Please edit with your configuration" -ForegroundColor Green
}

# Create logs directory
Write-Host ""
Write-Host "📁 Creating logs directory..." -ForegroundColor Yellow
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "✅ Logs directory created" -ForegroundColor Green
} else {
    Write-Host "⚠️  Logs directory already exists" -ForegroundColor Yellow
}

# Create media directory
Write-Host ""
Write-Host "📁 Creating media directory..." -ForegroundColor Yellow
if (!(Test-Path "media")) {
    New-Item -ItemType Directory -Path "media" | Out-Null
    Write-Host "✅ Media directory created" -ForegroundColor Green
} else {
    Write-Host "⚠️  Media directory already exists" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your MySQL and other credentials" -ForegroundColor White
Write-Host "2. Create MySQL database: CREATE DATABASE animal_detection_db;" -ForegroundColor White
Write-Host "3. Run migrations: python manage.py migrate" -ForegroundColor White
Write-Host "4. Create superuser: python manage.py createsuperuser" -ForegroundColor White
Write-Host "5. Start server: python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "For full documentation, see README.md" -ForegroundColor Yellow
