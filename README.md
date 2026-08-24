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
2. **Audio Extraction**: Extracts 16kHz mono PCM WAV audio using bundled FFmpeg into `data/projects/<project_id>/audio/audio.wav`.

---

## 🎙️ Phase 2 - Transcription Engine (Completed)

Phase 2 transcribes extracted audio files using `faster-whisper` on CPU INT8:

1. **Local Transcription Service**: Leverages `faster-whisper` (CTranslate2 INT8 quantization) for efficient CPU inference without GPU requirements.
2. **Resource Management**: Automatically unloads models and triggers garbage collection to free RAM.
3. **Structured Transcript Storage**: Saves timestamped segment details and detected language to `data/projects/<project_id>/transcript/transcript.json`.

---

## 🧠 Phase 3 - Clip Intelligence & Potential Scoring (Completed)

Phase 3 analyzes transcripts to identify standalone 15s–90s short-form reel moments:

1. **Semantic Chunker (`backend/engines/chunker.py`)**: Groups segments into 2–5 minute chunks based on pause gaps and sentence boundaries.
2. **Candidate Detector (`backend/engines/candidate_detector.py`)**:
   - Integrates local LLM (Ollama `http://localhost:11434`) when active.
   - Includes a deterministic heuristic/NLP fallback engine for offline execution.
3. **Clip Potential Scoring Engine (`backend/engines/scoring_engine.py`)**:
   - Computes weighted score out of 100 based on formula:
     $\text{Score} = (\text{Hook} \times 0.25 + \text{Context} \times 0.25 + \text{Completeness} \times 0.20 + \text{Emotion} \times 0.15 + \text{Curiosity} \times 0.10 + \text{Shareability} \times 0.05) \times 10$
4. **Data Storage & API/CLI**:
   - Saves candidates to `data/projects/<project_id>/analysis/candidates.json`.
   - `cli_analyze.py` for command-line intelligence testing.
   - Endpoints: `POST /api/projects/{id}/analyze` and `GET /api/projects/{id}/candidates`.

---

## 🧪 Testing

Run the automated test suite covering Phases 1, 2, & 3:

```bash
# Activate virtual environment
source venv/bin/activate

# Run pytest
pytest -v
```
