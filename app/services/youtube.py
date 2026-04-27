import os
import subprocess
from app.services.config import COOKIES_FILE

OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)


def download_audio(youtube_url):
    print(f"[INFO] Downloading audio from URL: {youtube_url}")
    output_template = os.path.join(OUT_DIR, "%(id)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", output_template,
    ]

    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        cmd.extend(["--cookies", COOKIES_FILE])

    cmd.append(youtube_url)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] yt-dlp failed: {result.stderr}")
        raise RuntimeError(result.stderr)

    video_id = youtube_url.split("v=")[-1].split("&")[0]

    for ext in ["mp3", "webm", "m4a"]:
        audio_path = os.path.join(OUT_DIR, f"{video_id}.{ext}")
        if os.path.exists(audio_path):
            print(f"[INFO] Audio downloaded: {audio_path}")
            return audio_path

    raise FileNotFoundError("Audio file not found")