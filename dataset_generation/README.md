# Dataset Creation Pipeline (YouTube → Summaries)

This folder provides a two-stage pipeline for building a Ukrainian summarization dataset from YouTube videos.

YouTube → audio → transcription → chunking → summaries


## Stage 1 — Transcription (YouTube → Text)

Script: `transcribe_youtube_links.py`

### What it does

For each link:
- downloads audio  
- transcribes it with Whisper  
- saves result as `.txt`  

Output:

output/
 ├── video_id_1.txt
 ├── video_id_2.txt


### How to use

1. Create `links.txt`:

```
https://www.youtube.com/watch?v=...
https://www.youtube.com/watch?v=...

```

2. Run:

`python transcribe_youtube_links.py`


### Configuration (optional)

You can adjust:
- model size (`large`, `medium`, `small`)  
- device (`cpu` / `cuda`)  
- output folders (`OUT_DIR`, `TEMP_DIR`)  


### Notes

- Output is raw ASR text (not cleaned)  
- May contain errors and spoken-language artifacts  
- Used as input for the next stage  


## Stage 2 — Summarization (Text → Dataset)

Script: `generate_summaries.py`

### What it does

For each `.txt` file:
- splits text into chunks  
- generates a summary for each chunk  
- saves results as `.json`  

Output:
```
summaries/
 ├── video1.json
 ├── video2.json
```

Each file:

```
{
  "file": "video1.txt",
  "chunks": [
    {
      "text": "...",
      "summary": "..."
    }
  ]
}
```

### How to use

1. Put transcription files into:

`processed_texts/`

(or provide a `.zip` archive)

2. Set your API key:

`API_KEY = "your_key_here"`

3. Run:

`python generate_summaries.py`


### Configuration (optional)

You can adjust:
- model (`MODEL`)  
- max chunk size (`MAX_TOKENS`)  
- number of threads (`THREADS`)  
- summarization prompt (`system_content`)  


### Notes

- Uses LLM to generate summaries (pseudo-labels)  
- Prompt defines summary style and can be customized  
- Output dataset is ready for fine-tuning or experiments  