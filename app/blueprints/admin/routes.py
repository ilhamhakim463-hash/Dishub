from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, jsonify, send_file, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
import random
import pandas as pd
from io import BytesIO
import re

# Import untuk PDF
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

admin = Blueprint('admin', __name__)

# --- VARIABEL GLOBAL UNTUK RUNNING TEXT ---
latest_running_text = "Selamat Datang di Layanan LaporPak! Dishub Jombang"


# --- DECORATOR ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


# --- CONTEXT PROCESSOR (SINKRONISASI DATA KE SEMUA HALAMAN) ---
@admin.app_context_processor
def inject_global_data():
    from app.models import Category, Report, User
    try:
        all_cats = Category.query.order_by(Category.name.asc()).all()

        # Hitung statistik secara global agar sama di Landing Page & Admin
        total_lap = Report.query.filter_by(is_archived=False).count()
        total_sel = Report.query.filter_by(status_warna='biru', is_archived=False).count()
        total_usr = User.query.filter_by(role='user').count()

        return dict(
            sidebar_categories=all_cats,
            running_text=latest_running_text,
            global_total_laporan=total_lap,
            global_total_selesai=total_sel,
            global_total_warga=total_usr
        )
    except Exception:
        return dict(
            sidebar_categories=[],
            running_text=latest_running_text,
            global_total_laporan=0,
            global_total_selesai=0,
            global_total_warga=0
        )


# --- DASHBOARD ---
@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    from app.models import Report, User, Category
    from sqlalchemy import func

    f_kategori = request.args.get('kategori', '').strip()
    f_status = request.args.get('status', '').strip()

    db_categories = Category.query.order_by(Category.name.asc()).all()
    query = Report.query.filter_by(is_archived=False)

    if f_kategori and f_kategori != 'Semua Kategori':
        query = query.filter(Report.kategori == f_kategori)
    if f_status and f_status != 'Semua Status':
        query = query.filter_by(status_warna=f_status)

    all_reports = query.order_by(Report.created_at.desc()).all()
    recent_reports = all_reports[:10]

    dua_jam_lalu = datetime.utcnow() - timedelta(hours=2)
    sla_overdue = Report.query.filter(
        Report.status_warna == 'merah',
        Report.created_at < dua_jam_lalu,
        Report.is_archived == False
    ).count()

    # Statistik untuk Dashboard Admin
    stats = {
        'total_reports': Report.query.filter_by(is_archived=False).count(),
        'darurat_reports': Report.query.filter_by(status_warna='merah', is_archived=False).count(),
        'biasa_reports': Report.query.filter(Report.status_warna != 'merah', Report.is_archived == False).count(),
        'selesai_reports': Report.query.filter_by(status_warna='biru', is_archived=False).count(),
        'total_users': User.query.filter_by(role='user').count(),
        'sla_warning': sla_overdue,
        'archived_count': Report.query.filter_by(is_archived=True).count()
    }

    weekly_data, days = [], []
    try:
        for i in range(6, -1, -1):
            target_date = (datetime.utcnow() - timedelta(days=i)).date()
            count = Report.query.filter(func.date(Report.created_at) == target_date).count()
            weekly_data.append(count)
            day_labels = {'Mon': 'Sen', 'Tue': 'Sel', 'Wed': 'Rab', 'Thu': 'Kam', 'Fri': 'Jum', 'Sat': 'Sab',
                          'Sun': 'Min'}
            raw_day = (datetime.utcnow() - timedelta(days=i)).strftime('%a')
            days.append(day_labels.get(raw_day, raw_day))
    except Exception:
        weekly_data, days = [0] * 7, ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']

    return render_template('admin/dashboard.html', stats=stats, reports=recent_reports, recent_reports=recent_reports,
                           all_reports=all_reports, categories=db_categories, weekly_data=weekly_data, days=days,
                           now=datetime.utcnow())


# --- API MAPS ---
@admin.route('/api/reports-map-data')
def reports_map_data():
    from app.models import Report
    reports = Report.query.filter_by(is_archived=False).all()
    data = []
    for r in reports:
        try:
            lat = float(r.latitude) if r.latitude else -7.5460 + random.uniform(-0.01, 0.01)
            lng = float(r.longitude) if r.longitude else 112.2330 + random.uniform(-0.01, 0.01)
            data.append({
                'id': r.id,
                'judul': r.judul or f"Laporan #{r.id}",
                'lat': lat, 'lng': lng,
                'status_warna': (r.status_warna or 'biru').lower(),
                'url_detail': url_for('main.view_report', report_id=r.id),
                'foto': r.foto_awal,
                'created_at': r.created_at.strftime('%d/%m/%Y %H:%M')
            })
        except:
            continue
    return jsonify(data)


