# 🚀 LaporPak Jombang Enterprise - Production Ready

Platform Pelaporan Masyarakat Kabupaten Jombang dengan fitur enterprise lengkap.

## ⚡ Quick Start (5 Menit!)

```bash
# 1. Extract ZIP
unzip laporpak-final.zip
cd laporpak-final

# 2. Install Python dependencies
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Setup MySQL Port 3307
mysql -h localhost -P 3307 -u root -p < database.sql

# 4. Configure environment
cp .env.example .env
# Edit .env - set DB_PORT=3307 dan SECRET_KEY

# 5. Install template (DOWNLOAD ZIP TERPISAH!)
# Extract laporpak-templates-FINAL.zip
# Copy folder templates/ ke app/templates/

# 6. Run
python app.py
```

Buka: **http://localhost:5000**

## 📦 Paket Lengkap

### ZIP 1: Aplikasi Backend (laporpak-final.zip)
- ✅ Flask app dengan Blueprint architecture
- ✅ Database models & migrations  
- ✅ Utils & helpers lengkap
- ✅ WhatsApp OTP integration
- ✅ AI Chatbot backend
- ✅ Export PDF/Excel
- ✅ Real-time SocketIO
- ✅ PWA support
- ✅ Config untuk port 3307

### ZIP 2: Template HTML (laporpak-templates-FINAL.zip)
- ✅ 23 template HTML lengkap
- ✅ Responsive mobile-first
- ✅ Interactive maps
- ✅ AI chatbot widget
- ✅ Admin command center
- ✅ 100% sinkron dengan backend

## 🏗️ Arsitektur Enterprise

```
laporpak-final/
├── app.py                          # Entry point
├── config.py                       # Configuration
├── requirements.txt                # Dependencies
├── database.sql                    # MySQL schema
├── .env.example                    # Environment template
│
├── app/
│   ├── __init__.py                # App factory
│   ├── models.py                   # Database models
│   ├── utils.py                    # Helper functions
│   │
│   ├── blueprints/                 # Modular routes
│   │   ├── auth/                  # Authentication
│   │   ├── user/                  # User dashboard
│   │   ├── admin/                 # Admin panel
│   │   ├── public/                # Public pages
│   │   └── api/                   # REST API + WebSocket
│   │
│   ├── utils/                      # Utilities
│   │   ├── whatsapp.py            # Twilio integration
│   │   ├── ai_chatbot.py          # NLP chatbot
│   │   ├── geo_utils.py           # Geotagging & maps
│   │   ├── export_utils.py        # PDF & Excel
│   │   └── sentiment.py           # Sentiment analysis
│   │
│   └── static/
│       ├── css/                    # Stylesheets
│       ├── js/                     # JavaScript
│       ├── img/                    # Images
│       └── uploads/                # User uploads
│
├── instance/                        # Instance-specific files
└── logs/                           # Application logs
```

## 🔑 Login Default

```
Admin:
Email: admin@diskominfo.jombang.go.id
Password: Admin@Jombang2024

⚠️ WAJIB GANTI PASSWORD SETELAH LOGIN PERTAMA!
```

## 🗄️ Database (MySQL Port 3307)

### Tables:
1. **users** - Data warga & admin
2. **reports** - Laporan masyarakat
3. **interactions** - Support & comments
4. **notifications** - Push notifications
5. **otp_logs** - WhatsApp OTP tracking
6. **analytics** - Daily statistics
7. **chatbot_sessions** - AI conversation

### Import Database:
```bash
mysql -h localhost -P 3307 -u root -p < database.sql
```

## ✨ Fitur Enterprise

### 🔐 Authentication & Security
- WhatsApp OTP via Twilio
- NIK validation (prefix 3517)
- Password hashing (Scrypt)
- Role-based access control
- Session management

### 👥 User Features
- Dashboard dengan gamification
- Poin warga system
- Digital ID card
- Buat laporan dengan GPS
- Track status real-time
- Notifications

### 📝 Pelaporan
- **Urgency switch**: DARURAT vs BIASA
- **Auto-geotagging**: Extract dari EXIF foto
- **Interactive map**: Leaflet.js, draggable pin
- **Reverse geocoding**: Nominatim API
- **AI-assisted**: Chatbot bantu isi form
- **Offline mode**: IndexedDB queue

