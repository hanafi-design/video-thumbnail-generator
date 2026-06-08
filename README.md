# Video Thumbnail Generator

## Deskripsi

Video Thumbnail Generator adalah aplikasi berbasis FastAPI yang digunakan untuk menghasilkan thumbnail secara otomatis dari video lokal, YouTube, maupun Google Drive menggunakan FFmpeg.

## Fitur

* Upload video lokal
* Download video dari YouTube
* Download video dari Google Drive
* Generate thumbnail berdasarkan interval waktu
* Download seluruh thumbnail dalam format ZIP
* UI modern dan responsif

## Teknologi

* Python
* FastAPI
* Jinja2
* Bootstrap 5
* FFmpeg
* yt-dlp
* gdown

## Instalasi

### Clone Repository

git clone https://github.com/hanafi-design/video-thumbnail-generator.git

### Masuk Folder

cd video-thumbnail-generator

### Buat Virtual Environment

python -m venv venv

### Aktifkan Virtual Environment

venv\Scripts\activate

### Install Dependency

pip install -r requirements.txt

### Jalankan Aplikasi

uvicorn app.main:app --reload

### Buka Browser

http://127.0.0.1:8000

## Author

Riski Hanafi
Politeknik Elektronika Negeri Surabaya
