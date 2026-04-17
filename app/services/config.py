import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

WHISPER_COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"

MAX_TOKENS = 512

MODEL_NAME = "moisamidi/yt-summarizer-mt5"