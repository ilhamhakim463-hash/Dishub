from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.blueprints.admin import admin
from app.models import User, Report, EmergencyAlert, Category, Interaction
from app import db
from sqlalchemy import func, or_, extract
from datetime import datetime, timedelta, time
import os
from werkzeug.utils import secure_filename


# --- HELPER: SAVE UPLOAD (SINKRON DENGAN FEEDBACK ADMIN) ---
def save_feedback_photo(file):
    """Fungsi pembantu untuk menyimpan foto progres/selesai dari admin"""
    if file:
        filename = secure_filename(f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        # Menggunakan current_app.root_path agar path absolut selalu benar
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'reports')

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file.save(os.path.join(upload_folder, filename))
        return filename
    return None


# --- CONTEXT PROCESSOR (Navigasi Sidebar Dashboard Admin) ---
@admin.app_context_processor
def inject_status_nav():
    status_menu = [
        {'nama': 'Darurat', 'warna': 'merah', 'icon': 'bi-exclamation-triangle-fill'},
        {'nama': 'Proses', 'warna': 'biru', 'icon': 'bi-gear-fill'},
        {'nama': 'Selesai', 'warna': 'hijau', 'icon': 'bi-check-circle-fill'}
    ]
    return dict(sidebar_status=status_menu)


# --- MIDDLEWARE: PROTEKSI ADMIN ---
@admin.before_request
@login_required
def is_admin():
    """Memastikan hanya user dengan role 'admin' yang bisa masuk ke blueprint ini"""
    if current_user.role != 'admin':
        flash('Akses ditolak! Anda bukan administrator.', 'danger')
        return redirect(url_for('main.dashboard'))


# --- DASHBOARD & STATISTIK (FIXED & FULL LOGIC) ---
@admin.route('/dashboard')
def dashboard():
    """
    Menghitung statistik utama Command Center.
    Sinkron dengan card: Total, SLA Overdue, Sedang, dan Tuntas.
    """
    reports_query = Report.query

    # Statistik Utama untuk Card Dashboard (Nilai Tidak Tetap)
    stats = {
        'total_reports': reports_query.count(),
        'darurat': reports_query.filter_by(status_warna='merah').count(),  # SLA Overdue / Urgent
        'sedang': reports_query.filter_by(status_warna='kuning').count(),  # Urgency Sedang
        'proses': reports_query.filter_by(status_warna='biru').count(),  # Sedang Dikerjakan
        'selesai': reports_query.filter_by(status_warna='hijau').count(),  # Tuntas
        'total_warga': User.query.filter(User.role != 'admin').count()
    }

    # Logika Grafik Mingguan (7 Hari Terakhir)
    days, weekly_data = [], []
    day_labels = {'Mon': 'Sen', 'Tue': 'Sel', 'Wed': 'Rab', 'Thu': 'Kam', 'Fri': 'Jum', 'Sat': 'Sab', 'Sun': 'Min'}

    for i in range(6, -1, -1):
        target_date = (datetime.now() - timedelta(days=i)).date()
        raw_day = (datetime.now() - timedelta(days=i)).strftime('%a')
        days.append(day_labels.get(raw_day, raw_day))

        start_day = datetime.combine(target_date, time.min)
        end_day = datetime.combine(target_date, time.max)

        count = Report.query.filter(
            Report.created_at >= start_day,
            Report.created_at <= end_day
        ).count()
        weekly_data.append(count)

    # 10 Laporan Terbaru untuk Tabel Dashboard
    recent_reports = Report.query.order_by(Report.created_at.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_reports=recent_reports,
                           days=days,
                           weekly_data=weekly_data,
                           now=datetime.now())


# --- API MAPS (SINKRONISASI PIN MULTI-WARNA) ---
@admin.route('/api/reports-map-data')
def reports_map_data():
    """Endpoint API untuk merender marker di Peta Leaflet/Google Maps Admin"""
    reports = Report.query.filter(
        Report.latitude.isnot(None),
        Report.longitude.isnot(None),
        Report.is_archived == False
    ).all()

    data = []
    for r in reports:
        # Penentuan label urgensi teks berdasarkan warna status
        urgensi_text = "BIASA"
        if r.status_warna == 'merah':
            urgensi_text = "DARURAT"
        elif r.status_warna == 'kuning':
            urgensi_text = "SEDANG"

        data.append({
            'id': r.id,
            'judul': r.judul or "Tanpa Judul",
            'lat': r.latitude,
            'lng': r.longitude,
            'status_warna': r.status_warna or 'biru',
            'urgensi_label': urgensi_text,
            'foto': r.foto_awal if r.foto_awal else None,
            'pelapor': r.author.nama if r.author else 'Anonim',
            'kategori': r.kategori or 'Umum',
            'url_detail': url_for('admin.view_report', report_id=r.id),
            'created_at': r.created_at.strftime('%d/%m/%Y %H:%M')
        })
    return jsonify(data)


