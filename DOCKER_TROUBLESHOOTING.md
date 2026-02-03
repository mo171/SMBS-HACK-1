# 🔧 Docker Troubleshooting Checklist

Use this checklist to diagnose and fix common Docker issues.

## ✅ Pre-Build Checklist

- [ ] Docker Desktop is installed and running
- [ ] Docker version is up to date (`docker --version`)
- [ ] `.env` file exists and contains all required variables
- [ ] `backend/app/.env` file exists with credentials
- [ ] `backend/requirements.txt` has all dependencies
- [ ] `docker-entrypoint.sh` has Unix line endings (LF, not CRLF)
- [ ] No other services using ports 3000 or 8000

## 🏗️ Build Issues

### ❌ Build fails with "no such file or directory"

**Check:**

```powershell
# Verify all files exist
ls Dockerfile
ls docker-compose.yml
ls docker-entrypoint.sh
ls backend/requirements.txt
```

**Fix:**

- Ensure you're in the project root directory
- Re-create missing files from the guide

### ❌ "ERROR [internal] load metadata for docker.io/library/node"

**Cause:** Docker can't pull base images (network issue)

**Fix:**

```powershell
# Check Docker is running
docker info

# Test internet connection
ping docker.io

# Restart Docker Desktop
# Right-click Docker Desktop icon → Restart
```

### ❌ "failed to solve with frontend dockerfile.v0"

**Cause:** Syntax error in Dockerfile

**Fix:**

```powershell
# Validate Dockerfile syntax
docker build --no-cache -t test .

# Check for Windows line endings
(Get-Content Dockerfile -Raw) -match "`r`n"
```

### ❌ Python package installation fails

**Error:** `ERROR: Could not find a version that satisfies the requirement...`

**Fix:**

```powershell
# Update requirements.txt with correct versions
# Check your current venv for exact versions:
cd backend
.\venv\Scripts\activate
pip freeze > requirements_actual.txt

# Compare and update requirements.txt
```

### ❌ Next.js build fails

**Error:** `Error: Cannot find module...`

**Fix:**

```powershell
# Ensure package.json is correct
cat frontend/my-app/package.json

# Try building locally first
cd frontend/my-app
npm install
npm run build
```

## 🚀 Runtime Issues

### ❌ Container exits immediately after starting

**Diagnose:**

```powershell
# Check container status
docker-compose ps

# View logs
docker-compose logs app

# Check exit code
docker inspect smbs-hack-1 --format='{{.State.ExitCode}}'
```

**Common causes:**

1. Missing environment variables
2. Entrypoint script has errors
3. Application crashes on startup

**Fix:**

```powershell
# Run container interactively to debug
docker run -it --rm --entrypoint sh smbs-hack-1:latest

# Inside container, manually run commands:
cd /app/backend/app
uvicorn app:app --host 0.0.0.0 --port 8000
```

### ❌ Port already in use

**Error:** `bind: address already in use`

**Diagnose:**

```powershell
# Find what's using the port
netstat -ano | findstr :3000
netstat -ano | findstr :8000
```

**Fix Option 1 - Kill the process:**

```powershell
# Replace <PID> with the actual process ID
taskkill /PID <PID> /F
```

**Fix Option 2 - Change ports:**

```yaml
# In docker-compose.yml
ports:
  - "3001:3000" # Use port 3001 on host
  - "8001:8000" # Use port 8001 on host
```

### ❌ Frontend can't connect to backend

**Symptoms:**

- Frontend loads but shows errors
- Network errors in browser console
- API calls fail

**Diagnose:**

```powershell
# Test backend directly
curl http://localhost:8000/docs

# Check if backend is running
docker-compose logs app | Select-String "uvicorn"
```

**Fix:**

```javascript
// In frontend code, ensure API URL is correct:
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// NOT the container name or internal IP
```

### ❌ CORS errors in browser

**Error:** `Access to fetch at 'http://localhost:8000' has been blocked by CORS policy`

**Fix:**

```python
# In backend/app/app.py, verify CORS settings:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Add your production domain here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### ❌ Environment variables not loaded

**Symptoms:**

- Backend can't connect to Supabase
- OpenAI API errors
- Missing configuration

**Diagnose:**

```powershell
# Check environment variables in container
docker exec smbs-hack-1 env | Select-String "OPENAI"
docker exec smbs-hack-1 env | Select-String "SUPABASE"
```

**Fix:**

```powershell
# Ensure .env file exists
ls .env

