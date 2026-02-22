from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
import random
import pandas as pd
from io import BytesIO

# Import untuk PDF
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

admin = Blueprint('admin', __name__)


# --- DECORATOR ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


# --- CONTEXT PROCESSOR ---
@admin.app_context_processor
def inject_sidebar_categories():
    from app.models import Category
    try:
        all_cats = Category.query.order_by(Category.name.asc()).all()
        return dict(sidebar_categories=all_cats)
    except Exception:
        return dict(sidebar_categories=[])


# --- DASHBOARD ---
@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    from app.models import Report, User
    from sqlalchemy import func

    f_kategori = request.args.get('kategori', '').strip()
    f_status = request.args.get('status', '').strip()

    query = Report.query.filter_by(is_archived=False)
    if f_kategori and f_kategori != 'Semua Kategori':
        query = query.filter(Report.kategori.ilike(f_kategori))
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

    archived_count = Report.query.filter_by(is_archived=True).count()

    stats = {
        'total_reports': Report.query.filter_by(is_archived=False).count(),
        'darurat_reports': Report.query.filter_by(status_warna='merah', is_archived=False).count(),
        'biasa_reports': Report.query.filter(Report.status_warna != 'merah', Report.is_archived == False).count(),
        'selesai_reports': Report.query.filter_by(status_warna='biru', is_archived=False).count(),
        'total_users': User.query.filter_by(role='user').count(),
        'sla_warning': sla_overdue,
        'archived_count': archived_count
    }

    # Logika Grafik
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
                           all_reports=all_reports, weekly_data=weekly_data, days=days, now=datetime.utcnow())


# --- API MAPS ---
@admin.route('/api/reports-map-data')
def reports_map_data():
    from app.models import Report
    reports = Report.query.filter_by(is_archived=False).all()

    data = []
    for r in reports:
        try:
            lat_raw = r.latitude
            lng_raw = r.longitude

            if lat_raw in [None, 0, "0", ""] or lng_raw in [None, 0, "0", ""]:
                lat = -7.5460 + random.uniform(-0.01, 0.01)
                lng = 112.2330 + random.uniform(-0.01, 0.01)
            else:
                lat = float(lat_raw)
                lng = float(lng_raw)

            tgl_str = r.created_at.strftime('%d/%m/%Y %H:%M') if r.created_at else "-"

            data.append({
                'id': r.id,
                'judul': r.judul or f"Laporan #{r.id}",
                'lat': lat,
                'lng': lng,
                'status_warna': (r.status_warna or 'biru').lower(),
                'url_detail': url_for('admin.view_report', report_id=r.id),
                'foto': r.foto_awal if hasattr(r, 'foto_awal') else None,
                'created_at': tgl_str
            })
        except Exception:
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
    import re
    if request.method == 'POST':
        nama = request.form.get('nama')
        if nama:
            slug = re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', nama).strip().lower())
            if not Category.query.filter_by(slug=slug).first():
                db.session.add(Category(name=nama, slug=slug))
                db.session.commit()
                flash('Kategori ditambahkan!', 'success')
        return redirect(url_for('admin.master_kategori'))
    cats = Category.query.order_by(Category.name.asc()).all()
    return render_template('admin/categories.html', categories=cats, now=datetime.utcnow())


