from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.background import BackgroundTask
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import os
import re
import shutil
import subprocess
import zipfile
import yt_dlp
import gdown

app = FastAPI()

# =====================================
# CONFIG
# =====================================

UPLOAD_DIR = "uploads"
THUMBNAIL_DIR = "thumbnails"
ZIP_DIR = "zips"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)
os.makedirs(ZIP_DIR, exist_ok=True)

# Bersihkan file lama saat startup
for folder in [UPLOAD_DIR, THUMBNAIL_DIR, ZIP_DIR]:

    for item in os.listdir(folder):

        path = os.path.join(folder, item)

        try:

            if os.path.isfile(path):
                os.remove(path)

        except Exception:
            pass

templates = Jinja2Templates(
    directory="templates"
)

app.mount(
    "/thumbnails",
    StaticFiles(directory=THUMBNAIL_DIR),
    name="thumbnails"
)

# =====================================
# HELPER
# =====================================

def sanitize_filename(filename: str) -> str:

    filename = os.path.splitext(filename)[0]

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        filename
    )


def get_video_duration(video_path: str) -> int:

    try:

        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                video_path
            ],
            capture_output=True,
            text=True
        )

        return int(float(result.stdout.strip()))

    except Exception:

        return 0


def download_youtube_video(url: str) -> str:

    ydl_opts = {
        "format": "mp4/best",
        "outtmpl": os.path.join(
            UPLOAD_DIR,
            "%(title)s.%(ext)s"
        ),
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        return ydl.prepare_filename(info)


def download_drive_video(url: str) -> str:

    output = os.path.join(
        UPLOAD_DIR,
        "gdrive_video.mp4"
    )

    gdown.download(
        url,
        output,
        quiet=False,
        fuzzy=True
    )

    return output


# =====================================
# ROUTES
# =====================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post("/upload")
async def upload_video(
    request: Request,
    video: UploadFile = File(None),
    video_url: str = Form(""),
    interval: int = Form(...)
):

    if interval < 1:
        interval = 1

    # =================================
    # VIDEO DARI URL
    # =================================

    if video_url:

        try:

            if (
                "youtube.com" in video_url
                or "youtu.be" in video_url
            ):

                video_path = download_youtube_video(
                    video_url
                )

            elif "drive.google.com" in video_url:

                video_path = download_drive_video(
                    video_url
                )

            else:

                return templates.TemplateResponse(
                    request=request,
                    name="result.html",
                    context={
                        "video": "",
                        "duration": 0,
                        "interval": interval,
                        "total": 0,
                        "thumbnails": [],
                        "error": "URL tidak didukung."
                    }
                )

            video_filename = os.path.basename(
                video_path
            )

        except Exception as e:

            return templates.TemplateResponse(
                request=request,
                name="result.html",
                context={
                    "video": "",
                    "duration": 0,
                    "interval": interval,
                    "total": 0,
                    "thumbnails": [],
                    "error": f"Gagal download video: {str(e)}"
                }
            )

    # =================================
    # VIDEO LOKAL
    # =================================

    else:

        if not video:

            return templates.TemplateResponse(
                request=request,
                name="result.html",
                context={
                    "video": "",
                    "duration": 0,
                    "interval": interval,
                    "total": 0,
                    "thumbnails": [],
                    "error": "Pilih video atau masukkan URL."
                }
            )

        safe_name = sanitize_filename(
            video.filename
        )

        video_filename = safe_name + ".mp4"

        video_path = os.path.join(
            UPLOAD_DIR,
            video_filename
        )

        with open(
            video_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                video.file,
                buffer
            )

    # =================================
    # DURASI VIDEO
    # =================================

    duration = get_video_duration(
        video_path
    )

    if duration <= 0:

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "video": video_filename,
                "duration": 0,
                "interval": interval,
                "total": 0,
                "thumbnails": [],
                "error": "Gagal membaca durasi video."
            }
        )

    # =================================
    # NAMA VIDEO AMAN
    # =================================

    video_name = sanitize_filename(
        video_filename
    )

    # =================================
    # HAPUS THUMBNAIL LAMA
    # =================================

    for file in os.listdir(
        THUMBNAIL_DIR
    ):

        if file.startswith(
            video_name
        ):

            os.remove(
                os.path.join(
                    THUMBNAIL_DIR,
                    file
                )
            )

    thumbnails = []

    # =================================
    # GENERATE THUMBNAIL
    # =================================

    for second in range(
        0,
        duration,
        interval
    ):

        thumbnail_name = (
            f"{video_name}_{second}.jpg"
        )

        thumbnail_path = os.path.join(
            THUMBNAIL_DIR,
            thumbnail_name
        )

        subprocess.run(
            [
                "ffmpeg",
                "-ss",
                str(second),
                "-i",
                video_path,
                "-frames:v",
                "1",
                thumbnail_path,
                "-y"
            ],
            capture_output=True,
            text=True
        )

        if os.path.exists(
            thumbnail_path
        ):

            thumbnails.append(
                thumbnail_name
            )

    # Hapus video setelah selesai diproses

    try:

        os.remove(video_path)

    except Exception:

        pass

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "video": video_filename,
            "video_name": video_name,
            "duration": duration,
            "interval": interval,
            "total": len(
                thumbnails
            ),
            "thumbnails": thumbnails
        }
    )


# =====================================
# DOWNLOAD ZIP
# =====================================

@app.get("/download-zip/{video_name}")
async def download_zip(
    video_name: str
):

    zip_path = os.path.join(
        ZIP_DIR,
        f"{video_name}.zip"
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for file in os.listdir(
            THUMBNAIL_DIR
        ):

            if file.startswith(
                video_name
            ):

                file_path = os.path.join(
                    THUMBNAIL_DIR,
                    file
                )

                zipf.write(
                    file_path,
                    arcname=file
                )

    return FileResponse(
        path=zip_path,
        filename=f"{video_name}.zip",
        media_type="application/zip",
        background=BackgroundTask(
            os.remove,
            zip_path
        )
    )