### 🎯 Admin Command Center
- **Live map**: Color-coded markers
- **Blinking**: Animation untuk darurat
- **CCTV integration**: Check nearby cameras
- **Sentiment analysis**: Marah/Panik detection
- **Export data**: PDF & Excel
- **User management**: Reset password, activate/deactivate
- **Real-time updates**: Socket.IO

### 🌐 Feed Sosial
- Moderasi anti-hoaks
- Support & comment system
- Hashtag otomatis
- Official "SELESAI" stamp
- Share WhatsApp/Facebook

### 🤖 AI Features
- **LaporBot chatbot**: NLP conversation
- **Auto-extract**: Judul, deskripsi, kategori
- **Sentiment analysis**: Emotional tone detection
- **Priority alerts**: High-risk reports

### 📱 PWA (Progressive Web App)
- Installable di Android/iOS
- Offline capability
- Push notifications
- Background sync
- Service worker

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production (Gunicorn)
```bash
gunicorn -w 4 --worker-class eventlet -b 0.0.0.0:5000 app:app
```

### VPS Setup (Ubuntu)

```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv mysql-server nginx

# 2. Setup MySQL Port 3307
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
# Change: port = 3307
sudo systemctl restart mysql

# 3. Deploy app
cd /var/www/laporpak
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Setup systemd service
sudo nano /etc/systemd/system/laporpak.service

# 5. Setup Nginx reverse proxy
sudo nano /etc/nginx/sites-available/laporpak

# 6. SSL with Let's Encrypt
sudo certbot --nginx -d laporpak.jombang.go.id
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "--worker-class", "eventlet", "-b", "0.0.0.0:5000", "app:app"]
```

## 📊 Environment Variables

```env
# Database (PORT 3307!)
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=laporpak_jombang_enterprise

# Flask
SECRET_KEY=generate-with-secrets.token_hex(32)
FLASK_ENV=production

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# AI
AI_ENABLED=True
```

## 🔧 API Endpoints

### Public API
```
GET  /api/reports              # List public reports
GET  /api/stats                # Statistics
POST /api/report/:id/support   # Support report
```

### WebSocket Events
```javascript
socket.on('report_updated', (data) => {
    // Real-time report updates
});

socket.on('new_report', (data) => {
    // New report notification
});
```

## 📝 Development Guide

### Add New Blueprint
```python
# app/blueprints/custom/__init__.py
from flask import Blueprint
bp = Blueprint('custom', __name__)

# app/__init__.py
from app.blueprints.custom import bp as custom_bp
app.register_blueprint(custom_bp, url_prefix='/custom')
```

### Add New Model
```python
# app/models.py
class NewModel(db.Model):
    __tablename__ = 'new_table'
    id = db.Column(db.Integer, primary_key=True)
    # ...
```

### Add New Util
```python
# app/utils/custom_utils.py
def custom_function():
    pass
```

## 🐛 Troubleshooting

### Port 3307 Error
```bash
# Check MySQL port
sudo netstat -tlnp | grep 3307

# Restart MySQL
sudo systemctl restart mysql
```

### Template Not Found
```bash
# Install template ZIP
unzip laporpak-templates-FINAL.zip
cp -r laporpak-templates/templates/* app/templates/
```

### WhatsApp OTP Not Working
- Check Twilio credentials in .env
- Join WhatsApp Sandbox first
- Verify phone number format (08xxx)

### Database Connection Failed
- Verify port 3307 in .env
- Check MySQL running: `systemctl status mysql`
- Test connection: `mysql -h localhost -P 3307 -u root -p`

## 📚 Documentation

- `README.md` - Main documentation (this file)
- `DEPLOYMENT.md` - Deployment guide (create if needed)
- `API.md` - API documentation (create if needed)

## 🔒 Security Checklist

Before production:
- [ ] Change SECRET_KEY
- [ ] Change admin password
- [ ] Set FLASK_ENV=production
- [ ] Enable HTTPS (SSL)
- [ ] Update Twilio credentials
- [ ] Set SESSION_COOKIE_SECURE=True
- [ ] Configure firewall
- [ ] Setup database backups
- [ ] Enable rate limiting
- [ ] Review file upload limits

## 📞 Support

**Dinas Komunikasi dan Informatika Kabupaten Jombang**
- Email: diskominfo@jombang.go.id
- Phone: 112
- Instagram: @jombangsiaga_112
- Facebook: jombang.1.siaga

## 📄 License

Copyright © 2024 Diskominfo Kabupaten Jombang. All Rights Reserved.

---

**Built with ❤️ for Masyarakat Jombang**

*"Suara Anda, Perubahan Kami"*
