# Ukrainian Content Summarization Pipeline

This project provides an end-to-end pipeline for abstractive summarization of Ukrainian multimedia content based on speech.

The system processes audio and video inputs, performs automatic speech recognition (ASR), and generates concise summaries of the transcribed content.

## Overview

The application supports summarization from:

- YouTube links  
- Audio files  
- Video files  

The pipeline follows a standard cascade approach:

Audio / Video → ASR (speech-to-text) → Text → Summarization

The system is designed to work with noisy, real-world transcriptions and focuses on Ukrainian-language content.

## Features

- Automatic transcription of multimedia content  
- Abstractive summarization of transcribed text  
- Support for long-form content via chunking  
- Modular pipeline design  
- Fine-tuned models for Ukrainian summarization  

## Running the Application

### 1. Clone the repository

```bash
git clone https://github.com/moisamidi/ukr-content-summarization-pipeline.git
cd ukr-content-summarization-pipeline
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Linux / Mac:
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
uvicorn app.main:app --reload
```

### 5. Access the API

After starting the server, the API will be available at the configured host and port.

By default:
http://127.0.0.1:8000

You can open this address in your browser or use an API client (e.g., Postman).

## Example Usage

You can provide:

- a YouTube URL  
- a local audio file  
- a local video file  

The system will return a generated summary of the content.

## Dataset Creation

The project includes a dedicated module for building custom datasets:

dataset_creation/

This module allows you to:

- collect YouTube links into a single input file  
- download and transcribe content  
- split transcripts into chunks  
- generate pseudo-labels using an LLM (via your API key)  

As a result, the pipeline produces a dataset in JSON format where:

- each file corresponds to a single video  
- each file contains:
  - segmented text chunks  
  - corresponding summaries  

This forms text–summary pairs suitable for training summarization models.

## Experiments

The repository includes an `experiments/` directory containing:

- experiment results  
- scripts used for running experiments  
- artifacts generated during experiments 

The contents may vary depending on the specific experiment and configuration.

## Models

Fine-tuned summarization models are available on Hugging Face:

- https://huggingface.co/moisamidi/yt-summarizer-v1-short-p1  
- https://huggingface.co/moisamidi/yt-summarizer-v2-short-ft-p2  
- https://huggingface.co/moisamidi/yt-summarizer-v3-short-mixed  
- https://huggingface.co/moisamidi/yt-summarizer-v4-short-full-p2  

## Datasets

Corresponding datasets:

- https://huggingface.co/datasets/moisamidi/yt-dataset-short-v1-jsonl-split  
- https://huggingface.co/datasets/moisamidi/yt-dataset-short-v2-jsonl-split  
- https://huggingface.co/datasets/moisamidi/yt-dataset-short-v2-jsonl-split  
- https://huggingface.co/datasets/moisamidi/yt-dataset-short-v4-jsonl-split  

## Notes

- The system is designed for Ukrainian language processing  
- Performance depends on transcription quality  
- The pipeline can be extended with custom models or datasets  
