from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
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


# --- CONTEXT PROCESSOR (Fitur Sinkronisasi Sidebar Otomatis) ---
@admin.app_context_processor
def inject_sidebar_categories():
    from app.models import Category
    try:
        # Menggunakan .name sesuai struktur model Anda
        all_cats = Category.query.order_by(Category.name.asc()).all()
        return dict(sidebar_categories=all_cats)
    except Exception:
        return dict(sidebar_categories=[])


# --- DASHBOARD SECTION ---
@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    from app.models import Report, User
    from sqlalchemy import func

    f_kategori = request.args.get('kategori', '').strip()
    f_status = request.args.get('status', '').strip()

    # Query utama untuk Dashboard (Hanya tampilkan yang TIDAK diarsip)
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

    # Hitung jumlah arsip untuk badge di menu
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

    # --- LOGIKA SINKRONISASI GRAFIK ---
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

    monthly_data = []
    current_year = datetime.utcnow().year
    try:
        for month in range(1, 13):
            count = Report.query.filter(func.extract('month', Report.created_at) == month,
                                        func.extract('year', Report.created_at) == current_year).count()
            monthly_data.append(count)
    except Exception:
        monthly_data = [0] * 12
    monthly_labels = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

    yearly_data = []
    yearly_labels = [str(y) for y in range(current_year - 4, current_year + 1)]
    try:
        for year in yearly_labels:
            count = Report.query.filter(func.extract('year', Report.created_at) == int(year)).count()
            yearly_data.append(count)
    except Exception:
        yearly_data = [0] * 5

    return render_template('admin/dashboard.html',
                           stats=stats,
                           reports=recent_reports,
                           recent_reports=recent_reports,
                           all_reports=all_reports,
                           weekly_data=weekly_data,
                           days=days,
                           monthly_data=monthly_data,
                           monthly_labels=monthly_labels,
                           yearly_data=yearly_data,
                           yearly_labels=yearly_labels,
                           now=datetime.utcnow())


# --- MANAJEMEN MASTER KATEGORI ---
@admin.route('/categories', methods=['GET', 'POST'])
@admin.route('/master-kategori', endpoint='master_kategori', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_categories():
    from app import db
    from app.models import Category
    import re  # Tambahkan import re untuk membuat slug

    if request.method == 'POST':
        nama_kategori = request.form.get('nama')

        if nama_kategori:
            # OTOMATISASI SLUG: Mengubah nama menjadi format slug (lowercase & ganti spasi jadi dash)
            slug_kategori = re.sub(r'[^\w\s-]', '', nama_kategori).strip().lower()
            slug_kategori = re.sub(r'[-\s]+', '-', slug_kategori)

            # Cek apakah slug sudah ada untuk menghindari IntegrityError (Duplicate)
            existing_cat = Category.query.filter_by(slug=slug_kategori).first()
            if existing_cat:
                flash(f'Kategori atau slug "{nama_kategori}" sudah ada!', 'danger')
            else:
                # Masukkan name dan slug ke database
                new_cat = Category(name=nama_kategori, slug=slug_kategori)
                db.session.add(new_cat)
                db.session.commit()
                flash('Kategori baru berhasil ditambahkan!', 'success')

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
    flash('Kategori berhasil dihapus.', 'success')
    return redirect(url_for('admin.master_kategori'))


# --- BROADCAST SYSTEM (EWS) ---
@admin.route('/broadcast', methods=['GET', 'POST'])
@login_required
@admin_required
def broadcast():
    from app import db
    from app.models import User, EmergencyAlert

    if request.method == 'POST':
        tipe = request.form.get('tipe_bencana')
        wilayah = request.form.get('wilayah_terdampak')
        pesan = request.form.get('pesan')
        level = request.form.get('level_bahaya')

        alert = EmergencyAlert(tipe_bencana=tipe, pesan=pesan, wilayah_terdampak=wilayah, level_bahaya=level)
        db.session.add(alert)

        if wilayah == "Semua" or wilayah == "Semua Wilayah":
            targets = User.query.filter_by(role='user', is_active=True).all()
        else:
            targets = User.query.filter_by(kecamatan=wilayah, role='user', is_active=True).all()

        db.session.commit()
        flash(f'Siaran darurat "{tipe}" berhasil dikirim ke {len(targets)} warga!', 'success')
        return redirect(url_for('admin.broadcast'))

    return render_template('admin/broadcast.html', now=datetime.utcnow())


# --- USER MANAGEMENT SECTION ---
@admin.route('/users')
@login_required
@admin_required
def users():
    from app.models import User
    search = request.args.get('search', '').strip()
    query = User.query.filter_by(role='user')
    if search:
        query = query.filter((User.nama.ilike(f'%{search}%')) | (User.nik.ilike(f'%{search}%')))

    all_users = query.order_by(User.created_at.desc()).all()
    stats = {'total_warga': User.query.filter_by(role='user').count()}
    return render_template('admin/users.html', users=all_users, stats=stats, now=datetime.utcnow())


@admin.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    from app import db
    from app.models import User
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.nama} berhasil dihapus.', 'success')
    return redirect(url_for('admin.users'))


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


