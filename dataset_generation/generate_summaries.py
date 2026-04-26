import os
import json
import zipfile
import time
from razdel import sentenize
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("google/mt5-base")

INPUT_PATH = "processed_texts"
OUTPUT_ZIP = "summaries.zip"
TEMP_DIR = "unzipped_filtered"
OUT_DIR = "summaries"
MODEL = "gpt-4o-mini"
MAX_TOKENS = 512
THREADS = 10
SLEEP_BETWEEN_REQUESTS = 0.6

API_KEY = ""
client = OpenAI(api_key=API_KEY)


def count_tokens(text):
    encoded = tokenizer.encode(text, add_special_tokens=False)
    return len(encoded)


def chunk_text(text, max_tokens=MAX_TOKENS):
    sentences = [s.text for s in sentenize(text)]

    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        sentence_tokens = tokenizer.encode(sentence, add_special_tokens=False)

        if len(sentence_tokens) > max_tokens:
            for i in range(0, len(sentence_tokens), max_tokens):
                piece_tokens = sentence_tokens[i:i+max_tokens]
                piece = tokenizer.decode(piece_tokens)
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                chunks.append(piece.strip())
            continue

        if current_chunk:
            test_chunk = current_chunk + " " + sentence
        else:
            test_chunk = sentence

        token_count = len(tokenizer.encode(test_chunk, add_special_tokens=False))

        if token_count > max_tokens:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk = test_chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# Prompt (EN translation):
# You are a neutral factual summarization model for analytical text.
# Generate 3–7 short sentences with key facts and statements from the author.
# The text may contain rhetoric, emotions, sarcasm, or exaggeration — do not reproduce them literally.
# If a statement is an opinion or assumption, clearly indicate that it is the author's position.
# Do not add new information.
# Write neutrally, without emotions or quotes.
# Format: fact1. fact2. fact3. Up to 80 words.

def summarize_text(text):
    system_content = """
    Ти — модель нейтральної фактологічної сумаризації аналітичного тексту.
    Сформулюй 3–7 коротких речень із ключових фактів і тверджень автора.
    Текст може містити риторику, емоції, сарказм або перебільшення -їх не відтворюй буквально.
    Якщо твердження є оцінкою або припущенням, чітко вказуй, що це позиція або оцінка автора.
    Не додавай нової інформації.
    Пиши нейтрально, без емоцій і цитат.
    Формат: факт1. факт2. факт3. До 80 слів.
    """

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error {type(e).__name__}, attempt {attempt+1}/3")
            time.sleep(2 ** attempt)
    return "Failed to get response"


def process_file(filepath):
    filename = os.path.basename(filepath)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()

        chunks = chunk_text(text)
        result = {"file": filename, "chunks": []}

        for i, chunk in enumerate(chunks, 1):
            print(f"[{os.getpid()}] {filename} | {i}/{len(chunks)}")

            summary = summarize_text(chunk)
            orig_tokens = count_tokens(chunk)
            summ_tokens = count_tokens(summary)

            print(f"[{os.getpid()}] {filename} | {i}/{len(chunks)} | {orig_tokens}->{summ_tokens} tokens")

            result["chunks"].append({"text": chunk, "summary": summary})
            time.sleep(SLEEP_BETWEEN_REQUESTS)

        json_path = os.path.join(OUT_DIR, f"{os.path.splitext(filename)[0]}.json")
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(result, jf, ensure_ascii=False, indent=2)

        return filename
    except Exception as e:
        print(f"Error in {filename}: {e}")
        return None


def main():
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    if os.path.isfile(INPUT_PATH) and INPUT_PATH.endswith(".zip"):
        print(f"Unzipping {INPUT_PATH}...")
        with zipfile.ZipFile(INPUT_PATH, "r") as zip_ref:
            zip_ref.extractall(TEMP_DIR)
        source_dir = TEMP_DIR
    elif os.path.isdir(INPUT_PATH):
        print(f"Using folder {INPUT_PATH}")
        source_dir = INPUT_PATH
    else:
        raise ValueError("INPUT_PATH must be a .zip file or a folder")

    txt_files = [os.path.join(source_dir, f) for f in os.listdir(source_dir) if f.endswith(".txt")]
    print(f"Found {len(txt_files)} files. Running {THREADS} threads...")

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(process_file, f): f for f in txt_files}
        for future in as_completed(futures):
            fname = os.path.basename(futures[future])
            try:
                result = future.result()
                if result:
                    print(f"Completed: {fname}")
            except Exception as e:
                print(f"{fname} failed: {e}")

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filename in os.listdir(OUT_DIR):
            zipf.write(os.path.join(OUT_DIR, filename), arcname=filename)

    print("Done! Archive created:", OUTPUT_ZIP)


if __name__ == "__main__":
    main()