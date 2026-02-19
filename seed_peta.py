from app import create_app, db
from app.models import Report, User
from datetime import datetime

app = create_app()

with app.app_context():
    # 1. Pastikan ada user untuk memiliki laporan ini
    user = User.query.first()
    if not user:
        print("Error: Tidak ada user di database. Jalankan aplikasi dan daftar satu akun dulu.")
    else:
        print(f"Menggunakan user: {user.nama}")

        # 2. Data Laporan Contoh (Koordinat wilayah Jombang)
        laporan_dummy = [
            {
                'judul': 'Jalan Berlubang Parah',
                'lat': -7.5461, 'lng': 112.2331,
                'urgency': 'merah', 'kat': 'Infrastruktur'
            },
            {
                'judul': 'Pohon Tumbang',
                'lat': -7.5390, 'lng': 112.2450,
                'urgency': 'kuning', 'kat': 'Bencana'
            },
            {
                'judul': 'Lampu Jalan Mati',
                'lat': -7.5550, 'lng': 112.2200,
                'urgency': 'hijau', 'kat': 'Fasilitas Umum'
            }
        ]

        for data in laporan_dummy:
            report = Report(
                user_id=user.id,
                judul=data['judul'],
                deskripsi='Ini adalah data percobaan untuk testing peta.',
                kategori=data['kat'],
                latitude=str(data['lat']),
                longitude=str(data['lng']),
                status_warna=data['urgency'],
                is_approved=True,  # WAJIB True agar muncul di peta sesuai filter codingan kita
                created_at=datetime.utcnow()
            )
            db.session.add(report)

        db.session.commit()
        print("✅ Sukses! 3 data laporan baru dengan koordinat Jombang telah ditambahkan.")