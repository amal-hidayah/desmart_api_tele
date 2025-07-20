import asyncio
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
import os

# Import model dari proyek Flask Anda
from models import Pengaduan, User 

# --- KONFIGURASI ---
BOT_TOKEN = "7554457306:AAG8wJ3m9Dw93g-GyNSx91uZB4o1z-knfEQ" # Token Anda
CHAT_ID = -4852510201  # Chat ID grup Anda

# Membuat path absolut ke file database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Mengasumsikan site.db ada di dalam folder 'instance'
DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "instance", "site.db")}'

# --- KONEKSI DATABASE ---
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Membuat sesi database baru."""
    return SessionLocal()

# --- FUNGSI HANDLER UNTUK TOMBOL ---
async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani saat tombol ditekan."""
    query = update.callback_query
    await query.answer()

    try:
        action, new_status, pengaduan_id_str = query.data.split(':')
        pengaduan_id = int(pengaduan_id_str)
    except (ValueError, IndexError):
        await query.edit_message_text(text="Error: Data tombol tidak valid.")
        return

    db_session = get_db_session()
    try:
        pengaduan = db_session.query(Pengaduan).filter_by(id=pengaduan_id).first()
        if not pengaduan:
            await query.edit_message_text(text=f"Error: Pengaduan ID {pengaduan_id} tidak ditemukan.")
            return

        pengaduan.status = new_status.capitalize()
        db_session.commit()

        # Edit pesan untuk menunjukkan status baru
        original_text = query.message.caption if query.message.caption else query.message.text
        updated_text = f"{original_text}\n\n*Status Diperbarui:* `{pengaduan.status}`"
        
        # Cek apakah pesan asli memiliki foto atau tidak
        if query.message.photo:
             await query.edit_message_caption(caption=updated_text, parse_mode=ParseMode.MARKDOWN)
        else:
             await query.edit_message_text(text=updated_text, parse_mode=ParseMode.MARKDOWN)
    finally:
        db_session.close()

# --- FUNGSI UTAMA BOT ---
async def check_new_complaints(context: ContextTypes.DEFAULT_TYPE):
    """Memeriksa database untuk pengaduan baru secara berkala."""
    db_session = get_db_session()
    try:
        pengaduan_baru = db_session.query(Pengaduan).filter_by(notifikasi_terkirim=False).all()

        for pengaduan in pengaduan_baru:
            pelapor_username = ""
            if pengaduan.pembuat_id and pengaduan.pembuat:
                pelapor_username = pengaduan.pembuat.username
            elif pengaduan.nama_pelapor:
                pelapor_username = pengaduan.nama_pelapor
            else:
                pelapor_username = "Tidak diketahui"
            
            # Buat link Google Maps jika ada koordinat
            link_gps = ""
            if pengaduan.latitude and pengaduan.longitude:
                gmaps_url = f"https://www.google.com/maps/search/?api=1&query={pengaduan.latitude},{pengaduan.longitude}"
                link_gps = f"\n*Link GPS:* [Lihat di Peta]({gmaps_url})"

            # Buat pesan notifikasi
            pesan_notifikasi = (
                f"🔔 *Pengaduan Baru Diterima!*\n\n"
                f"*ID:* `{pengaduan.id}`\n"
                f"*Judul:* {pengaduan.judul}\n"
                f"*Pelapor:* {pelapor_username}\n"
                f"*Kontak:* {pengaduan.kontak_pelapor}\n"
                f"*Lokasi:* {pengaduan.lokasi}"
                f"{link_gps}"  # <-- Link GPS ditambahkan di sini
                f"\n\n_{pengaduan.deskripsi}_"
            )

            # Buat tombol
            keyboard = [[
                InlineKeyboardButton("✅ Proses", callback_data=f"status:Diproses:{pengaduan.id}"),
                InlineKeyboardButton("🏁 Selesai", callback_data=f"status:Selesai:{pengaduan.id}"),
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Logika untuk mengirim foto jika ada
            if pengaduan.url_bukti_media:
                photo_path = os.path.join(BASE_DIR, 'uploads', pengaduan.url_bukti_media)
                if os.path.exists(photo_path):
                    await context.bot.send_photo(
                        chat_id=CHAT_ID,
                        photo=open(photo_path, 'rb'),
                        caption=pesan_notifikasi,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup
                    )
                else:
                    # Fallback jika file foto tidak ditemukan di server
                    pesan_error_foto = f"{pesan_notifikasi}\n\n*(Peringatan: File bukti foto tidak ditemukan di server)*"
                    await context.bot.send_message(
                        chat_id=CHAT_ID, text=pesan_error_foto, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
                    )
            else:
                # Kirim pesan teks biasa jika tidak ada bukti media
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=pesan_notifikasi,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            
            # Tandai bahwa notifikasi sudah terkirim
            pengaduan.notifikasi_terkirim = True
            db_session.commit()
            print(f"Notifikasi untuk pengaduan ID {pengaduan.id} telah dikirim.")
    
    except Exception as e:
        print(f"Terjadi error saat memeriksa pengaduan: {e}")
    finally:
        db_session.close()

def main() -> None:
    """Jalankan bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CallbackQueryHandler(handle_button_press))

    job_queue = application.job_queue
    job_queue.run_repeating(check_new_complaints, interval=10, first=0)

    print("Bot sedang berjalan dan memantau database...")
    application.run_polling()

if __name__ == "__main__":
    main()