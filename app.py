from flask import Flask, render_template, url_for, flash, redirect, request, send_from_directory, abort
from config import Config
from datetime import datetime
from extensions import db, login_manager

# Import forms yang dibutuhkan
from forms import RegistrasiForm, LoginForm, PengaduanForm, BeritaForm, UserEditForm, APBDesForm, CSRFForm 

# Import models yang dibutuhkan
from models import User, Pengaduan, Berita, APBDes 

from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename
from functools import wraps

# Import Flask-Migrate
from flask_migrate import Migrate
# Import Flask-WTF CSRFProtect
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(Config)

# PENTING: Inisialisasi CSRFProtect setelah objek 'app' dibuat
# Ini diperlukan agar Flask-WTF dapat menyediakan 'csrf_impl' ke semua formulir
csrf = CSRFProtect(app) 

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def save_uploaded_file(file):
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
            return filename
        except Exception as e:
            app.logger.error(f"Gagal menyimpan file {filename}: {e}")
            return None
    return None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rute Aplikasi ---

@app.route('/')
def index():
    berita_terbaru = Berita.query.order_by(Berita.tanggal_publikasi.desc()).limit(3).all()
    return render_template('index.html', berita_terbaru=berita_terbaru)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrasiForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Akun Anda berhasil dibuat! Anda sekarang bisa masuk.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registrasi', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Berhasil masuk!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
        else:
            flash('Login gagal. Mohon periksa email dan kata sandi Anda.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah berhasil keluar.', 'info')
    return redirect(url_for('index'))

@app.route('/pengaduan/baru', methods=['GET', 'POST'])
@login_required
def buat_pengaduan():
    form = PengaduanForm()
    if form.validate_on_submit():
        media_filename = None
        if form.bukti_media.data:
            media_filename = save_uploaded_file(form.bukti_media.data)
            if not media_filename:
                flash('Gagal mengunggah file. Pastikan format dan ukuran file sesuai.', 'danger')
                return render_template('pengaduan/create_pengaduan.html', title='Buat Pengaduan', form=form)

        pengaduan = Pengaduan(
            judul=form.judul.data,
            deskripsi=form.deskripsi.data,
            lokasi=form.lokasi.data,
            latitude=form.latitude.data if form.latitude.data else None,
            longitude=form.longitude.data if form.longitude.data else None,
            url_bukti_media=media_filename,
            pembuat=current_user
        )
        db.session.add(pengaduan)
        db.session.commit()
        flash('Pengaduan Anda berhasil diajukan!', 'success')
        return redirect(url_for('daftar_pengaduan'))
    return render_template('pengaduan/create_pengaduan.html', title='Buat Pengaduan', form=form)

@app.route('/pengaduan')
@login_required
def daftar_pengaduan():
    # Semua pengguna yang login (warga atau admin) akan melihat semua pengaduan.
    pengaduans = Pengaduan.query.order_by(Pengaduan.tanggal_pengaduan.desc()).all()
    return render_template('pengaduan/list_pengaduan.html', title='Daftar Pengaduan', pengaduans=pengaduans)


@app.route('/pengaduan/<int:pengaduan_id>')
@login_required
def detail_pengaduan(pengaduan_id):
    pengaduan = Pengaduan.query.get_or_404(pengaduan_id)
    return render_template('pengaduan/detail_pengaduan.html', title=pengaduan.judul, pengaduan=pengaduan)

# --- Rute Admin ---
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_pengaduan = Pengaduan.query.count()
    pengaduan_baru = Pengaduan.query.filter_by(status='Diterima').count()
    pengaduan_diproses = Pengaduan.query.filter_by(status='Diproses').count()
    pengaduan_selesai = Pengaduan.query.filter_by(status='Selesai').count()
    
    latest_pengaduans = Pengaduan.query.order_by(Pengaduan.tanggal_pengaduan.desc()).limit(5).all()
    latest_apbdes = APBDes.query.order_by(APBDes.tahun.desc(), APBDes.tanggal_unggah.desc()).limit(3).all()

    return render_template('admin/dashboard.html', title='Dashboard Admin',
                            total_pengaduan=total_pengaduan,
                            pengaduan_baru=pengaduan_baru,
                            pengaduan_diproses=pengaduan_diproses,
                            pengaduan_selesai=pengaduan_selesai,
                            latest_pengaduans=latest_pengaduans,
                            latest_apbdes=latest_apbdes)

@app.route('/admin/pengaduan')
@admin_required
def kelola_pengaduan():
    pengaduans = Pengaduan.query.order_by(Pengaduan.tanggal_pengaduan.desc()).all()
    return render_template('admin/kelola_pengaduan.html', title='Kelola Pengaduan', pengaduans=pengaduans)

