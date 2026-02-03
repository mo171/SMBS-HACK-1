# 🐳 Docker Quick Start

This project includes Docker configuration to run both frontend and backend in a single container.

## 🚀 Quick Start (3 Steps)

### 1. Install Docker Desktop

Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)

### 2. Configure Environment Variables

```powershell
# Copy example file
cp .env.example .env

# Edit with your credentials
notepad .env
```

### 3. Run the Application

```powershell
# Option A: Use the quick start script (easiest)
.\docker-start.ps1

# Option B: Use docker-compose directly
docker-compose up --build -d
```

## 🌐 Access Your Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📚 Full Documentation

See [DOCKER_SETUP_GUIDE.md](./DOCKER_SETUP_GUIDE.md) for:

- Detailed setup instructions
- Troubleshooting guide
- Production deployment tips
- Development workflow

## 🛠️ Common Commands

```powershell
# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose build --no-cache

# Restart
docker-compose restart
```

## 📁 Docker Files

- `Dockerfile` - Multi-stage build configuration
- `docker-compose.yml` - Container orchestration
- `docker-entrypoint.sh` - Startup script
- `.dockerignore` - Files excluded from build
- `backend/requirements.txt` - Python dependencies

## ❓ Need Help?

Check the [troubleshooting section](./DOCKER_SETUP_GUIDE.md#troubleshooting) in the full guide.
