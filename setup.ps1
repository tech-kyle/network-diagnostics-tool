# Network Diagnostics Tool - Quick Setup Script
# For Windows PowerShell

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Network Diagnostics Tool - Quick Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python 3 is installed
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonCmd) {
    Write-Host "❌ Error: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.7 or higher from https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    exit 1
}

$pythonVersion = (python --version 2>&1).ToString()
Write-Host "✅ Found $pythonVersion" -ForegroundColor Green

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Virtual environment created" -ForegroundColor Green

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host ""
    Write-Host "Creating .env configuration file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ .env file created from .env.example" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  NOTE: Please review and customize .env file for your environment" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Create necessary directories
Write-Host ""
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path logs | Out-Null
New-Item -ItemType Directory -Force -Path bulk_results | Out-Null
Write-Host "✅ Directories created" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor White
Write-Host ""
Write-Host "  1. Activate the virtual environment (if not already active):" -ForegroundColor White
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Run the application:" -ForegroundColor White
Write-Host "     python app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Open your browser to:" -ForegroundColor White
Write-Host "     http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "To customize settings, edit the .env file" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see README.md" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
