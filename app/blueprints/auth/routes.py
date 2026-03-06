from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import User
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from datetime import datetime
import logging

auth = Blueprint('auth', __name__)

# --- FUNGSI PELACAK ONLINE ---
@auth.before_app_request
def before_request():
    """Memperbarui waktu aktivitas terakhir jika user sedang login"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

# --- ROUTES OTENTIKASI ---

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard' if current_user.role == 'admin' else 'user.dashboard'))

    if request.method == 'POST':
        nama = request.form.get('nama')
        no_wa = request.form.get('no_wa')
        email = request.form.get('email')
        kecamatan = request.form.get('kecamatan')
        password = request.form.get('password')

        # REVISI: NIK dihapus dari pengecekan wajib
        if not all([nama, no_wa, kecamatan, password]):
            flash('Semua kolom bertanda * wajib diisi!', 'danger')
            return redirect(url_for('auth.register'))

        # REVISI: Pengecekan duplikasi kini berdasarkan Nomor WhatsApp (karena NIK sudah tidak ada)
        if User.query.filter_by(no_wa=no_wa).first():
            flash('Nomor WhatsApp sudah terdaftar!', 'warning')
            return redirect(url_for('auth.register'))

        # REVISI: Inisialisasi User baru tanpa parameter NIK
        new_user = User(
            nama=nama,
            no_wa=no_wa,
            email=email if email else None,
            kecamatan=kecamatan,
            role='user',
            is_active=True,
            poin_warga=0
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Akun berhasil dibuat! Silakan login untuk melapor.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error pada registrasi: {str(e)}")
            flash('Terjadi kesalahan database. Silakan coba lagi.', 'danger')

    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard' if current_user.role == 'admin' else 'user.dashboard'))

    if request.method == 'POST':
        login_id = request.form.get('login_input')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # REVISI: Cari user hanya berdasarkan No WA atau Email (NIK dihapus dari filter)
        user = User.query.filter(
            (User.no_wa == login_id) |
            (User.email == login_id)
        ).first()

        if user and user.check_password(password):
            # --- PROTEKSI SISTEM BLOKIR ---
            if not user.is_active:
                flash('Akses Ditolak! Akun Anda telah dinonaktifkan oleh Admin.', 'danger')
                return redirect(url_for('auth.login'))

            login_user(user, remember=remember)

            # Update last_seen langsung saat login
            user.last_seen = datetime.utcnow()
            db.session.commit()

            # Redirect berdasarkan Role
            if user.role == 'admin':
                flash(f'Mode Admin Aktif: Selamat bertugas, {user.nama}!', 'primary')
                return redirect(url_for('admin.dashboard'))

            flash(f'Selamat datang kembali, {user.nama}!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            # REVISI: Pesan error disesuaikan (Tanpa menyebut NIK)
            flash('Login gagal! Cek WhatsApp/Email dan password Anda.', 'danger')

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah keluar dari sistem.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    return render_template('auth/reset_password.html')