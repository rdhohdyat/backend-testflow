# 1. Level Dasar: Percabangan Sederhana (If-Else)
# Tujuan: Menguji apakah label True (Hijau) dan False (Merah) muncul dengan benar.
def cek_kelulusan(nilai):
    if nilai >= 75:
        return "Lulus"
    else:
        return "Tidak Lulus"

# 2. Level Menengah: Percabangan Bertingkat (Elif)
# Tujuan: Menguji apakah sistem bisa menangani percabangan beruntun tanpa menumpuk garis.

def tentukan_grade(skor):
    if skor >= 90:
        return "A"
    elif skor >= 80:
        return "B"
    elif skor >= 70:
        return "C"
    else:
        return "D"
    
# 3. Level Penting: Percabangan Bersarang (Nested If)
# Tujuan: Ini SANGAT PENTING untuk menguji perbaikan backend yang baru saja kita lakukan (mengatasi error dict ID).

def kategori_usia(umur):
    if umur >= 17:
        if umur >= 60:
            return "Lansia"
        else:
            return "Dewasa"
    else:
        return "Anak-anak"

# 4. Level Loop: Perulangan Sederhana (While)
# Tujuan: Menguji garis "loop back" dan memastikan Path Builder tidak terjebak infinite loop.
def hitung_mundur(n):
    hasil = []
    while n > 0:
        hasil.append(n)
        n = n - 1
    return "Selesai"


# Tujuan: Menguji kombinasi iterasi dan seleksi. Ini sering membingungkan visualisasi jika logika parent_id salah.
def jumlahkan_genap(batas):
    total = 0
    for i in range(batas):
        if i % 2 == 0:
            total += i
    return total

def cek_positif(angka):
    pesan = "Netral atau Negatif"
    
    if angka > 0:
        pesan = "Positif"
        
    return pesan


# Test Input: {"password": "test1234"}

# Ekspektasi: Graf panjang vertikal. PathList harus mendeteksi kombinasi jalur (misal: panjang True + angka False, dst).
def validasi_password(password):
    skor = 0
    pesan = []

    if len(password) >= 8:
        skor += 1
    else:
        pesan.append("Kurang panjang")
        
    ada_angka = False
    for char in password:
        if char.isdigit():
            ada_angka = True
            break
            
    if ada_angka:
        skor += 1
    else:
        pesan.append("Butuh angka")
        
    if skor == 2:
        return "Password Kuat"
    elif skor == 1:
        return "Password Sedang"
    else:
        return "Password Lemah"
    
    
def cari_prima(batas):
    daftar_prima = []
    
    # Loop Luar
    angka = 2
    while angka <= batas:
        is_prima = True
        
        # Loop Dalam
        pembagi = 2
        while pembagi * pembagi <= angka:
            if angka % pembagi == 0:
                is_prima = False
                break # Keluar dari Loop Dalam
            pembagi += 1
            
        if is_prima:
            daftar_prima.append(angka)
            
        angka += 1
        
    return daftar_prima