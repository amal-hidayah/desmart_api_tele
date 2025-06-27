# config.py

import os

class Config:
    # Kunci rahasia untuk keamanan sesi Flask. Ganti dengan string acak yang SANGAT kuat!
    # Anda bisa generate di Python dengan: import os; os.urandom(24).hex()
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ubah_ini_dengan_kunci_rahasia_yang_sangat_kuat_dan_unik_anda'
    
    # Konfigurasi koneksi database SQLite (FILE .db)
    # Database akan dibuat di root folder aplikasi Anda (desa_app/site.db)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Direkomendasikan False untuk menghindari overhead

    # Konfigurasi untuk folder penyimpanan file yang diunggah
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # Batas ukuran file (16 Megabyte)

    # Ekstensi file yang diizinkan untuk diunggah
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}