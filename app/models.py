from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    nik = db.Column(db.String(16), unique=True, nullable=False)
    no_wa = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)

    # Kolom password_hash sudah sinkron dengan sistem login terbaru
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default='user')
    kecamatan = db.Column(db.String(50), nullable=False)
    alamat = db.Column(db.Text)
    poin_warga = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    foto_profil = db.Column(db.String(255), default='default.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # RELASI
    reports = db.relationship('Report', backref='author', lazy='dynamic')
    interactions = db.relationship('Interaction', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    reports = db.relationship('Report', backref='category_rel', lazy='dynamic')


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    judul = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    kategori = db.Column(db.String(100), nullable=False)

    # Foto & Progres
    foto_awal = db.Column(db.String(255), nullable=False)
    foto_2 = db.Column(db.String(255), nullable=True)
    foto_3 = db.Column(db.String(255), nullable=True)

    # Lokasi (Penting agar Pin Muncul)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    alamat_manual = db.Column(db.String(255))

    # Status & Moderasi
    is_approved = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    status_warna = db.Column(db.String(20), default='abu-abu')
    status_label = db.Column(db.String(50))

    # Statistik & Interaksi
    support_count = db.Column(db.Integer, default=0)
    komentar_admin = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)

    # Relasi Interaksi
    comments = db.relationship('Interaction', backref='report', lazy='dynamic', cascade='all, delete-orphan')


class EmergencyAlert(db.Model):
    __tablename__ = 'emergency_alerts'
    id = db.Column(db.Integer, primary_key=True)
    tipe_bencana = db.Column(db.String(50), nullable=False)
    pesan = db.Column(db.Text, nullable=False)
    wilayah_terdampak = db.Column(db.String(50), nullable=False)
    level_bahaya = db.Column(db.String(20), default='bahaya')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Interaction(db.Model):
    __tablename__ = 'interactions'
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tipe = db.Column(db.String(20))
    konten = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)