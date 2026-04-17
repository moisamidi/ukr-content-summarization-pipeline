from faster_whisper import WhisperModel
from app.services.config import DEVICE, WHISPER_COMPUTE_TYPE

model = WhisperModel(
    "large",
    device=DEVICE,
    compute_type=WHISPER_COMPUTE_TYPE
)


def transcribe_segments(audio_path, language=None):
    print(f"[INFO] Starting transcription: {audio_path}")

    segments, info = model.transcribe(
        audio_path,
        language=language
    )

    detected_language = info.language
    print(f"[INFO] Detected language: {detected_language}")

    if detected_language != "uk":
        raise ValueError(f"Unsupported language detected: {detected_language}")

    segments_list = []

    for seg in segments:
        segments_list.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text
        })

    print(f"[INFO] Transcription completed, segments: {len(segments_list)}")

    return segments_list