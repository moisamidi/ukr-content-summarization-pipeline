import torch
import os

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

WHISPER_COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"

MAX_TOKENS = 512

MODEL_NAME = "moisamidi/yt-summarizer-v4-short-full-p2"

COOKIES_FILE = os.getenv("COOKIES_FILE")