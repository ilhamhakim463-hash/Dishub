import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-CHANGE-IN-PRODUCTION'

    # Database MySQL - MENGGUNAKAN 127.0.0.1 UNTUK STABILITAS EVENTLET
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_PORT = os.environ.get('DB_PORT', '3307')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = 'laporpak_jombang_diskominfo'

    # URI Koneksi Database
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Optimasi Engine untuk Flask-SocketIO & Eventlet
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'connect_args': {'connect_timeout': 60}
    }

    # Upload
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # WTF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Pagination
    POSTS_PER_PAGE = 12

    # NIK & Kecamatan
    VALID_NIK_PREFIX = '3517'
    NIK_LENGTH = 16
    KECAMATAN_LIST = [
        'Bandar Kedung Mulyo', 'Bareng', 'Diwek', 'Gudo', 'Jombang',
        'Jogoroto', 'Kabuh', 'Kesamben', 'Kudu', 'Megaluh',
        'Mojoagung', 'Mojowarno', 'Ngoro', 'Ngusikan', 'Perak',
        'Peterongan', 'Ploso', 'Plandaan', 'Sumobito', 'Tembelang', 'Wonosalam'
    ]

    # WhatsApp Twilio
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', '')

    # AI
    AI_ENABLED = os.environ.get('AI_ENABLED', 'True') == 'True'

    # SocketIO - Pastikan sinkron dengan app.py
    SOCKETIO_ASYNC_MODE = 'eventlet'

    # Gamification
    POINTS_LAPORAN_DIBUAT = 10
    POINTS_LAPORAN_DISETUJUI = 25
    POINTS_LAPORAN_SELESAI = 50

    # Status (Pastikan sesuai dengan kolom status_warna di database)
    STATUS_MERAH = 'merah'
    STATUS_HIJAU = 'hijau'
    STATUS_BIRU = 'biru'
    STATUS_ABU = 'abu'

    # Urgency
    URGENCY_DARURAT = 1
    URGENCY_BIASA = 2

    # App Info
    APP_NAME = 'LaporPak Jombang Enterprise'
    APP_VERSION = '3.0.0'
    APP_DESCRIPTION = 'Platform Pelaporan Masyarakat Kabupaten Jombang'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}