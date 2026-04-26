from fastapi import FastAPI, UploadFile, File
import os
import shutil
import uuid
from app.services.youtube import download_audio
from app.services.whisper import transcribe_segments
from app.services.chunking import smart_chunk_transcript
from app.services.summarizer import tokenizer, summarize_with_two_levels
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return FileResponse("app/index.html")


@app.post("/summarize")
def summarize_api(url: str):
    try:
        audio_path = download_audio(url)

        segments = transcribe_segments(audio_path)

        chunks = smart_chunk_transcript(
            segments,
            tokenizer=tokenizer
        )

        final_summary, total_chunks = summarize_with_two_levels(chunks)

        if os.path.exists(audio_path):
            os.remove(audio_path)

        return {
            "chunks": total_chunks,
            "summary": final_summary
        }

    except Exception as e:
        print("[ERROR]", e)

        return {
            "error": "Invalid or unavailable YouTube link"
        }


@app.post("/summarize-file")
async def summarize_file(file: UploadFile = File(...)):
    try:
        ext = file.filename.split(".")[-1]
        temp_filename = f"temp_{uuid.uuid4()}.{ext}"
        temp_path = os.path.join("output", temp_filename)

        os.makedirs("output", exist_ok=True)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"[INFO] File saved: {temp_path}")

        segments = transcribe_segments(temp_path)

        chunks = smart_chunk_transcript(
            segments,
            tokenizer=tokenizer
        )

        final_summary, total_chunks = summarize_with_two_levels(chunks)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {
            "chunks": total_chunks,
            "summary": final_summary
        }

    except Exception as e:
        print("[ERROR]", e)

        return {
            "error": "Invalid or unavailable YouTube link"
        }