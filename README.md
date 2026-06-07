# Video Thumbnail Generator

Aplikasi web untuk menghasilkan thumbnail video secara otomatis menggunakan Python FastAPI dan FFmpeg.

## Fitur

* Upload video
* Preview video sebelum upload
* Generate thumbnail otomatis berdasarkan interval
* Download thumbnail
* Download seluruh thumbnail dalam format ZIP

## Teknologi

* Python 3.14
* FastAPI
* FFmpeg
* Bootstrap 5

## Instalasi

Aktifkan virtual environment:

venv\Scripts\activate

Install dependency:

pip install -r requirements.txt

Jalankan aplikasi:

uvicorn app.main:app --reload

Buka browser:

http://127.0.0.1:8000
