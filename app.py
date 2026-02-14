#!/usr/bin/env python3
import os
# Import eventlet dan monkey_patch HARUS di paling atas jika menggunakan eventlet
# Ini agar SocketIO bisa menangani banyak koneksi chat sekaligus tanpa crash
try:
    import eventlet
    eventlet.monkey_patch()
except ImportError:
    pass

from app import create_app, socketio

# Membuat instance aplikasi Flask
app = create_app(os.getenv('FLASK_ENV') or 'development')

if __name__ == '__main__':
    # Menjalankan aplikasi dengan SocketIO
    # host='0.0.0.0' memungkinkan akses via IP lokal (misal: dari HP)
    # allow_unsafe_werkzeug=True ditambahkan untuk menghindari error di beberapa versi Flask
    socketio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=5000,
        log_output=True # Menampilkan log aktivitas chat di terminal
    )