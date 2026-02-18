import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import Report, Category
from app import db
from datetime import datetime

user = Blueprint('user', __name__)


# Fungsi Helper untuk Simpan Foto
def save_photo(file):
    if file and file.filename != '':
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        upload_path = os.path.join(current_app.root_path, 'static/uploads/reports', filename)

        # Pastikan folder ada
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)

        file.save(upload_path)
        return filename
    return None


@user.route('/user/lapor', methods=['GET', 'POST'])
@login_required
def create_report():
    if request.method == 'POST':
        # Line 28: Ambil data dari form
        judul = request.form.get('judul')
        deskripsi = request.form.get('deskripsi')
        kategori = request.form.get('kategori')
        status_warna = request.form.get('status_warna', 'hijau')
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')
        alamat = request.form.get('alamat_manual')

        # Line 37: Proses 3 Foto (Awal, Proses, Selesai)
        foto_awal = save_photo(request.files.get('foto_awal'))
        foto_proses = save_photo(request.files.get('foto_proses'))
        foto_selesai = save_photo(request.files.get('foto_selesai'))

        # Simpan ke Database
        new_report = Report(
            judul=judul,
            deskripsi=deskripsi,
            kategori=kategori,
            status_warna=status_warna,  # Enterprise Core Color
            latitude=lat,
            longitude=lng,
            lokasi_manual=alamat,
            foto_awal=foto_awal,
            foto_proses=foto_proses,
            foto_selesai=foto_selesai,
            user_id=current_user.id,
            created_at=datetime.now()
        )

        db.session.add(new_report)
        db.session.commit()

        flash('Laporan Dishub berhasil terkirim ke Command Center!', 'success')
        return redirect(url_for('user.my_reports'))

    # Menambahkan now=datetime.now() untuk mencegah UndefinedError di template
    return render_template('user/laporan.html', now=datetime.now())


@user.route('/user/my-reports')
@login_required
def my_reports():
    # Line 69: Menampilkan riwayat laporan user tersebut
    user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()

    # Menambahkan now=datetime.now() agar widget jam/status di layout tidak error
    return render_template('user/my_reports.html', reports=user_reports, now=datetime.now())


# --- TAMBAHAN UNTUK DASHBOARD USER (Fix UndefinedNow) ---
@user.route('/user/dashboard')
@login_required
def dashboard():
    # Menghitung statistik pribadi user
    user_reports = Report.query.filter_by(user_id=current_user.id)
    stats = {
        'total': user_reports.count(),
        'proses': user_reports.filter_by(status_warna='biru').count(),
        'selesai': user_reports.filter_by(status_warna='hijau').count()
    }

    # PASTI KAN mengirim now=datetime.now() di sini
    return render_template('user/dashboard.html', stats=stats, now=datetime.now())