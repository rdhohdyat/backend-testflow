def cek_genap_ganjil(angka):
    if angka % 2 == 0:
        return "Genap"
    else:
        return "Ganjil"
    
def jumlah_ganjil(n):
    start = 1
    for i in range(start, n):
        if i % 2 == 1:
            total += i
    return total
  
def percabangan(x, y):
    if x > y:
        for i in range(1,5):
            print("x " , i)
    else:
        print("y lebih besar")

def perulangan(a, b):
    hasil = 0
    if(b > a):
        for i in range(a, b):
            hasil += i
    else:
        return "b kecil dari a"
    return hasil
        
def perulangan_bersarang(a):
    for i in range(1, a):
        for j in range(1, a):
            print("hallo")
        
def luas_persegi_panjang(panjang, lebar):
    if panjang > 0 and lebar > 0:
        return panjang * lebar
    else:
        print("Panjang dan lebar harus lebih besari dari 0!")
        
def klasifikasi_angka(x):
    if x > 0:
        if x % 2 == 0:
            return "Positif genap"
        else:
            return "Positif ganjil"
    elif x < 0:
        return "Negatif"
    else:
        return "Nol"

def faktorial(n):
    if n < 0:
        return "Tidak ada faktorial untuk bilangan negatif"
    hasil = 1
    while n > 1:
        hasil *= n
        n -= 1
    return hasil
        
def is_pangkat_dua(n):
    if n < 1:
        return False
    while n > 1:
        if n % 2 != 0:
            return False
        n = n // 2
    return True


def bagi(a, b):
    try:
        hasil = a / b
    except ZeroDivisionError:
        return "Tidak bisa dibagi dengan nol"
    return hasil

def evaluasi_kelayakan(umur, pendapatan, skor_kredit):
    if umur >= 21:
        if pendapatan > 3000000 and skor_kredit >= 600:
            return "Disetujui"
        else:
            return "Ditolak: Pendapatan atau skor kredit tidak memenuhi"
    else:
        return "Ditolak: Umur belum cukup"


def tentukan_grade(rata_rata):
    if rata_rata >= 85:
        return 'A'
    elif rata_rata >= 75:
        return 'B'
    elif rata_rata >= 65:
        return 'C'
    elif rata_rata >= 50:
        return 'D'
    else:
        return 'E'
    
    
def evaluasi_mahasiswa(data_mahasiswa):
    hasil = {}
    for nama, nilai in data_mahasiswa.items():
            rata_rata = hitung_rata_rata(nilai)
            grade = tentukan_grade(rata_rata)
            hasil[nama] = {
                'nilai': nilai,
                'rata_rata': rata_rata,
                'grade': grade,
                'status': 'Lulus' if grade in ['A', 'B', 'C'] else 'Tidak Lulus'
            }
    return hasil


def tampilkan_hasil(hasil):
    for nama, info in hasil.items():
        print(f"Nama: {nama}")
        if 'error' in info:
            return "error"
        else:
            print(f"  Nilai: {info['nilai']}")
            print(f"  Rata-rata: {info['rata_rata']:.2f}")
            print(f"  Grade: {info['grade']}")
            print(f"  Status: {info['status']}")
        print("-" * 30)
        
def ulang_teks(teks, jumlah):
    for _ in range(jumlah):
        print(teks)
        
def test_loop(n):
    for i in range(n):
        print(i)
    print("Selesai")


def complext_program(limit):
  total = 0
  for i in range(1, limit + 1):
    if i % 2 == 0:
      for j in range(1, 4):
        if j % 2 == 0:
          total += i * j
        else:
          total -= i * j
    else:
      total += i
  if total > 50:
    return "Total is high"
  elif total == 50:
    return "Total is exactly 50"
  else:
    return "Total is low"

def test(a,b):
  if a != 0 and b != 0:
    if a > b:
      print("a besar dari b")
    else:
      for i in range(1, 5):
        print("hallo")
  else:
    for i in range(1,5):
      print("a dan b 0")
      
      
def proses_topup(jumlah, pin_benar, input_pin):
    percobaan = 1
    
    while percobaan <= 3:
        if input_pin == pin_benar:    
            if jumlah >= 10000:          
                return "Sukses"          
            else:
                return "Minimal 10rb"    
        else:
            percobaan += 1               
    
    return "Akun Terblokir"            

#"Input (jumlah, pin, input)",Output,Jalur (Line Numbers),Kategori Jalur
#Jalur A,"20000, 123, 123","""Sukses""","[1, 2, 3, 4, 5, 6]",Happy Path (Kondisi Ideal)
#Jalur B,"5000, 123, 123","""Min 10rb""","[1, 2, 3, 4, 5, 7]",Validation Path (Gagal di validasi saldo)
#Jalur C,"20000, 123, 000","""Terblokir""","[1, 2, 3, 4, 8, 3, 4, 8, 3, 4, 8, 3, 9]",Looping Path (Gagal karena perulangan habis)


def analisis_kesehatan(berat, tinggi, usia):
    bmi = berat / (tinggi * tinggi)
    
    if bmi < 18.5:
        status = "Underweight"
    elif bmi < 25:
        status = "Normal"      
    else:
        status = "Overweight" 
        
    if status == "Normal":    
        return "Pertahankan" 
    
    saran_porsi = 0
    while saran_porsi < 2:    
        saran_porsi += 1       
        
    return "Konsultasi Dokter" 

def cetak_kotak(sisi):
    for i in range(sisi):
        for j in range(sisi):
            print("*", end=" ") 
        
        print() 
    
    return "Selesai"

#test case = 0 dan 2