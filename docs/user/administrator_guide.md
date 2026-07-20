# Administrator Guide — DVA Platform v2

## Overview

This guide covers system administration tasks for DVA Platform v2, including installation management, backup/restore procedures, maintenance operations, and troubleshooting.

## System Requirements

### Minimum Specifications

| Component | Requirement |
|-----------|-------------|
| CPU | 2 cores, 2.0 GHz |
| RAM | 4 GB |
| Disk | 500 MB free (data storage separate) |
| OS | Linux (x86_64), Windows 10+, macOS 12+ |

### Recommended Specifications

| Component | Requirement |
|-----------|-------------|
| CPU | 4+ cores, 2.5+ GHz |
| RAM | 8+ GB |
| Disk | 10+ GB free (SSD preferred) |
| OS | Ubuntu 22.04+ / RHEL 9+ |

## Installation

### Production Installation

1. **System Dependencies**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip

# RHEL/CentOS
sudo dnf install -y python3.12 python3.12-pip
```

2. **Create Service User**

```bash
sudo useradd -r -s /bin/false -m -d /opt/dva dva
sudo usermod -aG dva $USER
```

3. **Install Application**

```bash
sudo mkdir -p /opt/dva
sudo chown dva:dva /opt/dva
sudo -u dva git clone <repository-url> /opt/dva/app
```

4. **Setup Virtual Environment**

```bash
cd /opt/dva/app
sudo -u dva python3.12 -m venv venv
sudo -u dva ./venv/bin/pip install -r requirements.txt
```

5. **Create Systemd Service**

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

```bash
sudo systemctl daemon-reload
sudo systemctl enable dva
sudo systemctl start dva
```

6. **Configure Firewall**

```bash
# Allow port 8080 (default)
sudo ufw allow 8080/tcp
# Or for custom port
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8080
CMD ["python3", "-m", "ui.app"]
```

```bash
# Build and run
docker build -t dva-platform .
docker run -d \
  --name dva \
  -p 8080:8080 \
  -v ~/.dva:/root/.dva \
  --restart unless-stopped \
  dva-platform
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DVA_HOST` | `0.0.0.0` | Bind address |
| `DVA_PORT` | `8080` | HTTP port |
| `DVA_DATA_DIR` | `~/.dva` | Data storage directory |
| `DVA_LOG_LEVEL` | `INFO` | Logging level |
| `DVA_MAX_FILE_SIZE` | `1073741824` | Max file size (1GB) |
| `DVA_CACHE_SIZE` | `536870912` | Cache size limit (512MB) |
| `DVA_THEME` | `light` | Default theme |
| `DVA_AUTO_SAVE` | `true` | Enable auto-save |

### Configuration File

The application reads configuration from `~/.dva/config.json`. This file is created automatically on first run.

```json
{
  "host": "0.0.0.0",
  "port": 8080,
  "data_dir": "~/.dva",
  "log_level": "INFO",
  "max_file_size": 1073741824,
  "cache_size": 536870912,
  "theme": "light",
  "auto_save": true,
  "max_projects": 50,
  "max_connections": 20
}
```

## Backup and Restore

### Backup Procedure

The DVA data directory (`~/.dva/`) contains all persistent state:

```bash
# Create backup
tar -czf dva-backup-$(date +%Y%m%d-%H%M%S).tar.gz ~/.dva/

# Automated backup script
#!/bin/bash
BACKUP_DIR="/var/backups/dva"
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/dva-$(date +%Y%m%d-%H%M%S).tar.gz" ~/.dva/
find "$BACKUP_DIR" -name "dva-*.tar.gz" -mtime +30 -delete
```

### Restore Procedure

```bash
# Stop the service
sudo systemctl stop dva

# Restore from backup
tar -xzf dva-backup-20250101-120000.tar.gz -C ~/

# Verify restoration
ls -la ~/.dva/