# --- LOG LAPORAN (MANAGEMENT TABLE) ---
@admin.route('/reports')
def reports():
    """Manajemen daftar laporan dengan filter status, kategori, dan pencarian global"""
    status_filter = request.args.get('status', 'Semua').lower()
    kategori_filter = request.args.get('kategori') # MENANGKAP FILTER KATEGORI SIDEBAR
    search = request.args.get('search', '')
    query = Report.query

    # Logika Filter Kategori (image_6fbd39.png)
    if kategori_filter:
        # Membersihkan tanda '+' dari URL jika ada
        kategori_clean = kategori_filter.replace('+', ' ')
        query = query.filter(Report.kategori == kategori_clean)

    # Logika Filter Status
    if status_filter != 'semua':
        color_map = {'darurat': 'merah', 'proses': 'biru', 'selesai': 'hijau', 'sedang': 'kuning'}
        target_color = color_map.get(status_filter)
        if target_color:
            query = query.filter_by(status_warna=target_color)

    # Logika Pencarian
    if search:
        query = query.filter(or_(
            Report.judul.ilike(f'%{search}%'),
            Report.id.ilike(f'%{search}%'),
            Report.deskripsi.ilike(f'%{search}%')
        ))

    reports_list = query.order_by(Report.created_at.desc()).all()
    return render_template('admin/reports.html', reports=reports_list)


# --- UPDATE PROGRESS (ADMIN FEEDBACK LOGIC) ---
@admin.route('/report/<int:report_id>/update-progress', methods=['POST'])
def update_progress(report_id):
    """Menangani perubahan status dan upload bukti penyelesaian oleh admin"""
    report = Report.query.get_or_404(report_id)
    status_baru = request.form.get('status_warna')
    komentar_admin = request.form.get('komentar_admin')

    if status_baru:
        # Simpan status lama untuk pengecekan poin nanti
        status_lama = report.status_warna
        report.status_warna = status_baru

        if komentar_admin:
            report.komentar_admin = komentar_admin

        # Handle Upload Foto Progress/Selesai
        if 'foto_feedback' in request.files:
            file = request.files['foto_feedback']
            if file and file.filename != '':
                filename = save_feedback_photo(file)
                if status_baru == 'biru':
                    report.foto_proses = filename
                elif status_baru == 'hijau':
                    report.foto_selesai = filename

        # Update Poin User jika Laporan Selesai (Penghargaan Warga)
        if status_baru == 'hijau' and status_lama != 'hijau':
            if report.author:
                report.author.poin_warga = (report.author.poin_warga or 0) + 20
            report.resolved_at = datetime.utcnow()

        db.session.commit()
        flash(f'Laporan #{report_id} diperbarui ke status {status_baru.upper()}!', 'success')

    return redirect(request.referrer or url_for('admin.dashboard'))


# --- USER MANAGEMENT ---
@admin.route('/users')
def users():
    """Melihat daftar warga mahasantri/user yang terdaftar"""
    users_list = User.query.filter(User.role != 'admin').order_by(User.id.desc()).all()
    return render_template('admin/users.html', users=users_list)


# --- VIEW DETAIL ---
@admin.route('/report/<int:report_id>/view')
def view_report(report_id):
    """Melihat detail lengkap satu laporan termasuk koordinat GPS"""
    report = Report.query.get_or_404(report_id)
    return render_template('admin/view_report.html', report=report)


# --- BROADCAST SYSTEM (SIARAN DARURAT) ---
@admin.route('/broadcast', methods=['GET', 'POST'])
def broadcast():
    """Mengirim pesan broadcast bencana/darurat ke seluruh landing page warga"""
    if request.method == 'POST':
        alert = EmergencyAlert(
            tipe_bencana=request.form.get('tipe_bencana'),
            pesan=request.form.get('pesan'),
            wilayah_terdampak=request.form.get('wilayah_terdampak'),
            level_bahaya=request.form.get('level_bahaya'),
            created_at=datetime.utcnow()
        )
        db.session.add(alert)
        db.session.commit()
        flash('Siaran Darurat berhasil dipublikasikan!', 'success')
        return redirect(url_for('admin.broadcast'))

    alerts = EmergencyAlert.query.order_by(EmergencyAlert.created_at.desc()).all()
    return render_template('admin/broadcast.html', alerts=alerts)


# --- EXPORT HANDLERS ---
@admin.route('/export/excel')
def export_excel():
    flash('Fitur Export Excel sedang disiapkan untuk laporan bulanan.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin.route('/export/pdf')
def export_pdf():
    flash('Menghasilkan dokumen PDF Command Center...', 'info')
    return redirect(url_for('admin.dashboard'))