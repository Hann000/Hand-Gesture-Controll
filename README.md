```markdown
<div align="center">

# 🖐️ PC Gesture Control

**Kontrol kursor, scroll, dan volume PC Anda layaknya pesulap, hanya dengan gestur tangan di depan webcam.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)](#)

Dibangun menggunakan **Python**, **OpenCV**, dan pelacakan canggih dari **MediaPipe Hand Landmarker**.

</div>

---

## 🎬 Demo

*(💡 Tips: Ganti tautan gambar di bawah dengan file `.gif` yang merekam layar saat Anda menggunakan aplikasi ini agar orang langsung paham cara kerjanya!)*

![Demo Aplikasi](https://via.placeholder.com/800x400.png?text=Upload+GIF+Demo+Aplikasi+Anda+Di+Sini)

> **Antarmuka Cerdas (HUD):** Aplikasi ini menampilkan overlay HUD informatif langsung di *feed* kamera Anda. Dilengkapi dengan **Mode Eksklusif**, memastikan hanya satu fitur yang aktif pada satu waktu sehingga gestur Anda tidak akan saling tumpang tindih atau bentrok.

---

## 🎮 Panduan Gestur & Mode

Sistem menggunakan "Mode Eksklusif". Tahan gestur pengalih mode selama **~0.7 detik** (dapat diatur) untuk berpindah fungsi.

| 🎯 Mode | 🔄 Cara Ganti Mode (Tahan Diam) | ⚙️ Cara Operasi |
|:---|:---|:---|
| 🖱️ **Kursor** | Bentuk **Peace Sign / V** (Telunjuk + Tengah) | Arahkan telunjuk di zona aktif HUD. Rapatkan telunjuk+tengah untuk **Klik**. |
| 📜 **Scroll** | Rapatkan **Jempol + Jari Manis** | Tahan jempol+manis, lalu geser tangan perlahan naik atau turun. |
| 🔊 **Volume** | Rapatkan **Jempol + Kelingking** | Tahan telunjuk+tengah untuk *Lock/Unlock*. Gunakan jarak **Jempol & Telunjuk** untuk atur volume. |

> **Catatan:** Untuk kembali ke Mode **Kursor** dari mode manapun, cukup tahan gestur *Peace sign* (V) agak lama. Secara *default*, pengaturan volume dalam keadaan **terkunci** saat Anda baru masuk ke Mode Volume untuk mencegah perubahan suara yang tidak disengaja.

---

## 🚀 Memulai (Instalasi)

### 1. Persyaratan Sistem
* Python 3.8 atau lebih baru
* Webcam yang berfungsi
* OS: Windows / macOS / Linux

### 2. Langkah Instalasi

Clone repositori ini dan masuk ke dalam foldernya:
```bash
git clone [https://github.com/Hann000/Hand-Gesture-Controll.git](https://github.com/Hann000/Hand-Gesture-Controll.git)
cd gesture-control```

Buat dan aktifkan *Virtual Environment* (Direkomendasikan):

```bash
# Untuk Windows:
python -m venv venv
venv\Scripts\activate

# Untuk macOS / Linux:
python -m venv venv
source venv/bin/activate

```

Instal dependensi dan unduh model AI:

```bash
pip install -r requirements.txt
python download_model.py

```

*(Skrip `download_model.py` akan otomatis mengunduh file `hand_landmarker.task` ke dalam folder `models/`)*.

---

## 💻 Cara Menjalankan Aplikasi

Jalankan perintah berikut di terminal Anda:

```bash
python main.py

```

*Tekan tombol **`Q`** pada keyboard saat jendela kamera aktif untuk keluar dari aplikasi.*

---

## ⚙️ Konfigurasi Lanjutan

Anda dapat menyesuaikan sensitivitas dan perilaku aplikasi dengan mengedit file `config.py`. Berikut adalah parameter utamanya:

| Parameter | Default | Efek jika diubah |
| --- | --- | --- |
| `CURSOR_ZONE_MIN_X` | `0.12` | Batas zona kursor. Semakin besar nilainya, semakin sedikit gerakan tangan yang dibutuhkan untuk mencapai ujung layar. |
| `SMOOTHING_ALPHA` | `0.2` | Tingkat kehalusan kursor. Nilai lebih kecil = pergerakan lebih halus (mengurangi getaran). |
| `CLICK_THRESHOLD` | `0.05` | Sensitivitas gestur klik. |
| `SCROLL_STEP` | `4` | Pengali kecepatan gulir (scroll) halaman. |
| `MODE_SWITCH_HOLD_SEC` | `0.7` | Durasi (detik) Anda harus menahan gestur untuk berganti mode. |
| `VOL_MIN_DIST` | `0.03` | Jarak minimum cubitan jari untuk volume 0%. |
| `VOL_MAX_DIST` | `0.30` | Jarak maksimum rentangan jari untuk volume 100%. |

---

## 🛠️ Troubleshooting (Penyelesaian Masalah)

| ⚠️ Masalah yang Sering Terjadi | 💡 Solusi |
| --- | --- |
| **Kamera tidak terbuka** | Buka `config.py` dan ubah nilai `CAMERA_INDEX` (coba ganti ke `0`, `1`, atau `2`). |
| **Model AI tidak ditemukan** | Pastikan Anda sudah menjalankan `python download_model.py`. |
| **Kursor bergetar parah (Jittering)** | Turunkan nilai `SMOOTHING_ALPHA` di `config.py` ke `0.1` atau `0.15`. |
| **Teks UI tampil aneh/kotak-kotak** | Pastikan nama perangkat atau input hanya menggunakan karakter ASCII. |
| **Volume tidak berubah (Khusus Windows)** | Pastikan *library* audio terinstal: jalankan `pip install pycaw comtypes`. |

---

## 📂 Struktur Proyek

```text
gesture-control/
├── main.py                 # Entry point / File utama
├── config.py               # Konfigurasi parameter & konstanta
├── mode_controller.py      # Logika eksklusif & transisi gestur
├── hand_tracker.py         # Modul pelacakan landmark tangan (MediaPipe)
├── cursor_controller.py    # Logika mouse & penghalusan (EMA smoothing)
├── scroll_controller.py    # Logika gulir vertikal
├── volume_controller.py    # Kontrol volume master sistem
├── gesture_detector.py     # Deteksi status jari & klik
├── ui_overlay.py           # Logika rendering HUD di layar
├── ui_theme.py             # Palet warna & helper desain UI
├── download_model.py       # Skrip pengunduh model pelacakan otomatis
├── models/                 # Direktori penyimpanan model AI (.task)
├── requirements.txt        # Daftar dependensi Python
└── README.md               # Dokumentasi proyek

```

---

## 🧠 Teknologi di Balik Layar

* **[MediaPipe Hand Landmarker](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker)** - Mesin utama untuk mendeteksi 21 titik landmark tangan secara *real-time*.
* **[OpenCV](https://opencv.org/)** - Untuk menangkap *feed* kamera dan menggambar antarmuka visual (HUD).
* **[PyAutoGUI](https://pyautogui.readthedocs.io/)** - Mentranslasikan koordinat tangan menjadi pergerakan dan klik mouse OS.
* **[pycaw](https://github.com/AndreMiras/pycaw)** - Mengatur level audio sistem pada Windows.

---

## 📄 Lisensi

Proyek ini dibangun untuk tujuan edukasi dan open-source. Bebas untuk dimodifikasi dan dikembangkan lebih lanjut. *Catatan: Model MediaPipe dilisensikan dan dikelola oleh Google.*
