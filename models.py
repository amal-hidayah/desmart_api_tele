from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='warga', nullable=False)
    tanggal_daftar = db.Column(db.DateTime, default=datetime.utcnow)

    pengaduan_dibuat = db.relationship('Pengaduan', backref='pembuat', lazy=True)
    # Relasi APBDes disembunyikan
    # apbdes_diunggah = db.relationship('APBDes', backref='pengunggah', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

class Pengaduan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pembuat_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_pengaduan_user'), nullable=True) 
    nama_pelapor = db.Column(db.String(100), nullable=True)
    kontak_pelapor = db.Column(db.String(100), nullable=True)
    judul = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    lokasi = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    url_bukti_media = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='Diterima', nullable=False)
    tanggal_pengaduan = db.Column(db.DateTime, default=datetime.utcnow)
    tanggal_update_status = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    respon_admin = db.Column(db.Text, nullable=True)
    notifikasi_terkirim = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"Pengaduan('{self.judul}', '{self.status}', '{self.tanggal_pengaduan}')"

class Berita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    isi_berita = db.Column(db.Text, nullable=False)
    url_gambar_utama = db.Column(db.String(255), nullable=True)
    tanggal_publikasi = db.Column(db.DateTime, default=datetime.utcnow)
    penulis = db.Column(db.String(50), default='Admin Desa', nullable=False)

    def __repr__(self):
        return f"Berita('{self.judul}', '{self.tanggal_publikasi}')"

"""
# Model APBDes disembunyikan untuk sementara
class APBDes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tahun = db.Column(db.Integer, nullable=False)
    judul = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    url_file_apbdes = db.Column(db.String(255), nullable=True)
    tanggal_unggah = db.Column(db.DateTime, default=datetime.utcnow)
    pengunggah_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_apbdes_user'), nullable=False)

    def __repr__(self):
        return f"APBDes('{self.judul}', Tahun {self.tahun}', '{self.tanggal_unggah}')"
"""
