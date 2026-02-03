# Docker Quick Start Script for Windows PowerShell
# Run this script to quickly build and start your Docker container

Write-Host "🐳 SMBS-HACK-1 Docker Quick Start" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "🔍 Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
Write-Host ""
Write-Host "🔍 Checking environment variables..." -ForegroundColor Yellow
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Please edit .env file with your actual credentials before continuing." -ForegroundColor Yellow
    Write-Host "Press any key to open .env file in notepad..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    notepad .env
    Write-Host ""
    Write-Host "After saving your credentials, press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} else {
    Write-Host "✅ .env file found" -ForegroundColor Green
}

# Fix line endings for entrypoint script
Write-Host ""
Write-Host "🔧 Fixing line endings in docker-entrypoint.sh..." -ForegroundColor Yellow
(Get-Content docker-entrypoint.sh -Raw) -replace "`r`n", "`n" | Set-Content docker-entrypoint.sh -NoNewline
Write-Host "✅ Line endings fixed" -ForegroundColor Green

# Ask user what to do
Write-Host ""
Write-Host "What would you like to do?" -ForegroundColor Cyan
Write-Host "1. Build and start containers (recommended for first time)" -ForegroundColor White
Write-Host "2. Start existing containers" -ForegroundColor White
Write-Host "3. Rebuild from scratch (no cache)" -ForegroundColor White
Write-Host "4. Stop containers" -ForegroundColor White
Write-Host "5. View logs" -ForegroundColor White
Write-Host "6. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🏗️  Building and starting containers..." -ForegroundColor Cyan
        docker-compose up --build -d
        Write-Host ""
        Write-Host "✅ Containers started!" -ForegroundColor Green
        Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "📡 Backend: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "To view logs, run: docker-compose logs -f" -ForegroundColor Yellow
    }
    "2" {
        Write-Host ""
        Write-Host "▶️  Starting containers..." -ForegroundColor Cyan
        docker-compose up -d
        Write-Host ""
        Write-Host "✅ Containers started!" -ForegroundColor Green
        Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "📡 Backend: http://localhost:8000" -ForegroundColor Cyan
    }
    "3" {
        Write-Host ""
        Write-Host "🔨 Rebuilding from scratch (this may take a while)..." -ForegroundColor Cyan
        docker-compose build --no-cache
        docker-compose up -d
        Write-Host ""
        Write-Host "✅ Rebuild complete and containers started!" -ForegroundColor Green
    }
    "4" {
        Write-Host ""
        Write-Host "🛑 Stopping containers..." -ForegroundColor Cyan
        docker-compose down
        Write-Host "✅ Containers stopped" -ForegroundColor Green
    }
    "5" {
        Write-Host ""
        Write-Host "📋 Viewing logs (press Ctrl+C to exit)..." -ForegroundColor Cyan
        docker-compose logs -f
    }
    "6" {
        Write-Host ""
        Write-Host "👋 Goodbye!" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host ""
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
