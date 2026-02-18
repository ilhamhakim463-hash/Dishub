from flask import Blueprint, jsonify
from app.models import User, Report

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
    # Menghitung statistik langsung dari database sesuai kebutuhan dashboard
    user_count = User.query.count()
    report_count = Report.query.count()
    selesai_count = Report.query.filter_by(status='selesai').count()  # Asumsi field status ada di model Report

    return jsonify({
        "total_user": user_count,
        "total_laporan": report_count,
        "selesai_laporan": selesai_count
    })


@main.route('/api/reports-map-data')
def reports_map_data():
    """
    Endpoint khusus untuk menyuplai data koordinat ke Leaflet JS.
    Pastikan model Report memiliki field: id, latitude, longitude, urgency, dan judul.
    """
    # Ambil semua data laporan dari database
    reports = Report.query.all()

    return jsonify([{
        'id': r.id,
        'latitude': r.latitude,
        'longitude': r.longitude,
        'urgency': r.urgency,  # Digunakan untuk menentukan warna pin di frontend
        'judul': r.judul
    } for r in reports])