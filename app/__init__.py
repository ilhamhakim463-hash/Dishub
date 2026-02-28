import os
from flask import Flask, render_template, Blueprint, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required, logout_user
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from datetime import datetime
from config import config

# Inisialisasi Ekstensi Global
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
socketio = SocketIO()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inisialisasi Aplikasi
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # SocketIO & CORS
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')
    CORS(app)

    # Konfigurasi Login Manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu untuk mengakses fitur Lapor Pak.'
    login_manager.login_message_category = 'info'

    from app.models import User, Report, Interaction

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- FITUR 1: LAPORBOT (REALTIME) ---
    @socketio.on('user_message')
    def handle_message(data):
        msg = data.get('message', '').lower()
        nama = current_user.nama if current_user.is_authenticated else 'Warga'
        if any(x in msg for x in ['halo', 'hi', 'p', 'pagi', 'siang', 'sore', 'malam']):
            reply = f"Halo {nama}! Saya LaporBot Jombang. Ada yang bisa dibantu?"
        elif any(x in msg for x in ['cara', 'lapor', 'buat']):
            reply = "Klik menu 'Lapor', isi data. Laporan akan ditinjau Admin sebelum tayang di Feed."
        elif any(x in msg for x in ['poin', 'nilai']):
            reply = f"Poin Anda: {current_user.poin_warga if current_user.is_authenticated else 0}."
        else:
            reply = "Maaf, LaporBot belum mengerti. Silakan tanya 'cara lapor'."
        emit('bot_response', {'message': reply})

    # --- 1. MAIN BLUEPRINT (Public & Feed) ---
    main_bp = Blueprint('main', __name__)

    @main_bp.route('/')
    def index():
        try:
            stats = {
                'total_reports': Report.query.filter_by(is_approved=True).count(),
                'total_users': User.query.filter_by(role='user').count(),
                'selesai_reports': Report.query.filter(
                    Report.is_approved == True,
                    Report.status_warna.in_(['biru', 'hijau'])
                ).count()
            }
        except Exception as e:
            app.logger.error(f"Stats Error: {e}")
            stats = {'total_reports': 0, 'total_users': 0, 'selesai_reports': 0}
        return render_template('public/landing.html', stats=stats)

    @main_bp.route('/api/reports-map-data')
    def reports_map_data():
        reports = Report.query.filter_by(is_approved=True).all()
        data = []
        for r in reports:
            try:
                if r.latitude and r.longitude:
                    urg_map = {'merah': '1', 'kuning': '2'}
                    urgency_level = urg_map.get(r.status_warna, '3')
                    data.append({
                        'id': r.id,
                        'judul': r.judul,
                        'latitude': float(r.latitude),
                        'longitude': float(r.longitude),
                        'urgency': urgency_level,
                        'kategori': r.kategori or "Umum"
                    })
            except (ValueError, TypeError):
                continue
        return jsonify(data)

    @main_bp.route('/feed')
    def feed():
        all_reports = Report.query.filter_by(is_approved=True).order_by(Report.created_at.desc()).all()
        return render_template('public/feed.html', reports=all_reports)

    @main_bp.route('/report/<int:report_id>')
    def view_report(report_id):
        report = Report.query.get_or_404(report_id)
        if hasattr(report, 'views_count'):
            report.views_count = (report.views_count or 0) + 1
            db.session.commit()
        comments = Interaction.query.filter_by(report_id=report_id, tipe='comment').order_by(
            Interaction.created_at.desc()).all()
        return render_template('public/view_report.html', report=report, comments=comments)

    @main_bp.route('/report/<int:report_id>/comment', methods=['POST'])
    @login_required
    def add_comment(report_id):
        content = request.form.get('konten') or request.form.get('comment')
        if content:
            new_comment = Interaction(
                user_id=current_user.id,
                report_id=report_id,
                konten=content,
                tipe='comment',
                created_at=datetime.utcnow()
            )
            db.session.add(new_comment)
            db.session.commit()
            flash('Komentar berhasil ditambahkan!', 'success')
        return redirect(url_for('main.view_report', report_id=report_id))

    @main_bp.route('/lapor-baru')
    @login_required
    def create_report():
        return redirect(url_for('user.create_report'))

    if 'main' not in app.blueprints:
        app.register_blueprint(main_bp)

    # --- 2. USER BLUEPRINT (Dashboard & Actions) ---
    user_bp = Blueprint('user', __name__)

    @user_bp.route('/dashboard')
    @login_required
    def dashboard():
        # JIKA ADMIN MASUK KE SINI, LEMPAR KE DASHBOARD ADMIN
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))

        user_reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).all()
        stats = {
            'total': len(user_reports),
            'pending': Report.query.filter_by(user_id=current_user.id, is_approved=False).count(),
            'poin': current_user.poin_warga or 0,
            'selesai': Report.query.filter(Report.user_id == current_user.id,
                                           Report.status_warna.in_(['biru', 'hijau'])).count()
        }
        return render_template('user/dashboard.html', stats=stats, reports=user_reports)

    @user_bp.route('/lapor', methods=['GET', 'POST'])
    @login_required
    def create_report():
        if request.method == 'POST':
            try:
                def handle_upload(field_name):
                    file = request.files.get(field_name)
                    if file and file.filename != '':
                        fname = secure_filename(
                            f"{field_name}_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M')}_{file.filename}")
                        path = os.path.join(app.static_folder, 'uploads/reports')
                        if not os.path.exists(path): os.makedirs(path)
                        file.save(os.path.join(path, fname))
                        return fname
                    return None

                new_report = Report(
                    user_id=current_user.id, judul=request.form.get('judul'), deskripsi=request.form.get('deskripsi'),
                    kategori=request.form.get('kategori'), latitude=request.form.get('latitude'),
                    longitude=request.form.get('longitude'),
                    status_warna='kuning', is_approved=False, foto_awal=handle_upload('foto_awal'),
                    created_at=datetime.utcnow()
                )
                db.session.add(new_report)
                db.session.commit()
                flash('Laporan terkirim! Menunggu verifikasi Admin.', 'success')
                return redirect(url_for('user.dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Gagal: {str(e)}', 'danger')
        return render_template('user/laporan.html')

    @user_bp.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        if request.method == 'POST':
            file = request.files.get('foto_profil')
            if file and file.filename != '':
                fname = secure_filename(f"user_{current_user.id}_{file.filename}")
                path = os.path.join(app.static_folder, 'uploads/profiles')
                if not os.path.exists(path): os.makedirs(path)
                file.save(os.path.join(path, fname))
                current_user.foto_profil = fname
            current_user.nama = request.form.get('nama')
            current_user.email = request.form.get('email')
            db.session.commit()
            flash('Profil diperbarui!', 'success')
        return render_template('user/profile.html')

    @user_bp.route('/change-password', methods=['POST'])
    @login_required
    def change_password():
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password and new_password == confirm_password:
            current_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Password berhasil diubah!', 'success')
        else:
            flash('Password baru dan konfirmasi tidak cocok!', 'danger')
        return redirect(url_for('user.profile'))

    @user_bp.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Anda telah keluar.', 'success')
        return redirect(url_for('auth.login'))

    if 'user' not in app.blueprints:
        app.register_blueprint(user_bp, url_prefix='/user')

    # --- 3. EXTERNAL BLUEPRINTS (Auth & Admin) ---
    # Memuat blueprint dari folder blueprints yang terlihat di gambar Anda
    try:
        from app.blueprints.auth.routes import auth as auth_blueprint
        if 'auth' not in app.blueprints:
            app.register_blueprint(auth_blueprint, url_prefix='/auth')

        from app.blueprints.admin.routes import admin as admin_blueprint
        if 'admin' not in app.blueprints:
            app.register_blueprint(admin_blueprint, url_prefix='/admin')
    except Exception as e:
        app.logger.error(f"Blueprint Registration Error: {e}")

    return app