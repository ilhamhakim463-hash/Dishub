import os
from app import create_app, socketio

# Gunicorn akan mengimpor "app" dari sini
app = create_app(os.getenv("FLASK_ENV") or "production")

# Alias umum (kalau ada tooling yang cari "application")
application = app
