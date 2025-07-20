from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from flask_wtf.file import FileField, FileAllowed
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Kata Sandi', validators=[DataRequired()])
    submit = SubmitField('Masuk')

class PengaduanPublikForm(FlaskForm):
    nama_pelapor = StringField('Nama Anda', validators=[DataRequired(), Length(min=3, max=100)])
    kontak_pelapor = StringField('Email atau No. HP Anda', validators=[DataRequired(), Length(min=5, max=100)])
    judul = StringField('Judul Pengaduan', validators=[DataRequired(), Length(max=100)])
    deskripsi = TextAreaField('Deskripsi Lengkap', validators=[DataRequired()])
    lokasi = StringField('Alamat/Lokasi Kejadian', validators=[DataRequired(), Length(max=200)])
    bukti_media = FileField('Upload Foto/Video Bukti (Opsional)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'mp4', 'avi', 'mov'], 'Hanya gambar atau video!')
    ])
    latitude = HiddenField('Latitude')
    longitude = HiddenField('Longitude')
    submit = SubmitField('Kirim Pengaduan')

class BeritaForm(FlaskForm):
    judul = StringField('Judul Berita', validators=[DataRequired(), Length(min=5, max=200)])
    isi_berita = TextAreaField('Isi Berita Lengkap', validators=[DataRequired(), Length(min=50)])
    gambar_utama = FileField('Gambar Utama (Opsional)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Hanya gambar (JPG, PNG, JPEG, GIF)!')
    ])
    submit = SubmitField('Simpan Berita')

class UserEditForm(FlaskForm):
    username = StringField('Nama Pengguna', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role Pengguna', choices=[('warga', 'Warga'), ('admin', 'Admin')], validators=[DataRequired()])
    password = PasswordField('Kata Sandi Baru (kosongkan jika tidak ingin mengubah)')
    konfirmasi_password = PasswordField('Konfirmasi Kata Sandi Baru', validators=[EqualTo('password', message='Kata sandi tidak cocok.')])
    submit = SubmitField('Update Pengguna')

    original_username = None
    original_email = None

    def __init__(self, original_username=None, original_email=None, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Nama pengguna ini sudah terdaftar. Mohon pilih yang lain.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email ini sudah terdaftar. Mohon gunakan email lain.')

"""
# Form APBDes disembunyikan
class APBDesForm(FlaskForm):
    tahun = IntegerField('Tahun Anggaran', validators=[DataRequired(), NumberRange(min=2000, max=2100, message='Tahun tidak valid.')])
    judul = StringField('Judul Dokumen APBDes', validators=[DataRequired(), Length(min=5, max=200)])
    deskripsi = TextAreaField('Deskripsi Singkat / Ringkasan', validators=[Length(max=500)], render_kw={"rows": 5})
    file_apbdes = FileField('Unggah Dokumen APBDes (PDF/Gambar, Opsional)', validators=[
        FileAllowed(['pdf', 'jpg', 'png', 'jpeg'], 'Hanya file PDF atau gambar!')
    ])
    submit = SubmitField('Simpan Data APBDes')
"""

class CSRFForm(FlaskForm):
    pass
