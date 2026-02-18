from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import User
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash  # Pastikan import ini ada
import logging

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard' if current_user.role == 'admin' else 'user.dashboard'))

    if request.method == 'POST':
        nama = request.form.get('nama')
        nik = request.form.get('nik')
        no_wa = request.form.get('no_wa')
        email = request.form.get('email')
        kecamatan = request.form.get('kecamatan')
        password = request.form.get('password')

        if not all([nama, nik, no_wa, kecamatan, password]):
            flash('Semua kolom bertanda * wajib diisi!', 'danger')
            return redirect(url_for('auth.register'))

        # Validasi NIK Jombang
        if not nik.startswith('3517'):
            flash('Pendaftaran khusus warga dengan NIK Jombang (3517)!', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(nik=nik).first():
            flash('NIK sudah terdaftar dalam sistem!', 'warning')
            return redirect(url_for('auth.register'))

        new_user = User(
            nama=nama,
            nik=nik,
            no_wa=no_wa,
            email=email if email else None,
            kecamatan=kecamatan,
            role='user',
            is_active=True,
            poin_warga=0
        )
        # Menggunakan method set_password dari model Anda
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Akun berhasil dibuat! Silakan login untuk melapor.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
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

        # Cari user berdasarkan NIK, No WA, atau Email
        user = User.query.filter(
            (User.nik == login_id) |
            (User.no_wa == login_id) |
            (User.email == login_id)
        ).first()

        # LOGIKA LOGIN: Cek keberadaan user dan kecocokan password hash
        # Kita gunakan check_password_hash langsung atau method user.check_password
        if user and user.check_password(password):

            # --- PROTEKSI SISTEM BLOKIR ---
            if not user.is_active:
                flash('Akses Ditolak! Akun Anda telah dinonaktifkan oleh Admin.', 'danger')
                return redirect(url_for('auth.login'))

            login_user(user, remember=remember)

            # Redirect berdasarkan Role
            if user.role == 'admin':
                flash(f'Mode Admin Aktif: Selamat bertugas, {user.nama}!', 'primary')
                return redirect(url_for('admin.dashboard'))

            flash(f'Selamat datang kembali, {user.nama}!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Login gagal! Cek NIK/WA/Email dan password Anda.', 'danger')

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah keluar dari sistem.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    # Route ini untuk halaman "Lupa Password" warga (mengirim OTP/WA)
    return render_template('auth/reset_password.html')