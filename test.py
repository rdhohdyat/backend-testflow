def example(x, y):
  if x > y:
    return x
  else:
    return y

def cek_genap_ganjil(angka):
    if angka % 2 == 0:
        return "Genap"
    else:
        return "Ganjil"
    
def faktorial(n):
    if n == 0:
        return 1
    else:
        return n * faktorial(n - 1)
    
def jumlah_ganjil(n):
    start = 1
    for i in range(start, n):
        if i % 2 == 1:
            total += i
    return total
  
  
def percabangan(x, y):
    if x > y:
        for i in range(1,5):
            print("hello")
    else:
        print("test")
        
def perulangan(a):
    for i in range(1, a):
        for j in range(1, a):
            print("hallo")
        
def luas_persegi_panjang(panjang, lebar):
    if panjang > 0 and lebar > 0:
        return panjang * lebar
    else:
        print("Panjang dan lebar harus lebih besari dari 0!")
        
def perulangan(a, b):
    hasil = 0
    if(b > a):
        for i in range(a, b):
            hasil += i
    else:
        return "b kecil dari a"
    return hasil

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


def analisis_bilangan(angka):
    i = 1
    jumlah_genap = 0
    jumlah_ganjil = 0
    jumlah_kelipatan_5 = 0
    total = 0

    if angka <= 0:
        print("Masukkan harus lebih dari nol.")
        return

    while i <= angka:
        total += i

        if i % 2 == 0:
            print(f"{i} adalah genap")
            jumlah_genap += 1
            if i % 4 == 0:
                print(f"{i} juga kelipatan 4")
        elif i % 5 == 0:
            print(f"{i} adalah kelipatan 5")
            jumlah_kelipatan_5 += 1
        else:
            print(f"{i} adalah ganjil")
            jumlah_ganjil += 1

        i += 1

    print("\nRingkasan:")
    print(f"Total: {total}")
    print(f"Jumlah genap: {jumlah_genap}")
    print(f"Jumlah ganjil: {jumlah_ganjil}")
    print(f"Jumlah kelipatan 5: {jumlah_kelipatan_5}")
