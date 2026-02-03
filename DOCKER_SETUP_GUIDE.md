# 🐳 Docker Setup Guide - Frontend + Backend in One Container

This guide provides a comprehensive, step-by-step walkthrough for Dockerizing your SMBS-HACK-1 application with both frontend (Next.js) and backend (FastAPI) running in a single Docker container.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Understanding the Docker Setup](#understanding-the-docker-setup)
4. [Step-by-Step Setup](#step-by-step-setup)
5. [Building and Running](#building-and-running)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)

---

## 🔧 Prerequisites

Before starting, ensure you have the following installed:

- **Docker Desktop** (Windows): [Download here](https://www.docker.com/products/docker-desktop/)
- **Docker Compose** (included with Docker Desktop)
- **Git** (for version control)

Verify installations:

```powershell
docker --version
docker-compose --version
```

---

## 📁 Project Structure

After setup, your project will have these Docker-related files:

```
SMBS-HACK-1/
├── backend/
│   ├── app/
│   │   ├── app.py
│   │   ├── .env                    # Your actual environment variables
│   │   └── ...
│   └── requirements.txt            # ✨ NEW - Python dependencies
├── frontend/
│   └── my-app/
│       ├── package.json
│       └── ...
├── Dockerfile                      # ✨ NEW - Multi-stage build configuration
├── docker-compose.yml              # ✨ NEW - Container orchestration
├── docker-entrypoint.sh            # ✨ NEW - Startup script
├── .dockerignore                   # ✨ NEW - Files to exclude from build
└── .env.example                    # ✨ NEW - Environment variables template
```

---

## 🎯 Understanding the Docker Setup

### **1. Multi-Stage Dockerfile**

The `Dockerfile` uses a **multi-stage build** approach:

- **Stage 1 (frontend-builder)**: Builds the Next.js frontend
- **Stage 2 (backend-builder)**: Installs Python dependencies
- **Stage 3 (final)**: Combines both into a single production image

**Benefits:**

- ✅ Smaller final image size
- ✅ Faster builds with layer caching
- ✅ Separation of build and runtime dependencies

### **2. Docker Compose**

`docker-compose.yml` simplifies container management:

- Defines services, ports, and environment variables
- Enables easy start/stop with single commands
- Manages networking between services

### **3. Entrypoint Script**

`docker-entrypoint.sh` starts both services:

- Runs FastAPI backend on port 8000
- Runs Next.js frontend on port 3000
- Handles graceful shutdown

---

## 🚀 Step-by-Step Setup

### **Step 1: Verify Files Created**

Ensure all Docker files were created in your project root:

```powershell
# Navigate to project directory
cd c:\movin\programing\3_projects\SMBS-HACK-1

# List Docker files
ls Dockerfile, docker-compose.yml, docker-entrypoint.sh, .dockerignore
```

### **Step 2: Configure Environment Variables**

1. **Copy the example file:**

   ```powershell
   cp .env.example .env
   ```

2. **Edit `.env` with your actual credentials:**

   ```powershell
   notepad .env
   ```

3. **Fill in your values:**

   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
   SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxx
   TWILIO_PHONE_NUMBER=+1234567890
   ```

4. **Also update `backend/app/.env`** with the same values (this is your existing file)

### **Step 3: Update Backend Requirements (If Needed)**

The `backend/requirements.txt` file has been created with common dependencies. You may need to adjust versions:

```powershell
# Check what's currently installed in your venv
cd backend
.\venv\Scripts\activate
pip freeze > requirements_current.txt
```

Compare `requirements_current.txt` with `requirements.txt` and update if needed.

### **Step 4: Update Frontend Configuration**

Ensure your Next.js app knows where the backend is:

1. **Create/update `frontend/my-app/.env.local`:**

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

2. **Verify API calls in your frontend code use this variable:**
   ```javascript
   const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
   ```

### **Step 5: Fix Line Endings (Windows Specific)**

The entrypoint script needs Unix-style line endings:

```powershell
# Install dos2unix if not available (using Git Bash or WSL)
# Or use this PowerShell command:
(Get-Content docker-entrypoint.sh -Raw) -replace "`r`n", "`n" | Set-Content docker-entrypoint.sh -NoNewline
```

---

## 🏗️ Building and Running

### **Method 1: Using Docker Compose (Recommended)**

#### **Build the Image:**

```powershell
docker-compose build
```

This will:

- Download base images (Node.js, Python)
- Install all dependencies
- Build the Next.js app
- Create the final container image

**Expected output:**

```
[+] Building 245.3s (24/24) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 1.23kB
 => [frontend-builder 1/6] FROM docker.io/library/node:20-alpine
 ...
 => => naming to docker.io/library/smbs-hack-1_app
```

#### **Start the Container:**

```powershell
docker-compose up
```

Or run in detached mode (background):

```powershell
docker-compose up -d
```

#### **View Logs:**

```powershell
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f app | Select-String "uvicorn"

# Frontend only
docker-compose logs -f app | Select-String "next"
```

#### **Stop the Container:**

```powershell
docker-compose down
```

### **Method 2: Using Docker Commands Directly**

#### **Build:**

```powershell
docker build -t smbs-hack-1:latest .
```

#### **Run:**

```powershell
docker run -d `
  --name smbs-hack-1 `
  -p 3000:3000 `
  -p 8000:8000 `
  --env-file .env `
  -v ${PWD}/backend/app/.env:/app/backend/app/.env:ro `
  smbs-hack-1:latest
```

#### **Stop:**

```powershell
docker stop smbs-hack-1
docker rm smbs-hack-1
```

---

## 🌐 Accessing Your Application

Once the container is running:

- **Frontend (Next.js)**: http://localhost:3000
- **Backend API (FastAPI)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### **Test the Backend:**

```powershell
# Using PowerShell
Invoke-WebRequest -Uri http://localhost:8000/docs

# Or using curl (if installed)
curl http://localhost:8000/docs
```

### **Test the Frontend:**

Open your browser and navigate to http://localhost:3000

---

## 🔍 Troubleshooting

### **Issue 1: Port Already in Use**

**Error:**

```
Error starting userland proxy: listen tcp4 0.0.0.0:3000: bind: address already in use
```

**Solution:**

```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change the port in docker-compose.yml:
# ports:
#   - "3001:3000"  # Map host port 3001 to container port 3000
```

### **Issue 2: Build Fails - Missing Dependencies**

**Error:**

```
ERROR: Could not find a version that satisfies the requirement <package>
```

**Solution:**

```powershell
# Update requirements.txt with correct versions
# Then rebuild:
docker-compose build --no-cache
```

### **Issue 3: Frontend Can't Connect to Backend**

**Symptoms:**

- Frontend loads but API calls fail
- CORS errors in browser console

**Solution:**

1. **Check CORS settings in `backend/app/app.py`:**

   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Verify frontend API URL:**
   ```javascript
   // Should use localhost, not container name
   const API_URL = "http://localhost:8000";
   ```

### **Issue 4: Container Exits Immediately**

**Check logs:**

```powershell
docker-compose logs app
```

**Common causes:**

- Missing environment variables
- Syntax errors in entrypoint script
- Application crashes on startup

### **Issue 5: Changes Not Reflected**

**Solution:**

```powershell
# Rebuild without cache
docker-compose build --no-cache

# Restart containers
docker-compose down
docker-compose up -d
```

### **Issue 6: Permission Denied on Entrypoint Script**

**Error:**

```
exec ./docker-entrypoint.sh: permission denied
```

**Solution:**

```powershell
# Make script executable (in WSL or Git Bash)
chmod +x docker-entrypoint.sh

# Or rebuild with --no-cache
docker-compose build --no-cache
```

---

## 🎨 Development Workflow

### **Development Mode with Hot Reload**

For development, you might want to mount your source code:

**Create `docker-compose.dev.yml`:**

```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
      - "8000:8000"
    environment:
      - NODE_ENV=development
    volumes:
      # Mount source code for hot reload
      - ./backend/app:/app/backend/app
      - ./frontend/my-app:/app/frontend
      - /app/frontend/node_modules # Prevent overwriting node_modules
      - /app/frontend/.next # Prevent overwriting .next
    command: >
      sh -c "
        cd /app/backend/app &&
        uvicorn app:app --host 0.0.0.0 --port 8000 --reload &
        cd /app/frontend &&
        npm run dev
      "
```

**Run development mode:**

```powershell
docker-compose -f docker-compose.dev.yml up
```

### **Inspecting the Container**

```powershell
# Enter the running container
docker exec -it smbs-hack-1 sh

# Check running processes
docker exec smbs-hack-1 ps aux

# View environment variables
docker exec smbs-hack-1 env
```

---

## 🚢 Production Deployment

### **Optimizations for Production**

1. **Use specific version tags:**

   ```dockerfile
   FROM node:20.11.0-alpine AS frontend-builder
   FROM python:3.11.7-slim AS backend-builder
   ```

2. **Add health checks:**

   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
     CMD curl -f http://localhost:8000/docs || exit 1
   ```

3. **Use multi-container setup** (recommended for production):
   - Separate frontend and backend containers
   - Use nginx as reverse proxy
   - Add Redis for caching
   - Use managed database instead of local

### **Example Production docker-compose.yml:**

```yaml
version: "3.8"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    environment:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
    restart: always
```

### **Deployment Platforms**

- **AWS ECS/Fargate**: Container orchestration
- **Google Cloud Run**: Serverless containers
- **DigitalOcean App Platform**: Simple deployment
- **Railway/Render**: Easy deployment with free tier

---

## 📊 Monitoring and Logs

### **View Real-time Logs:**

```powershell
docker-compose logs -f --tail=100
```

### **Export Logs:**

```powershell
docker-compose logs > logs.txt
```

### **Check Resource Usage:**

```powershell
docker stats smbs-hack-1
```

---

## 🔐 Security Best Practices

1. **Never commit `.env` files:**

   ```powershell
   # Ensure .env is in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use Docker secrets** for sensitive data in production

3. **Run as non-root user:**

   ```dockerfile
   RUN addgroup -g 1001 -S appuser && \
       adduser -S appuser -u 1001
   USER appuser
   ```

4. **Scan for vulnerabilities:**
   ```powershell
   docker scan smbs-hack-1:latest
   ```

---

## 🎓 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Docker Deployment](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)

---

## ✅ Quick Reference Commands

```powershell
# Build and start
docker-compose up --build -d

# Stop and remove
docker-compose down

# View logs
docker-compose logs -f

# Rebuild from scratch
docker-compose build --no-cache

# Restart services
docker-compose restart

# Remove all containers and images
docker-compose down --rmi all --volumes

# Check status
docker-compose ps

# Execute command in container
docker-compose exec app sh
```

---

## 🎉 Success Checklist

- [ ] Docker Desktop installed and running
- [ ] All Docker files created in project root
- [ ] Environment variables configured in `.env`
- [ ] Backend `requirements.txt` has correct dependencies
- [ ] Frontend configured to use correct API URL
- [ ] `docker-entrypoint.sh` has Unix line endings
- [ ] Container builds successfully
- [ ] Both frontend (port 3000) and backend (port 8000) accessible
- [ ] API calls from frontend to backend working
- [ ] No CORS errors in browser console

---

**Need Help?** Check the troubleshooting section or review the Docker logs for specific error messages.
