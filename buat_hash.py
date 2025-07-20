# buat_hash.py
from werkzeug.security import generate_password_hash

# Masukkan password yang Anda inginkan di dalam tanda kutip
password_admin = "PasswordAdmin123" 

# Generate hash
password_hash = generate_password_hash(password_admin)

print("Password Anda:", password_admin)
print("\nHasil Hash (salin teks panjang di bawah ini):")
print(password_hash)