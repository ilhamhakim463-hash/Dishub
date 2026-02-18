from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.blueprints.admin import admin
from app.models import User, Report, EmergencyAlert, Category, Interaction
from app import db
from sqlalchemy import func, or_, extract
from datetime import datetime, timedelta, time
import os
from werkzeug.utils import secure_filename


# --- HELPER: SAVE UPLOAD ---
def save_feedback_photo(file):
    """Fungsi pembantu untuk menyimpan foto progres/selesai dari admin"""
    if file:
        filename = secure_filename(f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        upload_folder = os.path.join(current_app.root_path, 'static/uploads/reports')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file.save(os.path.join(upload_folder, filename))
        return filename
    return None


# --- CONTEXT PROCESSOR (Navigasi Sidebar) ---
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
    if current_user.role != 'admin':
        flash('Akses ditolak! Anda bukan administrator.', 'danger')
        return redirect(url_for('main.feed'))


# --- DASHBOARD & STATISTIK (FIXED & FULL LOGIC) ---
@admin.route('/dashboard')
def dashboard():
    """
    Menghitung statistik utama untuk Command Center.
    Sinkronisasi otomatis dengan card: Total, SLA Overdue, Sedang, dan Tuntas.
    """
    reports_query = Report.query

    # Sinkronisasi Statistik Utama agar muncul di Card Dashboard
    stats = {
        'total_reports': reports_query.count(),
        'darurat': reports_query.filter_by(status_warna='merah').count(),  # Map ke Card SLA Overdue
        'sedang': reports_query.filter_by(status_warna='kuning').count(),  # Map ke Card Urgency Sedang
        'proses': reports_query.filter_by(status_warna='biru').count(),
        'selesai': reports_query.filter_by(status_warna='hijau').count(),  # Map ke Card Tuntas (Selesai)
        'total_warga': User.query.filter_by(role='user').count()
    }

    # Data grafik mingguan (7 hari terakhir)
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
    """Endpoint API untuk Leaflet.js dengan perbaikan data agar tidak 'undefined' di popup"""
    reports = Report.query.filter(
        Report.latitude.isnot(None),
        Report.longitude.isnot(None),
        Report.is_archived == False
    ).all()

    data = []
    for r in reports:
        # Penentuan label urgensi untuk Popup
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
            'status_warna': r.status_warna or 'hijau',
            'urgensi_label': urgensi_text,
            'foto': r.foto_awal if r.foto_awal else None,
            'pelapor': r.author.nama if r.author else 'Anonim',
            'kategori': r.kategori or 'Umum',
            'url_detail': url_for('admin.view_report', report_id=r.id),
            'created_at': r.created_at.strftime('%d/%m/%Y %H:%M')
        })
    return jsonify(data)


# --- LOG LAPORAN ---
@admin.route('/reports')
def reports():
    """Manajemen daftar laporan dengan filter status dan pencarian"""
    status_filter = request.args.get('status', 'Semua').lower()
    search = request.args.get('search', '')
    query = Report.query

    if status_filter != 'semua':
        color_map = {'darurat': 'merah', 'proses': 'biru', 'selesai': 'hijau', 'sedang': 'kuning'}
        target_color = color_map.get(status_filter)
        if target_color:
            query = query.filter_by(status_warna=target_color)

    if search:
        query = query.filter(or_(
            Report.judul.ilike(f'%{search}%'),
            Report.id.ilike(f'%{search}%'),
            Report.alamat_manual.ilike(f'%{search}%')
        ))

    reports_list = query.order_by(Report.created_at.desc()).all()
    return render_template('admin/reports.html', reports=reports_list)


# --- UPDATE PROGRESS ---
@admin.route('/report/<int:report_id>/update-progress', methods=['POST'])
def update_progress(report_id):
    """Merubah status laporan dan mengunggah bukti pengerjaan"""
    report = Report.query.get_or_404(report_id)
    status_baru = request.form.get('status_warna')
    komentar_admin = request.form.get('komentar_admin')

    if status_baru:
        report.status_warna = status_baru
        if komentar_admin:
            report.komentar_admin = komentar_admin

        if 'foto_feedback' in request.files:
            file = request.files['foto_feedback']
            if file and file.filename != '':
                filename = save_feedback_photo(file)
                if status_baru == 'biru':
                    report.foto_proses = filename
                elif status_baru == 'hijau':
                    report.foto_selesai = filename

        # Sinkronisasi Label Database
        labels = {'merah': 'DARURAT', 'kuning': 'SEDANG', 'hijau': 'SUKSES', 'biru': 'DIPROSES'}
        report.status_label = labels.get(status_baru, 'PENDING')

        if status_baru == 'hijau':
            report.resolved_at = datetime.utcnow()

        db.session.commit()
        flash(f'Status Laporan #{report_id} berhasil diperbarui!', 'success')

    return redirect(request.referrer or url_for('admin.dashboard'))


# --- USER MANAGEMENT ---
@admin.route('/users')
def users():
    users_list = User.query.filter(User.role != 'admin').order_by(User.id.desc()).all()
    return render_template('admin/users.html', users=users_list)


# --- VIEW DETAIL ---
@admin.route('/report/<int:report_id>/view')
def view_report(report_id):
    report = Report.query.get_or_404(report_id)
    return render_template('admin/view_report.html', report=report)


# --- BROADCAST SYSTEM ---
@admin.route('/broadcast', methods=['GET', 'POST'])
def broadcast():
    if request.method == 'POST':
        alert = EmergencyAlert(
            tipe_bencana=request.form.get('tipe_bencana'),
            pesan=request.form.get('pesan'),
            wilayah_terdampak=request.form.get('wilayah_terdampak'),
            level_bahaya=request.form.get('level_bahaya')
        )
        db.session.add(alert)
        db.session.commit()
        flash('Siaran Darurat berhasil disebarluaskan!', 'success')
        return redirect(url_for('admin.broadcast'))

    alerts = EmergencyAlert.query.order_by(EmergencyAlert.created_at.desc()).all()
    return render_template('admin/broadcast.html', alerts=alerts)


# --- EXPORT HANDLERS ---
@admin.route('/export/excel')
def export_excel():
    flash('Fitur Export Excel sedang disiapkan.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin.route('/export/pdf')
def export_pdf():
    flash('Menghasilkan dokumen PDF...', 'info')
    return redirect(url_for('admin.dashboard'))