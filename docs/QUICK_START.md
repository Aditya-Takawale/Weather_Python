# 🚀 Quick Fix - Two Options

## ⚠️ Current Issue
You have **Python 3.13.7** which is too new for some packages (pydantic-core fails to compile).

---

## ✅ OPTION 1: Docker (Easiest - Recommended)

### Step 1: Start Docker Desktop
1. Open **Docker Desktop** application
2. Wait for it to fully start (whale icon in system tray)
3. Should show "Docker Desktop is running"

### Step 2: Start Services
```powershell
cd c:\Developer\weather_python
docker-compose up -d --build
```

### Step 3: Wait & Access
- Wait ~1-2 minutes for build
- API: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Check Status
```powershell
docker-compose ps
docker-compose logs -f
```

---

## ✅ OPTION 2: Install Python 3.11 (Alternative)

### Step 1: Download Python 3.11
https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

- ✅ Check "Add Python to PATH"
- ✅ Install for all users (optional)
- Install location: `C:\Python311\`

### Step 2: Create Virtual Environment
```powershell
cd c:\Developer\weather_python\backend

# Create venv with Python 3.11
C:\Python311\python.exe -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Start Services (3 Terminals)

**Terminal 1: FastAPI**
```powershell
cd c:\Developer\weather_python\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Celery Worker**
```powershell
cd c:\Developer\weather_python\backend
.\venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

**Terminal 3: Celery Beat**
```powershell
cd c:\Developer\weather_python\backend
.\venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app beat --loglevel=info
```

### Step 4: Start Frontend
```powershell
cd c:\Developer\weather_python\frontend
npm install
npm run dev
```

---

## ✅ OPTION 3: Use Python 3.11 with py launcher

If you install Python 3.11 alongside 3.13:

```powershell
cd c:\Developer\weather_python\backend

# Use py launcher to select Python 3.11
py -3.11 -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Verify version
python --version
# Should show: Python 3.11.9

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

---

## 🎯 Recommended: Use Docker

**Why Docker is best:**
- ✅ No Python version conflicts
- ✅ Everything pre-configured
- ✅ One command to start all services
- ✅ Includes MongoDB & Redis
- ✅ Works exactly like production

**To use Docker:**
1. Start Docker Desktop (whale icon in taskbar)
2. Run: `docker-compose up -d`
3. Wait 2 minutes
4. Open: http://localhost:8000/docs

That's it! 🎉

---

## 🔍 Quick Test

After starting with either option, test the API:

```powershell
# Test health
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Test dashboard
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/dashboard/summary?city=Pune"
```

---

## 📝 Current Status

Your system is fully configured and ready to run. Just need compatible Python version:

- ✅ MongoDB database: `weather_dashboard`
- ✅ Collections aligned with your data
- ✅ API key configured and tested
- ✅ All code written and ready
- ⚠️ Python 3.13 too new (use 3.11 or Docker)

---

## 💡 My Recommendation

**Start Docker Desktop** then run:
```powershell
cd c:\Developer\weather_python
docker-compose up -d --build
```

This avoids all Python version headaches! 🐳
