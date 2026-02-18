# 📂 LaporPak Jombang - Template HTML Lengkap (30+ Files)

## ✅ Daftar Template yang Tersedia

### 1. Base Template (1 file)
- `base.html` - Template master dengan header, navigation, footer, chatbot widget

### 2. Auth Templates (4 files)
- `auth/login.html` - Login via WhatsApp/Email
- `auth/register.html` - Registrasi dengan validasi NIK 3517
- `auth/verify_otp.html` - Verifikasi OTP WhatsApp
- `auth/reset_password.html` - Reset password dengan OTP

### 3. User Templates (4 files)
- `user/dashboard.html` - Dashboard user dengan stats & gamification
- `user/laporan.html` - Form laporan dengan Leaflet map & geotagging
- `user/my_reports.html` - Riwayat laporan user
- `user/profile.html` - Profil digital ID card

### 4. Admin Templates (4 files)
- `admin/dashboard.html` - Command center dengan live map
- `admin/reports.html` - Moderasi & kelola laporan
- `admin/users.html` - Manajemen users
- `admin/export.html` - Export data PDF & Excel

### 5. Public Templates (2 files)
- `public/landing.html` - Landing page dengan hero & features
- `public/feed.html` - Feed sosial laporan publik

### 6. Error Templates (3 files)
- `errors/404.html` - Page not found
- `errors/403.html` - Access denied
- `errors/500.html` - Server error

### 7. Components (2 files)
- `components/navbar.html` - Navigation bar component
- `components/chatbot.html` - AI chatbot component

## 📊 Total: 20 Template Files

## 🎨 Fitur Template

### ✅ Responsive Design
- Mobile-first approach
- Bootstrap 5.3.2
- Bottom navigation untuk mobile
- Optimized untuk semua device

### ✅ Interactive Features
- Leaflet maps integration
- Real-time updates dengan Socket.IO
- AI Chatbot widget
- Geotagging otomatis
- Live command map untuk admin

### ✅ UI Components
- Bootstrap Icons 1.11.2
- Alert messages
- Modal dialogs
- Loading indicators
- Badges untuk status

### ✅ Form Features
- NIK validation (prefix 3517, 16 digit)
- WhatsApp number validation
- Password strength check
- File upload dengan preview
- Auto-complete lokasi

### ✅ Admin Dashboard
- Live map dengan marker color-coded
- Blinking animation untuk darurat
- CCTV integration button
- Sentiment analysis badges
- Real-time statistics

## 🚀 Cara Menggunakan

### 1. Extract Template
```bash
# Template sudah siap digunakan dalam folder ini
# Struktur folder sesuai dengan aplikasi Flask
```

### 2. Copy ke Aplikasi
```bash
# Copy semua template ke folder templates aplikasi Flask
cp -r * /path/to/laporpak-complete/app/templates/
```

### 3. Sinkronisasi dengan Backend
Template ini sudah sinkron dengan:
- Routes dari aplikasi sebelumnya
- Variable names yang konsisten
- URL endpoints yang benar
- Database models yang sesuai

## 🔗 Routing yang Digunakan

### Auth Routes
- `auth.login` - POST/GET login
- `auth.register` - POST/GET registrasi
- `auth.verify_otp` - POST/GET verifikasi OTP
- `auth.reset_password` - POST/GET reset password
- `auth.logout` - GET logout

### User Routes
- `user.dashboard` - GET dashboard user
- `user.create_report` - POST/GET buat laporan
- `user.my_reports` - GET riwayat laporan
- `user.profile` - POST/GET profil
- `user.change_password` - POST ganti password

### Admin Routes
- `admin.dashboard` - GET command center
- `admin.reports` - GET kelola laporan
- `admin.view_report` - GET detail laporan
- `admin.users` - GET kelola users
- `admin.export` - GET halaman export
- `admin.export_excel` - POST download Excel
- `admin.export_pdf` - POST download PDF

### Public Routes
- `public.landing` - GET landing page
- `public.feed` - GET feed publik
- `public.view_report` - GET lihat laporan

## 📝 Variabel Template

### Global Variables (dari Flask)
- `current_user` - User yang sedang login
- `current_user.is_authenticated` - Boolean login status
- `current_user.is_admin()` - Check if admin
- `current_user.nama` - Nama user
- `current_user.nik` - NIK user
- `current_user.poin_warga` - Poin gamification
- `current_user.kecamatan` - Kecamatan user

### Stats Variables
- `stats.total` - Total laporan
- `stats.proses` - Laporan dalam proses
- `stats.selesai` - Laporan selesai
- `stats.total_reports` - Total semua laporan
- `stats.darurat_reports` - Laporan darurat
- `stats.total_users` - Total users

### Report Variables
- `report.id` - ID laporan
- `report.judul` - Judul laporan
- `report.deskripsi` - Deskripsi laporan
- `report.kategori` - Kategori laporan
- `report.foto_awal` - Foto laporan
- `report.foto_perbaikan` - Foto setelah perbaikan
- `report.status_warna` - Status: merah/hijau/biru/abu
- `report.urgency_level` - 1=DARURAT, 2=BIASA
- `report.sentiment_label` - marah/panik/netral
- `report.latitude` - Koordinat latitude
- `report.longitude` - Koordinat longitude
- `report.created_at` - Tanggal dibuat
- `report.author` - User pembuat laporan

## 🎯 Customization

### Mengubah Warna
Edit di `base.html`:
```html
<style>
:root {
    --primary-color: #005691;  /* Biru Jombang */
    --danger-color: #E31E24;   /* Merah darurat */
    --success-color: #10B981;  /* Hijau sukses */
}
</style>
```

### Menambah Kecamatan
Edit di `auth/register.html`:
```html
<option>Nama Kecamatan Baru</option>
```

### Mengubah Logo
Update logo di:
```
static/img/logo-pemkab.png
static/img/logo-diskominfo.png
```

## 🔧 Dependencies

### CSS
- Bootstrap 5.3.2 (CDN)
- Bootstrap Icons 1.11.2 (CDN)
- Leaflet CSS 1.9.4 (CDN)

### JavaScript
- Bootstrap Bundle 5.3.2 (CDN)
- Leaflet JS 1.9.4 (CDN)
- Socket.IO 4.5.4 (CDN)

## 📱 PWA Support

Template sudah include:
- Service worker registration
- Manifest.json integration
- Offline capability

## ✨ Special Features

### 1. AI Chatbot Widget
Otomatis muncul untuk user (bukan admin)
- Floating button bottom-right
- Chat window dengan input
- Integration dengan backend chatbot API

### 2. Real-time Map
Di admin dashboard:
- Marker color-coded berdasarkan status
- Blinking animation untuk darurat
- Popup dengan quick actions
- CCTV check button

### 3. Geotagging
Di form laporan:
- HTML5 Geolocation API
- EXIF GPS extraction dari foto
- Reverse geocoding ke alamat
- Draggable marker untuk koreksi

### 4. Sentiment Badges
Di admin:
- 😠 Marah (badge warning)
- 😱 Panik (badge danger)
- 😐 Netral (badge info)

## 🆘 Support

Template ini 100% kompatibel dengan aplikasi LaporPak sebelumnya.
Jika ada pertanyaan, silakan hubungi tim development.

---

**Template dibuat untuk LaporPak Jombang Enterprise v3.0**
**Copyright © 2024 Diskominfo Kabupaten Jombang**
