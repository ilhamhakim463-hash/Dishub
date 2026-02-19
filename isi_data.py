from app import create_app, db
from app.models import Report, User

app = create_app()

with app.app_context():
    # Ambil user pertama sebagai pemilik laporan
    user = User.query.first()
    if not user:
        print("Gagal: Buat akun/register dulu di web agar ada user di database!")
    else:
        # Tambah 3 laporan dummy
        l1 = Report(user_id=user.id, judul="Jalan Berlubang", kategori="Infrastruktur",
                    latitude="-7.5461", longitude="112.2331", status_warna="merah", is_approved=True)
        l2 = Report(user_id=user.id, judul="Banjir Luapan", kategori="Bencana",
                    latitude="-7.5390", longitude="112.2450", status_warna="kuning", is_approved=True)
        l3 = Report(user_id=user.id, judul="Sampah Menumpuk", kategori="Kebersihan",
                    latitude="-7.5550", longitude="112.2200", status_warna="hijau", is_approved=True)

        db.session.add_all([l1, l2, l3])
        db.session.commit()
        print("✅ Berhasil! 3 Pin sekarang harusnya muncul di peta.")