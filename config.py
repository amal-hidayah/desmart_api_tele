# config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ubah_ini_dengan_kunci_rahasia_yang_sangat_kuat_dan_unik_anda'
    
    # UBAH INI KE SQLITE UNTUK PYTHONANYWHERE!
    # Database akan dibuat di root folder aplikasi Anda (desa_app/site.db)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # Batas ukuran file (16 Megabyte)

    # Menambahkan 'pdf' ke daftar ekstensi yang diizinkan
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'pdf'}