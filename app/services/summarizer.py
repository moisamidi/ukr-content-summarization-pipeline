import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from app.services.config import DEVICE, MODEL_NAME, MAX_TOKENS

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

model.to(DEVICE)
model.eval()


def run_model_on_chunk(text, tokenizer, model, device):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_TOKENS,
        padding=False
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_TOKENS,
            max_length=None,
            num_beams=4,
            no_repeat_ngram_size=3,
            repetition_penalty=1.1,
            early_stopping=True
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def summarize_with_two_levels(chunks):
    level1_results = []

    for i, chunk in enumerate(chunks, 1):
        print(f"[INFO] Level-1: processing chunk {i}/{len(chunks)}")

        summary = run_model_on_chunk(chunk, tokenizer, model, DEVICE)
        level1_results.append(summary)

    level1_text = "\n".join(
        r.strip() for r in level1_results if r.strip()
    )

    level2_chunks = []
    current_text = ""
    current_tokens = 0

    for sent in level1_text.split("\n"):
        sent = sent.strip()
        if not sent:
            continue

        tokens = tokenizer.encode(sent, add_special_tokens=False)
        sent_tokens = len(tokens)

        if sent_tokens > MAX_TOKENS:
            for i in range(0, sent_tokens, MAX_TOKENS):
                piece = tokenizer.decode(tokens[i:i+MAX_TOKENS])
                level2_chunks.append(piece.strip())
            continue

        if current_text and current_tokens + sent_tokens > MAX_TOKENS:
            level2_chunks.append(current_text.strip())
            current_text = ""
            current_tokens = 0

        current_text += " " + sent
        current_tokens += sent_tokens

    if current_text:
        level2_chunks.append(current_text.strip())

    print(f"[INFO] Level-2 chunks: {len(level2_chunks)}")

    level2_results = []

    for i, chunk in enumerate(level2_chunks, 1):
        print(f"[INFO] Level-2: processing chunk {i}/{len(level2_chunks)}")

        summary = run_model_on_chunk(chunk, tokenizer, model, DEVICE)
        level2_results.append(summary)

    final_summary = " ".join(level2_results)

    return final_summary, len(chunks)