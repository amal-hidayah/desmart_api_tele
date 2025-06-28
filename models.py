# models.py

# Import objek db dari extensions.py
from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Kelas User merepresentasikan tabel 'user' di database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # password_hash diperpanjang untuk menampung hash scrypt yang lebih panjang
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='warga', nullable=False) # 'warga' atau 'admin'
    tanggal_daftar = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi dengan model Pengaduan: Satu user dapat memiliki banyak pengaduan
    pengaduan = db.relationship('Pengaduan', backref='pembuat', lazy=True)

    # Fungsi untuk mengatur password (mengenkripsi dan menyimpan hash)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Fungsi untuk memeriksa password (membandingkan input dengan hash yang tersimpan)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Representasi string objek User
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

# Kelas Pengaduan merepresentasikan tabel 'pengaduan' di database
class Pengaduan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Foreign Key ke tabel user
    judul = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    lokasi = db.Column(db.String(200), nullable=True) # Lokasi spesifik dalam teks
    latitude = db.Column(db.Float, nullable=True) # Koordinat GPS Latitude
    longitude = db.Column(db.Float, nullable=True) # Koordinat GPS Longitude
    # url_bukti_media untuk menyimpan nama file (foto/video) yang diunggah
    url_bukti_media = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='Diterima', nullable=False) # Status pengaduan: Diterima, Diproses, Selesai, Ditolak
    tanggal_pengaduan = db.Column(db.DateTime, default=datetime.utcnow)
    # tanggal_update_status akan otomatis diperbarui setiap kali entri diupdate
    tanggal_update_status = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    respon_admin = db.Column(db.Text, nullable=True)

    # Representasi string objek Pengaduan
    def __repr__(self):
        return f"Pengaduan('{self.judul}', '{self.status}', '{self.tanggal_pengaduan}')"

# Kelas Berita merepresentasikan tabel 'berita' di database
class Berita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    isi_berita = db.Column(db.Text, nullable=False)
    url_gambar_utama = db.Column(db.String(255), nullable=True)
    tanggal_publikasi = db.Column(db.DateTime, default=datetime.utcnow)
    penulis = db.Column(db.String(50), default='Admin Desa', nullable=False) # Penulis berita, defaultnya Admin Desa

    # Representasi string objek Berita
    def __repr__(self):
        return f"Berita('{self.judul}', '{self.tanggal_publikasi}')"

# START - Penambahan Model APBDes
class APBDes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tahun = db.Column(db.Integer, nullable=False)
    judul = db.Column(db.String(200), nullable=False) # Misal: "APBDes Tahun 2024"
    deskripsi = db.Column(db.Text, nullable=True) # Ringkasan atau detail anggaran
    # url_file_apbdes untuk menyimpan nama file PDF atau dokumen lainnya
    url_file_apbdes = db.Column(db.String(255), nullable=True)
    tanggal_unggah = db.Column(db.DateTime, default=datetime.utcnow)
    pengunggah_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Siapa yang mengunggah
    pengunggah = db.relationship('User', backref='apbdes_uploads', lazy=True)

    def __repr__(self):
        return f"APBDes('{self.judul}', Tahun {self.tahun}', '{self.tanggal_unggah}')"
# END - Penambahan Model APBDes