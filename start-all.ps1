# Weather Monitoring System - Complete Startup Script
Write-Host "========================================================================================" -ForegroundColor Cyan
Write-Host "                    Weather Monitoring System - Startup                                 " -ForegroundColor Cyan
Write-Host "========================================================================================" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
$dockerRunning = $false
try {
    $dockerOutput = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerRunning = $true
        Write-Host "[OK] Docker is running" -ForegroundColor Green
    }
} catch {
    Write-Host "[SKIP] Docker is not available" -ForegroundColor Yellow
}

# Start Redis
if ($dockerRunning) {
    Write-Host "`nStarting Redis..." -ForegroundColor Yellow
    $redisStatus = docker start redis-weather 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Creating new Redis container..." -ForegroundColor Yellow
        docker run -d --name redis-weather -p 6379:6379 redis | Out-Null
    }
    Write-Host "[OK] Redis is running on port 6379" -ForegroundColor Green
    
    # Wait for Redis to be ready
    Write-Host "Waiting for Redis to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    
    # Start all services with Celery
    Write-Host "`n========================================================================================" -ForegroundColor Cyan
    Write-Host "Starting: API + Celery Worker + Celery Beat + Frontend" -ForegroundColor Cyan
    Write-Host "Weather data will auto-update every 10 minutes" -ForegroundColor Green
    Write-Host "========================================================================================`n" -ForegroundColor Cyan
    npm run start:full
} else {
    Write-Host "`n========================================================================================" -ForegroundColor Yellow
    Write-Host "[WARNING] Docker Desktop is not running!" -ForegroundColor Yellow
    Write-Host "========================================================================================" -ForegroundColor Yellow
    Write-Host "Starting in LIMITED mode (API + Frontend only)" -ForegroundColor Yellow
    Write-Host "Weather data will NOT auto-update." -ForegroundColor Yellow
    Write-Host "`nTo enable automatic weather updates:" -ForegroundColor Cyan
    Write-Host "  1. Start Docker Desktop" -ForegroundColor White
    Write-Host "  2. Stop this process (Ctrl+C)" -ForegroundColor White
    Write-Host "  3. Run 'npm start' again" -ForegroundColor White
    Write-Host "========================================================================================`n" -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    npm run start:dev
}