# --- CATEGORY MANAGEMENT ---
@admin.route('/categories', methods=['GET', 'POST'])
@admin.route('/master-kategori', endpoint='master_kategori', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_categories():
    from app import db
    from app.models import Category
    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        if nama:
            slug = re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', nama).lower())
            if not Category.query.filter((Category.slug == slug) | (Category.name == nama)).first():
                db.session.add(Category(name=nama, slug=slug))
                db.session.commit()
                flash(f'Kategori "{nama}" berhasil ditambahkan!', 'success')
            else:
                flash(f'Kategori "{nama}" sudah ada.', 'warning')
        else:
            flash('Nama kategori tidak boleh kosong.', 'danger')
        return redirect(url_for('admin.master_kategori'))
    return render_template('admin/categories.html', categories=Category.query.order_by(Category.name.asc()).all(),
                           now=datetime.utcnow())


@admin.route('/category/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    from app import db
    from app.models import Category
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Kategori berhasil dihapus.', 'success')
    return redirect(url_for('admin.master_kategori'))


# --- REPORTS & ARCHIVE ---
@admin.route('/reports')
@login_required
@admin_required
def reports():
    from app.models import Report, Category
    page = request.args.get('page', 1, type=int)
    pagination = Report.query.filter_by(is_archived=False).order_by(Report.created_at.desc()).paginate(page=page,
                                                                                                       per_page=10,
                                                                                                       error_out=False)
    arch_count = Report.query.filter_by(is_archived=True).count()
    return render_template('admin/reports.html', reports=pagination.items, pagination=pagination,
                           categories=Category.query.all(), arch_count=arch_count, now=datetime.utcnow())


@admin.route('/reports/archived')
@login_required
@admin_required
def archived_reports():
    from app.models import Report
    page = request.args.get('page', 1, type=int)
    pagination = Report.query.filter_by(is_archived=True).order_by(Report.created_at.desc()).paginate(page=page,
                                                                                                      per_page=10,
                                                                                                      error_out=False)
    return render_template('admin/archived_reports.html', reports=pagination.items, pagination=pagination,
                           now=datetime.utcnow())


@admin.route('/report/<int:report_id>/archive/<string:action>', methods=['POST'])
@login_required
@admin_required
def toggle_archive(report_id, action):
    from app import db
    from app.models import Report
    report = Report.query.get_or_404(report_id)
    report.is_archived = (action == 'archive')
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'Berhasil di-{action}'})


@admin.route('/report/<int:report_id>')
@login_required
@admin_required
def view_report(report_id):
    from app.models import Report, Interaction
    report = Report.query.get_or_404(report_id)
    comments = Interaction.query.filter_by(report_id=report_id).order_by(Interaction.created_at.desc()).all()
    return render_template('admin/view_report.html', report=report, comments=comments, now=datetime.utcnow())