@admin.route('/category/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    from app import db
    from app.models import Category
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Kategori dihapus.', 'success')
    return redirect(url_for('admin.master_kategori'))


# --- REPORTS & ARCHIVE ---
@admin.route('/reports')
@login_required
@admin_required
def reports():
    from app.models import Report, Category
    page = request.args.get('page', 1, type=int)
    query = Report.query.filter_by(is_archived=False)
    pagination = query.order_by(Report.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
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


# --- MODERASI & UPDATE ---
@admin.route('/report/<int:report_id>')
@login_required
@admin_required
def view_report(report_id):
    from app.models import Report
    return render_template('admin/view_report.html', report=Report.query.get_or_404(report_id), now=datetime.utcnow())


@admin.route('/report/<int:report_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_report(report_id):
    from app import db
    from app.models import Report, User
    report = Report.query.get_or_404(report_id)
    user = User.query.get(report.user_id)
    report.is_approved = True
    report.approved_at = datetime.utcnow()
    if report.status_warna in ['abu-abu', 'abu', None]:
        report.status_warna = 'merah'
    if user:
        user.poin_warga += 10
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
    if user:
        user.poin_warga -= 50
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
    if new_status:
        report.status_warna = new_status
        if catatan:
            report.deskripsi += f"\n\n[Catatan Admin] {catatan}"
        if new_status == 'biru':
            report.resolved_at = datetime.utcnow()
        db.session.commit()
        flash('Status diperbarui!', 'success')
    return redirect(url_for('admin.view_report', report_id=report.id))


@admin.route('/report/<int:report_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_report(report_id):
    from app import db
    from app.models import Report
    db.session.delete(Report.query.get_or_404(report_id))
    db.session.commit()
    flash('Laporan dihapus.', 'success')
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
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.nama} dihapus.', 'success')
    return redirect(url_for('admin.users'))


# --- RESET PASSWORD USER ---
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
        # SINKRONISASI: Menggunakan password_hash sesuai models.py
        user.password_hash = generate_password_hash(new_password)
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
    df = pd.DataFrame([{'ID': r.id, 'Judul': r.judul, 'Status': r.status_warna} for r in Report.query.all()])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="Laporan.xlsx", as_attachment=True)


@admin.route('/export/pdf')
@login_required
@admin_required
def export_pdf():
    from app.models import Report
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(letter))
    data = [['ID', 'Judul', 'Kategori', 'Status']]
    for r in Report.query.all():
        data.append([r.id, (r.judul[:20] if r.judul else '-'), r.kategori, r.status_warna])
    t = Table(data)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    doc.build([Paragraph("REKAP LAPORAN", getSampleStyleSheet()['Title']), t])
    output.seek(0)
    return send_file(output, download_name="Laporan.pdf", as_attachment=True)


# --- BROADCAST & PROFILE ---
@admin.route('/broadcast', methods=['GET', 'POST'])
@login_required
@admin_required
def broadcast():
    from app import db
    from app.models import EmergencyAlert
    if request.method == 'POST':
        db.session.add(EmergencyAlert(
            tipe_bencana=request.form.get('tipe_bencana'),
            pesan=request.form.get('pesan'),
            wilayah_terdampak=request.form.get('wilayah_terdampak'),
            level_bahaya=request.form.get('level_bahaya')
        ))
        db.session.commit()
        flash('Broadcast terkirim!', 'success')
    return render_template('admin/broadcast.html', now=datetime.utcnow())


@admin.route('/profile')
@login_required
@admin_required
def profile():
    return render_template('admin/profile.html', now=datetime.utcnow())


# --- EDIT PROFILE ADMIN ---
@admin.route('/profile/edit', methods=['POST'])
@login_required
@admin_required
def edit_profile():
    from app import db
    from app.models import User

    user = User.query.get(current_user.id)
    if not user:
        abort(404)

    nama = request.form.get('nama')
    email = request.form.get('email')
    password = request.form.get('password')

    if nama: user.nama = nama
    if email: user.email = email

    if password:
        # SINKRONISASI: Menggunakan password_hash
        user.password_hash = generate_password_hash(password)

    file = request.files.get('foto')
    if file and file.filename != '':
        filename = secure_filename(f"admin_{user.id}_{file.filename}")
        upload_path = os.path.join('app', 'static', 'uploads', 'profiles')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        file.save(os.path.join(upload_path, filename))
        # SINKRONISASI: Menggunakan foto_profil sesuai models.py
        user.foto_profil = filename

    db.session.commit()
    flash('Profil berhasil diperbarui!', 'success')
    return redirect(url_for('admin.profile'))