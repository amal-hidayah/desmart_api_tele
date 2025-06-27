# config.py

import os

class Config:
    # Kunci rahasia untuk keamanan sesi Flask. Ganti dengan string acak yang SANGAT kuat!
    # Anda bisa generate di Python dengan: import os; os.urandom(24).hex()
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci_rahasia_anda_yang_sangat_kuat_sekali_ini_ubah_ini'
    
    # Konfigurasi koneksi database MySQL
    # Ganti 'app_user' dan 'password_APLIKASI_MU_DISINI' dengan kredensial MySQL Anda
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://app_user:Amal191204@localhost/aplikasi_desa_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Konfigurasi untuk folder penyimpanan file yang diunggah
    # app.root_path akan merujuk ke direktori root aplikasi (desa_app)
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # Batas ukuran file (16 Megabyte)

    # Ekstensi file yang diizinkan untuk diunggah
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}