@admin.route('/user/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password_user(user_id):
    from app import db
    from app.models import User
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    if not new_password:
        return jsonify({'status': 'error', 'message': 'Password baru tidak boleh kosong'}), 400
    try:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Password {user.nama} berhasil direset.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# --- REPORT MANAGEMENT ---
@admin.route('/reports')
@login_required
@admin_required
def reports():
    from app.models import Report, Category
    page = request.args.get('page', 1, type=int)
    f_kategori = request.args.get('kategori', '').strip()
    f_status = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()

    query = Report.query.filter_by(is_archived=False)
    if f_kategori and f_kategori != 'Semua Kategori':
        query = query.filter(Report.kategori.ilike(f_kategori))
    if f_status and f_status != 'Semua Status':
        query = query.filter_by(status_warna=f_status)
    if search:
        query = query.filter(Report.judul.ilike(f'%{search}%'))

    pagination = query.order_by(Report.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    # Ambil semua kategori untuk dropdown di halaman reports
    categories = Category.query.order_by(Category.name.asc()).all()

    clean_args = request.args.to_dict()
    clean_args.pop('page', None)

    arch_count = Report.query.filter_by(is_archived=True).count()

    return render_template('admin/reports.html',
                           reports=pagination.items,
                           pagination=pagination,
                           categories=categories,
                           request_args=clean_args,
                           arch_count=arch_count,
                           now=datetime.utcnow())


# --- FITUR ARSIP & UNARCHIVE ---
@admin.route('/report/<int:report_id>/archive/<string:action>', methods=['POST'])
@login_required
@admin_required
def toggle_archive(report_id, action):
    from app import db
    from app.models import Report
    report = Report.query.get_or_404(report_id)
    report.is_archived = (action == 'archive')
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'Laporan berhasil di-{action}'})


@admin.route('/reports/archived')
@login_required
@admin_required
def archived_reports():
    from app.models import Report
    page = request.args.get('page', 1, type=int)
    pagination = Report.query.filter_by(is_archived=True).order_by(Report.created_at.desc()).paginate(page=page,
                                                                                                      per_page=10,
                                                                                                      error_out=False)
    clean_args = request.args.to_dict()
    clean_args.pop('page', None)

    return render_template('admin/archived_reports.html', reports=pagination.items, pagination=pagination,
                           request_args=clean_args, now=datetime.utcnow())


# --- DETAIL & MODERASI LAPORAN ---
@admin.route('/report/<int:report_id>')
@login_required
@admin_required
def view_report(report_id):
    from app.models import Report
    report = Report.query.get_or_404(report_id)
    return render_template('admin/view_report.html', report=report, now=datetime.utcnow())


