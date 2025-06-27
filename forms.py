# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_wtf.file import FileField, FileAllowed
from models import User # Import model User untuk validasi

class RegistrasiForm(FlaskForm):
    username = StringField('Nama Pengguna', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Kata Sandi', validators=[DataRequired()])
    konfirmasi_password = PasswordField('Konfirmasi Kata Sandi',
                                         validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Daftar Sebagai', choices=[('warga', 'Warga')], validators=[DataRequired()])
    submit = SubmitField('Daftar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Nama pengguna ini sudah terdaftar. Mohon pilih yang lain.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email ini sudah terdaftar. Mohon gunakan email lain.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Kata Sandi', validators=[DataRequired()])
    submit = SubmitField('Masuk')

class PengaduanForm(FlaskForm):
    judul = StringField('Judul Pengaduan', validators=[DataRequired(), Length(min=5, max=100)])
    deskripsi = TextAreaField('Deskripsi Lengkap', validators=[DataRequired(), Length(min=10)])
    lokasi = StringField('Lokasi (Contoh: Jl. Merdeka No. 10, RT 01 RW 02)', validators=[DataRequired(), Length(min=5, max=200)])
    
    latitude = FloatField('Latitude')
    longitude = FloatField('Longitude')

    bukti_media = FileField('Upload Foto/Video Bukti', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'mp4', 'avi', 'mov'], 'Hanya gambar (JPG, PNG, GIF) atau video (MP4, AVI, MOV)!')])
    
    submit = SubmitField('Kirim Pengaduan')

# --- Form Baru untuk Berita ---
class BeritaForm(FlaskForm):
    judul = StringField('Judul Berita', validators=[DataRequired(), Length(min=5, max=200)])
    isi_berita = TextAreaField('Isi Berita Lengkap', validators=[DataRequired(), Length(min=50)])
    # Untuk gambar utama berita, bisa opsional
    gambar_utama = FileField('Gambar Utama (Opsional)', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Hanya gambar (JPG, PNG, JPEG, GIF)!')])
    submit = SubmitField('Simpan Berita')