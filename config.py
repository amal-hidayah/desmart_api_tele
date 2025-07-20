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

    # --- INFORMASI BOT TELEGRAM (TAMBAHAN) ---
    TELEGRAM_BOT_TOKEN = '7554457306:AAG8wJ3m9Dw93g-GyNSx91uZB4o1z-knfEQ'
    TELEGRAM_CHAT_ID = '-4852510201'

    # --- INFORMASI BOT TELEGRAM (TAMBAHAN) ---
    TELEGRAM_BOT_TOKEN = '7554457306:AAG8wJ3m9Dw93g-GyNSx91uZB4o1z-knfEQ' # Ganti dengan token Anda
    TELEGRAM_CHAT_ID = '-4852510201'      # Ganti dengan ID grup Anda
    TELEGRAM_WEBHOOK_SECRET = '123654' # Ganti dengan string acak