@app.route('/admin/pengaduan/<int:pengaduan_id>/update', methods=['GET', 'POST'])
@admin_required
def update_pengaduan_status(pengaduan_id):
    pengaduan = Pengaduan.query.get_or_404(pengaduan_id)
    
    if request.method == 'POST':
        new_status = request.form.get('status')
        admin_response = request.form.get('respon_admin')

        if new_status:
            pengaduan.status = new_status
        if admin_response:
            pengaduan.respon_admin = admin_response
        
        db.session.commit()
        flash('Status pengaduan berhasil diperbarui.', 'success')
        return redirect(url_for('detail_pengaduan', pengaduan_id=pengaduan.id))
    
    return render_template('admin/update_pengaduan.html', title='Update Pengaduan', pengaduan=pengaduan)

# --- Rute Admin Berita ---
@app.route('/admin/berita/baru', methods=['GET', 'POST'])
@admin_required
def buat_berita():
    form = BeritaForm()
    if form.validate_on_submit():
        gambar_filename = None
        if form.gambar_utama.data:
            gambar_filename = save_uploaded_file(form.gambar_utama.data)
            if not gambar_filename:
                flash('Gagal mengunggah gambar utama berita. Pastikan format dan ukuran file sesuai.', 'danger')
                return render_template('admin/berita/create_berita.html', title='Buat Berita', form=form)

        berita = Berita(
            judul=form.judul.data,
            isi_berita=form.isi_berita.data,
            url_gambar_utama=gambar_filename,
            penulis=current_user.username
        )
        db.session.add(berita)
        db.session.commit()
        flash('Berita berhasil ditambahkan!', 'success')
        return redirect(url_for('kelola_berita'))
    return render_template('admin/berita/create_berita.html', title='Buat Berita Baru', form=form)

@app.route('/admin/berita')
@admin_required
def kelola_berita():
    beritas = Berita.query.order_by(Berita.tanggal_publikasi.desc()).all()
    return render_template('admin/berita/list_berita.html', title='Kelola Berita', beritas=beritas)

@app.route('/admin/berita/<int:berita_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_berita(berita_id):
    berita = Berita.query.get_or_404(berita_id)
    form = BeritaForm(obj=berita)

    if form.validate_on_submit():
        if form.gambar_utama.data:
            if berita.url_gambar_utama:
                 old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], berita.url_gambar_utama)
                 if os.path.exists(old_file_path):
                     os.remove(old_file_path)

            gambar_filename = save_uploaded_file(form.gambar_utama.data)
            if not gambar_filename:
                flash('Gagal mengunggah gambar baru. Pastikan format dan ukuran file sesuai.', 'danger')
                return render_template('admin/berita/edit_berita.html', title='Edit Berita', form=form, berita=berita)
            berita.url_gambar_utama = gambar_filename
        
        berita.judul = form.judul.data
        berita.isi_berita = form.isi_berita.data

        db.session.commit()
        flash('Berita berhasil diperbarui!', 'success')
        return redirect(url_for('kelola_berita'))
    
    elif request.method == 'GET':
        pass

    return render_template('admin/berita/edit_berita.html', title='Edit Berita', form=form, berita=berita)

@app.route('/admin/berita/<int:berita_id>/hapus', methods=['POST'])
@admin_required
def hapus_berita(berita_id):
    berita = Berita.query.get_or_404(berita_id)
    
    if berita.url_gambar_utama:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], berita.url_gambar_utama)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(berita)
    db.session.commit()
    flash('Berita berhasil dihapus!', 'success')
    return redirect(url_for('kelola_berita'))

# --- Rute Publik Berita ---
@app.route('/berita')
def daftar_berita_publik():
    beritas = Berita.query.order_by(Berita.tanggal_publikasi.desc()).all()
    return render_template('list_berita_publik.html', title='Berita Desa', beritas=beritas)

@app.route('/berita/<int:berita_id>')
def detail_berita_publik(berita_id):
    berita = Berita.query.get_or_404(berita_id)
    return render_template('detail_berita_publik.html', title=berita.judul, berita=berita)

