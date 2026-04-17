import re
from app.services.config import MAX_TOKENS

def smart_chunk_transcript(segments, tokenizer):
    print(f"[INFO] Starting chunking, segments: {len(segments)}")

    full_text = " ".join(seg["text"].strip() for seg in segments)
    full_text = re.sub(r"\s+", " ", full_text)
    sentences = re.split(r'(?<=[.!?])\s+', full_text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        sentence_tokens = tokenizer.encode(sentence, add_special_tokens=False)

        if len(sentence_tokens) > MAX_TOKENS:
            for i in range(0, len(sentence_tokens), MAX_TOKENS):
                piece = tokenizer.decode(sentence_tokens[i:i+MAX_TOKENS])
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                chunks.append(piece.strip())
            continue

        test_chunk = current_chunk + " " + sentence if current_chunk else sentence
        token_count = len(tokenizer.encode(test_chunk, add_special_tokens=False))

        if token_count > MAX_TOKENS:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk = test_chunk

    if current_chunk:
        chunks.append(current_chunk.strip())

    print(f"[INFO] Chunking completed, chunks: {len(chunks)}")
    return chunks