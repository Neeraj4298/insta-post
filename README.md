# ClipForge Local (`instassist`)

> Local-first AI-powered video clip extraction tool optimized for low-resource environments (8 GB RAM, CPU INT8 processing, zero paid APIs).

## 🚀 Overview

**ClipForge Local** ingests long-form video content (YouTube URLs or local MP4 files), transcribes audio locally using `faster-whisper`, extracts high-potential short-form moments via local LLM analysis, and renders captioned 9:16 vertical reels using FFmpeg.

---

## 🛠️ Repository Setup

### Virtual Environment

A Python virtual environment is initialized at `./venv`.

To activate the virtual environment:

```bash
source venv/bin/activate
```

### Git Branches

- `development` (Active working branch)
- `main`

Remote URL configured: `https://github.com/neeraj4298/clipforge-local.git`

---

## 📦 Phase 1 - Video Pipeline Implementation (Completed)

Phase 1 provides end-to-end video ingestion and audio extraction:

1. **Video Ingestion**: Accepts YouTube URLs or local video paths, validates input, retrieves media via `yt-dlp` or local file handler, and organizes files into `data/projects/<project_id>/source/video.mp4`.
2. **Audio Extraction**: Extracts 16kHz mono PCM WAV audio using bundled FFmpeg into `data/projects/<project_id>/audio/audio.wav` (optimal sample rate for Whisper transcription).
3. **Structured Storage & Metadata**: Tracks processing status (`CREATED`, `DOWNLOADING`, `DOWNLOADED`, `EXTRACTING_AUDIO`, `AUDIO_EXTRACTED`).

---

## 🎙️ Phase 2 - Transcription Engine (Completed)

Phase 2 transcribes extracted audio files using `faster-whisper` on CPU INT8:

1. **Local Transcription Service**: Leverages `faster-whisper` (CTranslate2 INT8 quantization) for efficient CPU inference without GPU requirements.
2. **Resource Management**: Automatically unloads models and triggers garbage collection to free RAM (optimized for 8 GB RAM systems).
3. **Structured Transcript Storage**: Saves timestamped segment details and detected language to `data/projects/<project_id>/transcript/transcript.json`.
4. **FastAPI & CLI**:
   - `cli_transcribe.py` for testing via command-line.
   - Endpoints: `POST /api/projects/{id}/transcribe` and `GET /api/projects/{id}/transcript`.

---

## 🧪 Testing

Run the automated test suite covering Phase 1 & Phase 2:

```bash
# Activate virtual environment
source venv/bin/activate

# Run pytest
pytest -v
```
