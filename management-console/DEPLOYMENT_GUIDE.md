# Stinger Management Console Deployment Guide

## Overview
The Stinger Management Console provides real-time monitoring and analytics for your Stinger deployments. This guide covers various deployment options.

## Quick Start (Development)

```bash
cd management-console
./start_console.sh
```

Access at:
- Frontend: http://localhost:3001
- Backend API: http://localhost:8001

## Production Deployment

### Prerequisites
- Python 3.8+
- Node.js 16+
- 2GB RAM minimum
- 10GB disk space for logs

### 1. Docker Deployment (Recommended)

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8001:8001"
    environment:
      - STINGER_CONFIG_PATH=/app/config/stinger.yaml
      - AUDIT_LOG_PATH=/app/logs/audit.log
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3001:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://backend:8001
    restart: unless-stopped
```

Deploy:
```bash
docker-compose up -d
```

### 2. Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stinger-console
spec:
  replicas: 1
  selector:
    matchLabels:
      app: stinger-console
  template:
    metadata:
      labels:
        app: stinger-console
    spec:
      containers:
      - name: backend
        image: stinger-console-backend:latest
        ports:
        - containerPort: 8001
        env:
        - name: AUDIT_LOG_PATH
          value: /data/audit.log
        volumeMounts:
        - name: data
          mountPath: /data
      - name: frontend
        image: stinger-console-frontend:latest
        ports:
        - containerPort: 80
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: stinger-data
```

### 3. Systemd Service (Linux)

Create `/etc/systemd/system/stinger-console.service`:

```ini
[Unit]
Description=Stinger Management Console
After=network.target

[Service]
Type=simple
User=stinger
WorkingDirectory=/opt/stinger-console
ExecStart=/opt/stinger-console/start_console.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable stinger-console
sudo systemctl start stinger-console
```

## Configuration

### Environment Variables

Backend:
- `STINGER_CONFIG_PATH`: Path to Stinger configuration file
- `AUDIT_LOG_PATH`: Path to audit log file
- `PORT`: Backend port (default: 8001)
- `HOST`: Backend host (default: 0.0.0.0)

Frontend:
- `REACT_APP_API_URL`: Backend API URL
- `PORT`: Frontend port (default: 3001)

### Performance Tuning

1. **Enable production mode**:
   ```bash
   export NODE_ENV=production
   npm run build
   ```

2. **Increase backend workers**:
   ```python
   # In start_console.sh
   uvicorn main:app --workers 4
   ```

3. **Configure log rotation**:
   ```bash
   # /etc/logrotate.d/stinger
   /var/log/stinger/*.log {
       daily
       rotate 7
       compress
       delaycompress
       missingok
       notifempty
   }
   ```

## Monitoring Multiple Instances

To monitor multiple Stinger deployments:

1. **Configure multiple backends**:
   ```python
   # In backend/main.py
   DEPLOYMENTS = {
       "prod": {"config": "/configs/prod.yaml", "logs": "/logs/prod/"},
       "staging": {"config": "/configs/staging.yaml", "logs": "/logs/staging/"}
   }
   ```

2. **Add instance selector in frontend**:
   ```javascript
   // In frontend App.js
   const [instance, setInstance] = useState('prod');
   ```

## Security Considerations

### 1. Enable HTTPS

Use a reverse proxy (nginx/caddy):

```nginx
server {
    listen 443 ssl http2;
    server_name console.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Basic Authentication (Optional)

Add to nginx:
```nginx
auth_basic "Stinger Console";
auth_basic_user_file /etc/nginx/.htpasswd;
```

### 3. IP Whitelisting

```nginx
location / {
    allow 10.0.0.0/8;
    allow 192.168.0.0/16;
    deny all;
    proxy_pass http://localhost:3001;
}
```

## Backup and Recovery

### Automated Backups

Create backup script:
```bash
#!/bin/bash
# /opt/stinger-console/backup.sh

BACKUP_DIR="/backups/stinger"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup audit logs
tar -czf "$BACKUP_DIR/audit_logs_$DATE.tar.gz" /var/log/stinger/

# Backup metrics database (if using)
pg_dump stinger_metrics > "$BACKUP_DIR/metrics_$DATE.sql"

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /opt/stinger-console/backup.sh
```

## Troubleshooting

### Common Issues

1. **Console not loading**:
   - Check backend is running: `curl http://localhost:8001/api/health`
   - Check frontend proxy settings
   - Review browser console for errors

2. **No metrics displayed**:
   - Verify audit log path is correct
   - Check file permissions
   - Ensure Stinger pipeline is configured

3. **High memory usage**:
   - Enable data retention policies
   - Reduce polling intervals
   - Use virtual scrolling for logs

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
export LOG_LEVEL=debug
./start_console.sh
```

## Performance Optimization

1. **CDN for static assets**:
   ```bash
   npm run build
   aws s3 sync build/ s3://your-bucket/
   aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
   ```

2. **Database for metrics** (optional):
   - Use PostgreSQL/TimescaleDB for metrics storage
   - Implement data aggregation policies
   - Index frequently queried fields

3. **Caching**:
   - Enable Redis for API caching
   - Set appropriate cache TTLs
   - Use browser caching headers

## Monitoring the Monitor

Use standard monitoring tools:
- Prometheus metrics endpoint: `/metrics`
- Health check: `/api/health`
- Uptime monitoring with Pingdom/UptimeRobot

## Support

For issues or questions:
- GitHub Issues: https://github.com/virtualsteve-star/stinger/issues
- Documentation: https://stinger.readthedocs.io