@admin.route('/report/<int:report_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_report(report_id):
    from app import db
    from app.models import Report, User
    report = Report.query.get_or_404(report_id)
    user = User.query.get(report.user_id)
    try:
        report.is_approved = True
        report.approved_at = datetime.utcnow()
        if report.status_warna in ['abu-abu', 'abu', None]:
            report.status_warna = 'merah'
        if user:
            user.poin_warga += 10
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@admin.route('/report/<int:report_id>/reject-hoax', methods=['POST'])
@login_required
@admin_required
def reject_hoax(report_id):
    from app import db
    from app.models import Report, User
    report = Report.query.get_or_404(report_id)
    user = User.query.get(report.user_id)
    try:
        if user:
            user.poin_warga -= 50
        db.session.delete(report)
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


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
            report.deskripsi += f"\n\n[Catatan Admin {datetime.now().strftime('%d/%m/%Y %H:%M')}] {catatan}"
        if new_status == 'biru':
            report.resolved_at = datetime.utcnow()

        if 'bukti_foto' in request.files:
            file = request.files['bukti_foto']
            if file and file.filename != '':
                filename = secure_filename(f"selesai_{report.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                path = os.path.join('app/static/uploads/reports')
                os.makedirs(path, exist_ok=True)
                file.save(os.path.join(path, filename))
                report.foto_selesai = filename

        db.session.commit()
        flash('Status laporan berhasil diperbarui!', 'success')

    return redirect(url_for('admin.view_report', report_id=report.id))


@admin.route('/report/<int:report_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_report(report_id):
    from app import db
    from app.models import Report
    report = Report.query.get_or_404(report_id)
    try:
        db.session.delete(report)
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# --- EXPORT DATA (EXCEL & PDF) ---
@admin.route('/export/excel')
@login_required
@admin_required
def export_excel():
    from app.models import Report
    reports = Report.query.all()
    data = [{'ID': r.id, 'Tanggal': r.created_at, 'Judul': r.judul, 'Kategori': r.kategori, 'Status': r.status_warna}
            for r in reports]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="Laporan_Dishub_Enterprise.xlsx", as_attachment=True)


@admin.route('/export/pdf')
@login_required
@admin_required
def export_pdf():
    from app.models import Report
    reports = Report.query.all()
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph("REKAPITULASI LAPORAN DISHUB", styles['Title']))
    data = [['ID', 'Tanggal', 'Judul', 'Kategori', 'Status']]
    for r in reports:
        data.append([r.id, r.created_at.strftime('%d/%m/%y'), r.judul[:30], r.kategori, r.status_warna])
    t = Table(data)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.red), ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(t)
    doc.build(elements)
    output.seek(0)
    return send_file(output, download_name="Laporan_Dishub_Enterprise.pdf", as_attachment=True)


# --- API & MAP DATA ---
@admin.route('/api/reports-map-data')
def reports_map_data():
    from app.models import Report
    reports = Report.query.filter_by(is_archived=False).all()
    return jsonify(
        [{'id': r.id, 'lat': r.latitude, 'lng': r.longitude, 'status': r.status_warna} for r in reports if r.latitude])


# --- PROFILE MANAGEMENT ---
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
    nama, email = request.form.get('nama'), request.form.get('email')
    if nama: user.nama = nama
    if email: user.email = email
    if 'foto_profil' in request.files:
        file = request.files['foto_profil']
        if file and file.filename != '':
            filename = secure_filename(f"admin_{user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
            path = os.path.join('app/static/uploads/profiles')
            os.makedirs(path, exist_ok=True)
            file.save(os.path.join(path, filename))
            user.foto_profil = filename
    db.session.commit()
    flash('Profil berhasil diperbarui!', 'success')
    return redirect(url_for('admin.profile'))


@admin.route('/change_password', methods=['POST'])
@login_required
@admin_required
def change_password():
    from app import db
    from app.models import User
    user = User.query.get(current_user.id)
    new_password = request.form.get('password') or request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    if not new_password:
        flash('Password baru tidak boleh kosong!', 'danger')
    elif new_password != confirm_password:
        flash('Konfirmasi password tidak cocok!', 'danger')
    else:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Password berhasil diperbarui!', 'success')
    return redirect(url_for('admin.profile'))