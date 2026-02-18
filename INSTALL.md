# 📦 Panduan Instalasi LaporPak Enterprise

## ⚡ Quick Install

### 1. Extract & Setup

```bash
# Extract backend
unzip laporpak-backend-FINAL.zip
cd laporpak-final

# Extract templates (DOWNLOAD ZIP TERPISAH)
unzip laporpak-templates-FINAL.zip
cp -r laporpak-templates/templates/* app/templates/
```

### 2. Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. MySQL Database (Port 3307)

```bash
# Import schema
mysql -h localhost -P 3307 -u root -p < database.sql
```

### 4. Configuration

```bash
cp .env.example .env
nano .env

# Edit:
DB_PORT=3307
SECRET_KEY=<generate-random>
```

### 5. Run

```bash
python app.py
```

## 📝 Catatan Penting

### Dua ZIP Terpisah:

1. **laporpak-backend-FINAL.zip**
   - Flask application
   - Database schema
   - Configuration
   - Documentation

2. **laporpak-templates-FINAL.zip** (DOWNLOAD TERPISAH)
   - 23 HTML templates
   - Responsive mobile-first
   - 100% sinkron dengan backend

### Struktur Akhir:

```
laporpak-final/
├── app/
│   ├── templates/          ← DARI ZIP TEMPLATE
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── user/
│   │   ├── admin/
│   │   └── public/
│   ├── static/
│   ├── models.py
│   └── __init__.py
├── app.py
├── config.py
└── database.sql
```

## ✅ Verifikasi Instalasi

```bash
# Check Python version
python --version  # 3.8+

# Check MySQL
mysql -h localhost -P 3307 -u root -p

# Check virtual environment
which python  # Should be in venv/

# Test run
python app.py
```

## 🚀 Ready to Deploy!

Lihat `DEPLOYMENT.md` untuk deployment ke VPS.