# --- Rute Admin Pengguna ---
@app.route('/admin/users')
@admin_required
def kelola_users():
    users = User.query.order_by(User.tanggal_daftar.desc()).all()
    return render_template('admin/users/list_users.html', title='Kelola Pengguna', users=users)

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(original_username=user.username, original_email=user.email, obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        flash('Data pengguna berhasil diperbarui!', 'success')
        return redirect(url_for('kelola_users'))
    
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role

    return render_template('admin/users/edit_user.html', title='Edit Pengguna', form=form, user=user)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Anda tidak dapat menghapus akun Anda sendiri.', 'danger')
        return redirect(url_for('kelola_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash(f'Pengguna {user.username} berhasil dihapus secara permanen.', 'success')
    return redirect(url_for('kelola_users'))

# --- Rute APBDes (Admin) ---
@app.route('/admin/apbdes/baru', methods=['GET', 'POST'])
@admin_required
def buat_apbdes():
    form = APBDesForm()
    if form.validate_on_submit():
        file_filename = None
        if form.file_apbdes.data:
            file_filename = save_uploaded_file(form.file_apbdes.data)
            if not file_filename:
                flash('Gagal mengunggah file APBDes. Pastikan format dan ukuran file sesuai.', 'danger')
                return render_template('admin/apbdes/create_apbdes.html', title='Tambah APBDes', form=form)

        apbdes = APBDes(
            tahun=form.tahun.data,
            judul=form.judul.data,
            deskripsi=form.deskripsi.data,
            url_file_apbdes=file_filename,
            pengunggah=current_user
        )
        db.session.add(apbdes)
        db.session.commit()
        flash('Data APBDes berhasil ditambahkan!', 'success')
        return redirect(url_for('kelola_apbdes'))
    return render_template('admin/apbdes/create_apbdes.html', title='Tambah Data APBDes', form=form)

@app.route('/admin/apbdes')
@admin_required
def kelola_apbdes():
    apbdes_list = APBDes.query.order_by(APBDes.tahun.desc(), APBDes.tanggal_unggah.desc()).all()
    # Buat instance CSRFForm untuk dikirim ke template
    form_hapus = CSRFForm() 
    return render_template('admin/apbdes/list_apbdes.html', title='Kelola APBDes', apbdes_list=apbdes_list, form=form_hapus)


@app.route('/admin/apbdes/<int:apbdes_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_apbdes(apbdes_id):
    apbdes = APBDes.query.get_or_404(apbdes_id)
    form = APBDesForm(obj=apbdes)

    if form.validate_on_submit():
        if form.file_apbdes.data:
            if apbdes.url_file_apbdes:
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], apbdes.url_file_apbdes)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            file_filename = save_uploaded_file(form.file_apbdes.data)
            if not file_filename:
                flash('Gagal mengunggah file baru. Pastikan format dan ukuran file sesuai.', 'danger')
                return render_template('admin/apbdes/edit_apbdes.html', title='Edit APBDes', form=form, apbdes=apbdes)
            apbdes.url_file_apbdes = file_filename
        
        apbdes.tahun = form.tahun.data
        apbdes.judul = form.judul.data
        apbdes.deskripsi = form.deskripsi.data
        
        db.session.commit()
        flash('Data APBDes berhasil diperbarui!', 'success')
        return redirect(url_for('kelola_apbdes'))
    
    elif request.method == 'GET':
        pass

    return render_template('admin/apbdes/edit_apbdes.html', title='Edit APBDes', form=form, apbdes=apbdes)

@app.route('/admin/apbdes/<int:apbdes_id>/hapus', methods=['POST'])
@admin_required
def hapus_apbdes(apbdes_id):
    apbdes = APBDes.query.get_or_404(apbdes_id)
    
    # Validasi CSRF token
    form_hapus = CSRFForm() # Buat instance form hapus juga di sini
    if form_hapus.validate_on_submit(): 
        if apbdes.url_file_apbdes:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], apbdes.url_file_apbdes)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(apbdes)
        db.session.commit()
        flash('Data APBDes berhasil dihapus!', 'success')
        return redirect(url_for('kelola_apbdes'))
    else:
        flash('Permintaan tidak valid. Mohon coba lagi.', 'danger') 
        return redirect(url_for('kelola_apbdes'))


# --- Rute APBDes (Publik) ---
@app.route('/apbdes')
def daftar_apbdes_publik():
    apbdes_list = APBDes.query.order_by(APBDes.tahun.desc(), APBDes.tanggal_unggah.desc()).all()
    return render_template('apbdes/list_apbdes_publik.html', title='Cek APBDes', apbdes_list=apbdes_list)

@app.route('/apbdes/<int:apbdes_id>')
def detail_apbdes_publik(apbdes_id):
    apbdes = APBDes.query.get_or_404(apbdes_id)
    return render_template('apbdes/detail_apbdes_publik.html', title=f"APBDes {apbdes.tahun}", apbdes=apbdes)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
