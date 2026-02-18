# 🚀 LaporPak Jombang - Panduan Deployment VPS

## Deployment ke VPS Ubuntu 22.04

### 1. Persiapan Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server
```

### 2. Setup MySQL Port 3307

```bash
# Edit MySQL config
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Ubah:
# port = 3306
# Menjadi:
# port = 3307

# Restart MySQL
sudo systemctl restart mysql

# Secure MySQL
sudo mysql_secure_installation
```

### 3. Deploy Aplikasi

```bash
# Create directory
sudo mkdir -p /var/www/laporpak
sudo chown -R $USER:$USER /var/www/laporpak
cd /var/www/laporpak

# Upload files (via SCP/FTP)
# atau git clone

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Edit configuration

# Import database
mysql -h localhost -P 3307 -u root -p < database.sql

# Install templates
# Upload laporpak-templates-FINAL.zip
unzip laporpak-templates-FINAL.zip
cp -r laporpak-templates/templates/* app/templates/
```

### 4. Setup Gunicorn Service

```bash
sudo nano /etc/systemd/system/laporpak.service
```

```ini
[Unit]
Description=LaporPak Jombang Application
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/laporpak
Environment="PATH=/var/www/laporpak/venv/bin"
ExecStart=/var/www/laporpak/venv/bin/gunicorn \
    -w 4 \
    --worker-class eventlet \
    -b 127.0.0.1:5000 \
    --access-logfile /var/www/laporpak/logs/access.log \
    --error-logfile /var/www/laporpak/logs/error.log \
    app:app

[Install]
WantedBy=multi-user.target
```

```bash
# Enable & start service
sudo systemctl daemon-reload
sudo systemctl enable laporpak
sudo systemctl start laporpak
sudo systemctl status laporpak
```

### 5. Setup Nginx

```bash
sudo nano /etc/nginx/sites-available/laporpak
```

```nginx
server {
    listen 80;
    server_name laporpak.jombang.go.id www.laporpak.jombang.go.id;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/laporpak/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    client_max_body_size 16M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/laporpak /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL dengan Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d laporpak.jombang.go.id -d www.laporpak.jombang.go.id

# Auto-renewal
sudo certbot renew --dry-run
```

### 7. Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3307/tcp  # MySQL
sudo ufw enable
```

### 8. Monitoring & Logs

```bash
# View application logs
sudo journalctl -u laporpak -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View app logs
tail -f /var/www/laporpak/logs/access.log
tail -f /var/www/laporpak/logs/error.log
```

## Maintenance

### Update Aplikasi

```bash
cd /var/www/laporpak
source venv/bin/activate
git pull  # atau upload file baru
pip install -r requirements.txt
sudo systemctl restart laporpak
```

### Backup Database

```bash
# Backup
mysqldump -h localhost -P 3307 -u root -p laporpak_jombang_enterprise > backup_$(date +%Y%m%d).sql

# Restore
mysql -h localhost -P 3307 -u root -p laporpak_jombang_enterprise < backup_20240203.sql
```

### Auto Backup (Cron)

```bash
crontab -e

# Add:
0 2 * * * /usr/bin/mysqldump -h localhost -P 3307 -u root -pYOUR_PASSWORD laporpak_jombang_enterprise > /backup/laporpak_$(date +\%Y\%m\%d).sql
```

## Performance Optimization

### 1. MySQL Tuning

```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

```ini
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
max_connections = 200
query_cache_size = 32M
```

### 2. Gunicorn Workers

```ini
# Increase workers based on CPU cores
ExecStart=... -w 8 ...
```

### 3. Nginx Caching

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=laporpak_cache:10m max_size=1g;

location / {
    proxy_cache laporpak_cache;
    proxy_cache_valid 200 10m;
    ...
}
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u laporpak -n 50

# Check permissions
sudo chown -R www-data:www-data /var/www/laporpak

# Test manually
cd /var/www/laporpak
source venv/bin/activate
python app.py
```

### Database Connection Error

```bash
# Test connection
mysql -h localhost -P 3307 -u root -p

# Check .env file
cat .env | grep DB_
```

### Nginx 502 Bad Gateway

```bash
# Check if Gunicorn is running
sudo systemctl status laporpak

# Check Gunicorn bind address
ps aux | grep gunicorn
```

---

**Deploy dengan sukses!** 🚀
