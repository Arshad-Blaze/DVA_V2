# Installation Guide — DVA Platform v2

## Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores, 2.0 GHz | 4+ cores, 2.5+ GHz |
| RAM | 4 GB | 8+ GB |
| Disk Space | 500 MB free | 10+ GB free |
| OS | Linux, Windows 10+, macOS 12+ | Ubuntu 22.04+ |
| Python | 3.12.0 | 3.12.x |

### Required Software

- **Python 3.12+** — Available from [python.org](https://python.org) or system package manager
- **pip** — Python package installer (included with Python 3.12+)
- **Git** (optional) — For cloning the repository

### Optional Software

- **Docker** — For containerized deployment
- **nginx** — For reverse proxy setup (production)

## Installation Steps

### Step 1: Verify Python

```bash
python3 --version
```

You must see Python 3.12.x or later. If not, install Python 3.12:

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

**RHEL/CentOS/Fedora**:
```bash
sudo dnf install python3.12 python3.12-pip
```

**Windows**:
Download from [python.org](https://www.python.org/downloads/) and ensure "Add Python to PATH" is checked during installation.

**macOS**:
```bash
# Using Homebrew
brew install python@3.12
```

### Step 2: Obtain the Platform

**Option A: Clone from Repository**
```bash
git clone <repository-url> dva-platform
cd dva-platform
```

**Option B: Download Archive**
```bash
# Extract the downloaded archive
tar -xzf dva-platform-v2.0.0.tar.gz
cd dva-platform-v2.0.0
```

### Step 3: Create Virtual Environment

Using a virtual environment is strongly recommended to avoid conflicts with system packages.

**Linux/macOS**:
```bash
python3.12 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt)**:
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell)**:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### Step 4: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:
- **NiceGUI** — Web UI framework
- **Polars** — DataFrame processing engine
- **DuckDB** — Embedded database for temporary storage
- **PyArrow** — Columnar format support
- **psutil** — System monitoring

### Step 6: Verify Installation

```bash
python3 scripts/dependency_checker.py
```

Expected output:
```
Checking dependencies...

  nicegui: installed 1.4.15 ✓
  polars: installed 0.20.19 ✓
  duckdb: installed 0.10.0 ✓
  pyarrow: installed 15.0.0 ✓

  Python: 3.12.3 ✓

All dependencies satisfied ✓
```

### Step 7: Run Environment Validation

```bash
python3 scripts/environment_validation.py
```

Expected output:
```
DVA Platform — Environment Validation
==================================================

  ✓ Python version
  ✓ Home directory writable
  ✓ DVA config directory
  ✓ Temp directory writable

Environment validation PASSED ✓
```

### Step 8: Launch the Application

```bash
python3 -m ui.app
```

Open your browser to **http://localhost:8080**

You should see the Welcome Wizard on first launch.

## Running Startup Validation

Before launching the application, you can run the startup validation script to catch common issues:

```bash
python3 scripts/startup_validation.py
```

This checks:
- Python version compatibility
- Critical package imports (NiceGUI, Polars)
- DVA config directory accessibility
- Port 8080 availability

## Docker Installation

### Using Dockerfile

1. **Create Dockerfile** (included in project root):

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8080
CMD ["python3", "-m", "ui.app"]
```

2. **Build the image**:

```bash
docker build -t dva-platform .
```

3. **Run the container**:

```bash
docker run -d \
  --name dva \
  -p 8080:8080 \
  -v ~/.dva:/root/.dva \
  --restart unless-stopped \
  dva-platform
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  dva:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ~/.dva:/root/.dva
    restart: unless-stopped
```

```bash
docker-compose up -d
```

## Production Installation

### Linux (Systemd Service)

1. **Create service user**:

```bash
sudo useradd -r -s /bin/false -m -d /opt/dva dva
```

2. **Install application**:

```bash
sudo mkdir -p /opt/dva/app
sudo cp -r * /opt/dva/app/
sudo chown -R dva:dva /opt/dva/app
```

3. **Setup virtual environment**:

```bash
cd /opt/dva/app
sudo -u dva python3.12 -m venv venv
sudo -u dva ./venv/bin/pip install -r requirements.txt
```

4. **Create systemd service**:

```ini
# /etc/systemd/system/dva.service
[Unit]
Description=DVA Platform v2
After=network.target

[Service]
User=dva
Group=dva
WorkingDirectory=/opt/dva/app
ExecStart=/opt/dva/app/venv/bin/python3 -m ui.app
Restart=on-failure
RestartSec=5
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

5. **Enable and start**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dva
sudo systemctl start dva
sudo systemctl status dva
```

### Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name dva.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Post-Installation Verification

### 1. Check Service Status

```bash
# If using systemd
sudo systemctl status dva

# If running directly
ps aux | grep ui.app
```

### 2. Test Application Access

```bash
curl -s http://localhost:8080 | head -20
```

Should return HTML content from the application.

### 3. Validate Core Functionality

```bash
# Run dependency check
python3 scripts/dependency_checker.py

# Run environment validation
python3 scripts/environment_validation.py

# Run startup validation
python3 scripts/startup_validation.py
```

### 4. Open in Browser

Navigate to `http://localhost:8080` and complete the Welcome Wizard.

## Troubleshooting Installation

### pip install fails with compilation errors

**Solution**: Install build tools:
```bash
# Ubuntu/Debian
sudo apt install build-essential python3-dev

# RHEL/CentOS
sudo dnf install gcc python3-devel
```

### "No module named nicegui"

**Solution**: Activate virtual environment and install requirements:
```bash
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### "Address already in use" on port 8080

**Solution**: Change port:
```bash
# Using environment variable
export DVA_PORT=8081
python3 -m ui.app

# Or modify in ui/app.py (line with ui.run port parameter)
```

### Permission denied on ~/.dva

**Solution**: Ensure home directory is writable:
```bash
ls -ld ~/
chmod 755 ~/
```

## Uninstall

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv/

# Remove application directory
rm -rf dva-platform/

# Remove DVA data (projects, connections, settings)
rm -rf ~/.dva/
```

## Next Steps

- Read the [Quick Start Guide](quick_start_guide.md) for your first workflow
- Review the [User Guide](user_guide.md) for detailed feature descriptions
- See the [Administrator Guide](administrator_guide.md) for production deployment
- Check the [FAQ](faq.md) for common questions