@admin.route('/report/<int:report_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_report(report_id):
    from app import db
    from app.models import Report, User
    report = Report.query.get_or_404(report_id)
    report.is_approved = True
    report.approved_at = datetime.utcnow()
    if report.status_warna in ['abu-abu', 'abu', None]: report.status_warna = 'merah'
    user = User.query.get(report.user_id)
    if user: user.poin_warga += 10
    db.session.commit()
    return jsonify({'status': 'success'})


@admin.route('/report/<int:report_id>/reject-hoax', methods=['POST'])
@login_required
@admin_required
def reject_hoax(report_id):
    from app import db
    from app.models import Report, User
    report = Report.query.get_or_404(report_id)
    user = User.query.get(report.user_id)
    if user: user.poin_warga -= 50
    db.session.delete(report)
    db.session.commit()
    return jsonify({'status': 'success'})


@admin.route('/report/update/<int:report_id>', methods=['POST'])
@login_required
@admin_required
def update_status(report_id):
    from app import db
    from app.models import Report
    report = Report.query.get_or_404(report_id)
    new_status = request.form.get('status_warna')
    catatan = request.form.get('catatan_admin')
    file = request.files.get('bukti_foto')

    if new_status:
        report.status_warna = new_status
        if catatan:
            report.komentar_admin = catatan

        if file and file.filename != '':
            filename = secure_filename(f"update_{report.id}_{file.filename}")
            upload_path = os.path.join('app', 'static', 'uploads', 'reports')
            if not os.path.exists(upload_path): os.makedirs(upload_path)
            file.save(os.path.join(upload_path, filename))

            if new_status == 'biru':
                report.foto_selesai = filename
                report.resolved_at = datetime.utcnow()
            else:
                report.foto_proses = filename

        db.session.commit()
        flash('Status & Bukti Penanganan diperbarui!', 'success')
    return redirect(url_for('admin.view_report', report_id=report.id))


@admin.route('/report/<int:report_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_report(report_id):
    from app import db
    from app.models import Report
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    flash('Laporan berhasil dihapus.', 'success')
    return redirect(url_for('admin.reports'))


# --- USER MANAGEMENT ---
@admin.route('/users')
@login_required
@admin_required
def users():
    from app.models import User
    all_users = User.query.filter_by(role='user').order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users, now=datetime.utcnow())


@admin.route('/user/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    from app import db
    from app.models import User
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': user.is_active})


@admin.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    from app import db
    from app.models import User
    user = User.query.get_or_404(user_id)
    nama_user = user.nama
    db.session.delete(user)
    db.session.commit()
    flash(f'User {nama_user} berhasil dihapus.', 'success')
    return redirect(url_for('admin.users'))


@admin.route('/user/reset-password/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reset_password_user(user_id):
    from app import db
    from app.models import User
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('password')
    if not new_password or len(new_password) < 6:
        return jsonify({'status': 'error', 'message': 'Password minimal 6 karakter.'}), 400
    try:
        user.set_password(new_password)
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Password untuk {user.nama} berhasil direset.'})
    except Exception:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Gagal mereset password.'}), 500


# --- EXPORT ---
@admin.route('/export/excel')
@login_required
@admin_required
def export_excel():
    from app.models import Report
    data = [{'ID': r.id, 'Judul': r.judul, 'Kategori': r.kategori, 'Status': r.status_warna, 'Tanggal': r.created_at}
            for r in Report.query.all()]
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame(data).to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name=f"Rekap_{datetime.now().strftime('%Y%m%d')}.xlsx", as_attachment=True)


@admin.route('/export/pdf')
@login_required
@admin_required
def export_pdf():
    from app.models import Report
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(letter))
    data = [['ID', 'Judul Laporan', 'Kategori', 'Status', 'Tanggal']]
    for r in Report.query.all():
        data.append([
            r.id,
            (r.judul[:30] + '..') if r.judul and len(r.judul) > 30 else (r.judul or '-'),
            r.kategori or '-',
            (r.status_warna or 'pending').upper(),
            r.created_at.strftime('%d/%m/%Y') if r.created_at else '-'
        ])
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    doc.build([Paragraph("REKAP LAPORAN SISTEM LAPORPAK", getSampleStyleSheet()['Title']), t])
    output.seek(0)
    return send_file(output, download_name=f"Rekap_{datetime.now().strftime('%Y%m%d')}.pdf", as_attachment=True)


# --- BROADCAST & RUNNING TEXT ---
@admin.route('/broadcast', methods=['GET', 'POST'])
@login_required
@admin_required
def broadcast():
    from app import db
    from app.models import EmergencyAlert
    global latest_running_text

    if request.method == 'POST':
        tipe = request.form.get('tipe_bencana')
        wilayah = request.form.get('wilayah_terdampak')
        pesan_tambahan = request.form.get('pesan')

        latest_running_text = f"Peringatan Dini: {tipe} di wilayah {wilayah}. Pesan: {pesan_tambahan}"

        new_alert = EmergencyAlert(
            tipe_bencana=tipe,
            pesan=pesan_tambahan,
            wilayah_terdampak=wilayah,
            level_bahaya=request.form.get('level_bahaya') or 'bahaya',
            created_at=datetime.utcnow()
        )
        db.session.add(new_alert)
        db.session.commit()

        flash('Peringatan Dini Berhasil Disiarkan dan Navbar telah diperbarui!', 'success')
        return redirect(url_for('admin.broadcast'))

    return render_template('admin/broadcast.html', now=datetime.utcnow())


@admin.route('/profile')
@login_required
@admin_required
def profile():
    return render_template('admin/profile.html', now=datetime.utcnow())


@admin.route('/profile/edit', methods=['POST'])
@login_required
@admin_required
def edit_profile():
    from app import db
    from app.models import User
    user = User.query.get(current_user.id)
    user.nama = request.form.get('nama') or user.nama
    user.email = request.form.get('email') or user.email
    if request.form.get('password'): user.set_password(request.form.get('password'))

    file = request.files.get('foto')
    if file and file.filename != '':
        filename = secure_filename(f"admin_{user.id}_{file.filename}")
        file.save(os.path.join('app', 'static', 'uploads', 'profiles', filename))
        user.foto_profil = filename

    db.session.commit()
    flash('Profil diperbarui!', 'success')
    return redirect(url_for('admin.profile'))