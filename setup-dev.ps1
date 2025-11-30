# Development Setup Script
# Sets up the development environment without Docker

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Weather Monitoring System - Dev Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Backend Setup
Write-Host "Setting up backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Copy .env if needed
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Backend .env created" -ForegroundColor Green
    Write-Host "⚠ Remember to update .env with your API keys!" -ForegroundColor Yellow
}

# Initialize database
Write-Host ""
Write-Host "Initializing database..." -ForegroundColor Yellow
python setup.py
Write-Host "✓ Database initialized" -ForegroundColor Green

Set-Location ..

# Frontend Setup
Write-Host ""
Write-Host "Setting up frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Copy .env if needed
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Frontend .env created" -ForegroundColor Green
}

Set-Location ..

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "✓ Development environment setup complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Make sure MongoDB and Redis are running:" -ForegroundColor White
Write-Host "   mongod --dbpath C:\data\db" -ForegroundColor Gray
Write-Host "   redis-server" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Update .env files with your configuration" -ForegroundColor White
Write-Host ""
Write-Host "3. Start the backend (3 terminals):" -ForegroundColor White
Write-Host "   Terminal 1: cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "   Terminal 2: cd backend; .\venv\Scripts\Activate.ps1; celery -A app.tasks.celery_app worker -l info" -ForegroundColor Gray
Write-Host "   Terminal 3: cd backend; .\venv\Scripts\Activate.ps1; celery -A app.tasks.celery_app beat -l info" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Start the frontend:" -ForegroundColor White
Write-Host "   cd frontend; npm run dev" -ForegroundColor Gray
Write-Host ""
