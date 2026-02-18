from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Report, Category, User, EmergencyAlert, Interaction
from app import db
from datetime import datetime
from sqlalchemy import func
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)


# --- FUNGSI HELPER SAVE PHOTO ---
def save_report_photo(file):
    if file and file.filename != '':
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        upload_path = os.path.join('app/static/uploads/reports', filename)
        file.save(upload_path)
        return filename
    return None


# --- LANDING PAGE (SINKRON DENGAN DATA PETA & STATS) ---
@main.route('/')
def index():
    try:
        # Sinkronisasi statistik dengan dashboard admin
        stats = {
            'total_reports': Report.query.count(),
            'total_warga': User.query.filter_by(role='user').count(),
            'darurat': Report.query.filter_by(status_warna='merah').count(),
            'sedang': Report.query.filter_by(status_warna='kuning').count(),
            'selesai': Report.query.filter_by(status_warna='hijau').count()
        }

        # Menarik laporan untuk Pin Peta Landing (Lengkap agar tidak undefined)
        reports_for_map = Report.query.filter(
            Report.latitude.isnot(None),
            Report.longitude.isnot(None),
            Report.is_archived == False
        ).all()

    except Exception:
        stats = {'total_reports': 0, 'total_warga': 0, 'darurat': 0, 'sedang': 0, 'selesai': 0}
        reports_for_map = []

    latest_alert = EmergencyAlert.query.order_by(EmergencyAlert.created_at.desc()).first()

    return render_template('public/landing.html',
                           stats=stats,
                           alert=latest_alert,
                           reports=reports_for_map,
                           now=datetime.now())


# --- FITUR KIRIM LAPORAN (UPDATE 3 FOTO) ---
@main.route('/report/new', methods=['GET', 'POST'])
@login_required
def create_report():
    if request.method == 'POST':
        # Mengambil file dari form (foto_awal wajib, foto_2 & 3 opsional)
        f1 = request.files.get('foto_awal')
        f2 = request.files.get('foto_2')
        f3 = request.files.get('foto_3')

        if not f1:
            flash('Foto utama wajib diunggah!', 'danger')
            return redirect(request.url)

        try:
            new_report = Report(
                judul=request.form.get('judul'),
                deskripsi=request.form.get('deskripsi'),
                latitude=request.form.get('latitude'),
                longitude=request.form.get('longitude'),
                kategori=request.form.get('kategori'),
                user_id=current_user.id,
                status_warna='biru',  # Default awal
                foto_awal=save_report_photo(f1),
                foto_2=save_report_photo(f2),
                foto_3=save_report_photo(f3),
                created_at=datetime.now()
            )
            db.session.add(new_report)
            db.session.commit()
            flash('Laporan berhasil dikirim dan sedang diverifikasi.', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengirim laporan: {str(e)}', 'danger')

    categories = Category.query.all()
    return render_template('user/laporan.html', categories=categories)


# --- FEED PUBLIK & LIVE MAP DATA (SINKRON DENGAN SLIDER) ---
@main.route('/feed')
def feed():
    reports = Report.query.filter_by(is_approved=True, is_archived=False).order_by(Report.created_at.desc()).all()

    # Data Peta Feed (Dibuat lengkap agar popup tidak undefined)
    map_data = [{
        'id': r.id,
        'lat': r.latitude,
        'lng': r.longitude,
        'judul': r.judul or "Laporan",
        'warna': r.status_warna or 'biru',
        'pelapor': r.author.nama if r.author else 'Anonim',
        'kategori': r.kategori or 'Umum'
    } for r in reports if r.latitude and r.longitude]

    return render_template('public/feed.html', reports=reports, map_data=map_data)


# --- DETAIL LAPORAN ---
@main.route('/report/<int:report_id>')
def view_report(report_id):
    report = Report.query.get_or_404(report_id)
    comments = Interaction.query.filter_by(report_id=report_id, tipe='comment').order_by(
        Interaction.created_at.asc()).all()

    user_has_supported = False
    if current_user.is_authenticated:
        existing = Interaction.query.filter_by(report_id=report_id, user_id=current_user.id, tipe='support').first()
        user_has_supported = True if existing else False

    return render_template('public/view_report.html', report=report, comments=comments,
                           user_has_supported=user_has_supported)


# --- FITUR DUKUNG & KOMENTAR (AJAX COMPATIBLE) ---
@main.route('/report/<int:report_id>/support', methods=['POST'])
@login_required
def support_report(report_id):
    report = Report.query.get_or_404(report_id)
    existing = Interaction.query.filter_by(report_id=report_id, user_id=current_user.id, tipe='support').first()

    if not existing:
        try:
            new_support = Interaction(report_id=report_id, user_id=current_user.id, tipe='support')
            db.session.add(new_support)
            report.support_count = (report.support_count or 0) + 1
            db.session.commit()
            return jsonify({'status': 'success', 'count': report.support_count})
        except:
            db.session.rollback()
            return jsonify({'status': 'error'}), 500
    return jsonify({'status': 'error', 'message': 'Sudah didukung'}), 400


@main.route('/report/<int:report_id>/comment', methods=['POST'])
@login_required
def add_comment(report_id):
    konten = request.form.get('konten') or request.form.get('comment')
    if not konten:
        return jsonify({'status': 'error', 'message': 'Komentar kosong'}), 400

    try:
        new_comment = Interaction(report_id=report_id, user_id=current_user.id, tipe='comment', konten=konten.strip())
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Terkirim'}), 200
    except:
        db.session.rollback()
        return jsonify({'status': 'error'}), 500


# --- DASHBOARD MULTI-ROLE ---
@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        stats = {
            'total_reports': Report.query.count(),
            'darurat': Report.query.filter_by(status_warna='merah').count(),
            'sedang': Report.query.filter_by(status_warna='kuning').count(),
            'selesai': Report.query.filter_by(status_warna='hijau').count(),
            'total_warga': User.query.filter(User.role != 'admin').count()
        }
        recent_reports = Report.query.order_by(Report.created_at.desc()).limit(10).all()
        return render_template('admin/dashboard.html', stats=stats, recent_reports=recent_reports, now=datetime.now())

    user_stats = {
        'total': Report.query.filter_by(user_id=current_user.id).count(),
        'proses': Report.query.filter_by(user_id=current_user.id).filter(
            Report.status_warna.in_(['merah', 'kuning', 'biru'])).count(),
        'selesai': Report.query.filter_by(user_id=current_user.id, status_warna='hijau').count(),
        'poin': current_user.poin_warga or 0
    }
    my_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
    return render_template('user/dashboard.html', stats=user_stats, reports=my_reports)


# --- API DATA PETA (SINKRONISASI REAL-TIME) ---
@main.route('/api/map-markers')
def map_markers():
    reports = Report.query.filter(Report.latitude.isnot(None), Report.is_archived == False).all()
    return jsonify([{
        'id': r.id,
        'judul': r.judul or "Tanpa Judul",
        'lat': r.latitude,
        'lng': r.longitude,
        'warna': r.status_warna or 'biru',
        'status': 'Selesai' if r.status_warna == 'hijau' else 'Proses',
        'kategori': r.kategori or 'Umum',
        'pelapor': r.author.nama if r.author else 'Anonim',
        'foto': r.foto_awal,
        'created_at': r.created_at.strftime('%d/%m/%Y %H:%M') if r.created_at else ''
    } for r in reports])