# Start the service
sudo systemctl start dva
```

### What Gets Backed Up

| Item | Path | Description |
|------|------|-------------|
| Session State | `~/.dva/session.json` | Active workspace and selections |
| Projects | `~/.dva/projects/` | Project configurations |
| Connections | `~/.dva/connections/` | Connection settings |
| Logs | `~/.dva/logs/` | Application logs |
| Settings | `~/.dva/config.json` | Application configuration |
| Cache | `~/.dva/cache/` | Temporary cached data |

## Maintenance

### Routine Tasks

#### Daily
- Monitor disk usage in data directory
- Review error logs for critical issues
- Check service status

#### Weekly
- Rotate log files
- Clear cache directory
- Verify backup integrity

#### Monthly
- Update dependencies
- Review and archive old projects
- Performance benchmark

### Log Management

Logs are stored in `~/.dva/logs/` with automatic rotation:

```bash
# View recent logs
tail -f ~/.dva/logs/dva.log

# Archive old logs
tar -czf logs-archive-$(date +%Y%m).tar.gz ~/.dva/logs/*.log.*
rm ~/.dva/logs/*.log.*
```

### Cache Management

```bash
# Clear all cache
rm -rf ~/.dva/cache/*

# Check cache size
du -sh ~/.dva/cache/
```

### Monitoring

#### Health Check Endpoint

The Health workspace provides real-time monitoring:
- Service status indicators
- Memory and CPU usage
- Uptime tracking
- Active sessions count

#### System Metrics

Track the following metrics:
- Application response time
- Memory footprint over time
- Number of concurrent sessions
- File processing throughput
- Export generation time

### Performance Tuning

#### Memory
- Reduce cache size for memory-constrained environments
- Process files in chunks for large datasets
- Monitor memory usage in Health workspace

#### CPU
- Adjust chunk sizes for processing (default: 10,000 rows)
- Disable statistics computation when not needed
- Use streaming mode for large files

## Security

### Network Security

- Run behind a reverse proxy (nginx, Apache) for production
- Enable HTTPS with TLS 1.2+
- Restrict access via firewall
- Use VPN for remote access

### File System Security

- Run as dedicated service user (not root)
- Restrict data directory permissions
- Validate file paths to prevent traversal attacks
- Sanitize file names and paths

### Data Security

- Session data stored locally only
- No sensitive data transmitted externally
- Temporary files cleaned after processing
- Cache expiration and automatic cleanup

## Upgrading

### Version Upgrade Procedure

```bash
# 1. Stop service
sudo systemctl stop dva

# 2. Backup data
tar -czf pre-upgrade-backup.tar.gz ~/.dva/

# 3. Backup current version
cp -r /opt/dva/app /opt/dva/app.bak

# 4. Update code
cd /opt/dva/app
git pull origin main

# 5. Update dependencies
./venv/bin/pip install -r requirements.txt

# 6. Run migrations (if applicable)
./venv/bin/python3 -c "from ui.shared import persistence; persistence.run_migrations()"

# 7. Start service
sudo systemctl start dva

# 8. Verify
sudo systemctl status dva
```

### Rollback Procedure

```bash
sudo systemctl stop dva
rm -rf /opt/dva/app
cp -r /opt/dva/app.bak /opt/dva/app
sudo systemctl start dva
```

## Troubleshooting

### Service Won't Start

1. Check logs: `journalctl -u dva -n 50`
2. Verify Python version: `python3 --version`
3. Check port availability: `ss -tlnp | grep 8080`
4. Validate dependencies: `./venv/bin/python3 scripts/dependency_checker.py`

### High Memory Usage

1. Check Health workspace for memory metrics
2. Reduce cache size in settings
3. Restart application to clear memory
4. Check for memory leaks in processing loops

### Permission Errors

1. Verify service user ownership: `ls -la ~/.dva/`
2. Check data directory permissions
3. Ensure temp directory is writable
4. Validate file system mount options

## Support

For issues beyond basic administration:
- Check the [Troubleshooting Guide](troubleshooting_guide.md)
- Review application logs
- Contact development team
- File issues in the project repository
