from flask import Blueprint, jsonify, url_for
from app.models import User, Report, Category
from app import db

# Mendefinisikan Blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return jsonify({
        "status": "online",
        "app_name": "Lapor Pak Backend",
        "message": "Backend successfully connected!"
    })

@main.route('/api/stats')
def get_stats():
    # Menghitung statistik sesuai dengan nama field di model User & Report
    user_count = User.query.count()
    report_count = Report.query.count()
    # Filter menggunakan status_label atau is_approved sesuai logika bisnis Anda
    selesai_count = Report.query.filter(Report.status_label.ilike('%selesai%')).count()

    return jsonify({
        "total_user": user_count,
        "total_laporan": report_count,
        "selesai_laporan": selesai_count
    })

@main.route('/api/reports-map-data')
def reports_map_data():
    """
    Endpoint khusus untuk menyuplai data koordinat ke Leaflet JS di landing.html.
    Menggunakan field dari model Report: latitude, longitude, status_warna, judul.
    """
    # Ambil semua data laporan yang memiliki koordinat
    reports = Report.query.filter(Report.latitude.isnot(None), Report.longitude.isnot(None)).all()

    return jsonify([{
        'id': r.id,
        'lat': r.latitude,
        'lng': r.longitude,
        'status_warna': r.status_warna or 'biasa', # Menentukan warna pin (merah/kuning/biru)
        'judul': r.judul or 'Laporan Tanpa Judul',
        'foto': r.foto_awal,
        'created_at': r.created_at.strftime("%d %b %Y %H:%M") if r.created_at else "-",
        'url_detail': f"/report/{r.id}" # Sesuaikan dengan route detail Anda
    } for r in reports])