# Verify docker-compose.yml has env_file:
cat docker-compose.yml | Select-String "env_file"

# Restart with fresh environment
docker-compose down
docker-compose up -d
```

### ❌ Permission denied on entrypoint script

**Error:** `exec ./docker-entrypoint.sh: permission denied`

**Fix:**

```powershell
# In Git Bash or WSL:
chmod +x docker-entrypoint.sh

# Or rebuild with no cache:
docker-compose build --no-cache
```

### ❌ Line ending issues (Windows)

**Symptoms:**

- Entrypoint script fails with weird errors
- `/bin/bash^M: bad interpreter`

**Fix:**

```powershell
# Convert CRLF to LF
(Get-Content docker-entrypoint.sh -Raw) -replace "`r`n", "`n" | Set-Content docker-entrypoint.sh -NoNewline

# Rebuild
docker-compose build --no-cache
```

## 🔍 Debugging Commands

### View detailed logs

```powershell
# All logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Backend only
docker-compose logs app | Select-String "uvicorn"

# Frontend only
docker-compose logs app | Select-String "next"
```

### Inspect container

```powershell
# Enter running container
docker exec -it smbs-hack-1 sh

# Check running processes
docker exec smbs-hack-1 ps aux

# Check disk space
docker exec smbs-hack-1 df -h

# View file contents
docker exec smbs-hack-1 cat /app/backend/app/.env
```

### Check resource usage

```powershell
# Container stats
docker stats smbs-hack-1

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

### Network debugging

```powershell
# List networks
docker network ls

# Inspect network
docker network inspect smbs-hack-1_app-network

# Test connectivity
docker exec smbs-hack-1 ping google.com
```

## 🧹 Clean Slate (Nuclear Option)

If nothing works, start fresh:

```powershell
# Stop and remove everything
docker-compose down -v --rmi all

# Remove all Docker data (WARNING: affects all projects)
docker system prune -a --volumes

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Health Check

Run these commands to verify everything is working:

```powershell
# 1. Check Docker is running
docker info

# 2. Check container is running
docker-compose ps

# 3. Check logs for errors
docker-compose logs --tail=50

# 4. Test backend
curl http://localhost:8000/docs

# 5. Test frontend
# Open browser to http://localhost:3000

# 6. Check resource usage
docker stats smbs-hack-1 --no-stream
```

## 🆘 Still Having Issues?

### Collect diagnostic information:

```powershell
# Create diagnostic report
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = "docker_diagnostic_$timestamp.txt"

@"
=== Docker Diagnostic Report ===
Generated: $(Get-Date)

--- Docker Version ---
$(docker --version)
$(docker-compose --version)

--- Container Status ---
$(docker-compose ps)

--- Recent Logs ---
$(docker-compose logs --tail=100)

--- Environment Check ---
.env exists: $(Test-Path .env)
backend/.env exists: $(Test-Path backend/app/.env)

--- Port Check ---
$(netstat -ano | findstr :3000)
$(netstat -ano | findstr :8000)

--- Disk Space ---
$(docker system df)

"@ | Out-File $reportFile

Write-Host "Diagnostic report saved to: $reportFile"
```

### Get help:

1. Review the full [DOCKER_SETUP_GUIDE.md](./DOCKER_SETUP_GUIDE.md)
2. Check [Docker documentation](https://docs.docker.com/)
3. Search for error messages on Stack Overflow
4. Share the diagnostic report with your team

## ✅ Success Indicators

Your setup is working correctly when:

- [ ] `docker-compose ps` shows container as "Up"
- [ ] No errors in `docker-compose logs`
- [ ] http://localhost:3000 loads the frontend
- [ ] http://localhost:8000/docs shows API documentation
- [ ] Frontend can make API calls to backend
- [ ] No CORS errors in browser console
- [ ] Backend can connect to Supabase
- [ ] OpenAI API calls work (if configured)

---

**Remember:** Most issues are caused by:

1. Missing or incorrect environment variables
2. Port conflicts
3. Line ending issues (Windows)
4. Missing dependencies
5. Docker not running

Check these first! 🎯
