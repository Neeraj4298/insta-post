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

1. **Semantic Chunker**: Groups segments into 2–5 minute chunks based on pause gaps and sentence boundaries.
2. **Candidate Detector**: Integrates local LLM (Ollama) with heuristic/NLP fallback engine for offline candidate discovery.
3. **Scoring Engine**: Computes weighted score out of 100 based on formula ($\text{Hook} \cdot 0.25 + \text{Context} \cdot 0.25 + \text{Completeness} \cdot 0.20 + \text{Emotion} \cdot 0.15 + \text{Curiosity} \cdot 0.10 + \text{Shareability} \cdot 0.05) \cdot 10$.

---

## 🏆 Phase 4 - Candidate Ranking & Deduplication Engine (Completed)

Phase 4 filters and ranks candidate clips into the Top 10 reel moments:

1. **Overlap Removal (`backend/engines/deduplicator.py`)**: Identifies timestamp overlaps and keeps only the highest-scoring candidate.
2. **Timeline Diversity Spacing**: Ensures clips are spaced at least 60 seconds apart across the video timeline.
3. **Score Thresholding**: Filters clips with $\text{Clip Potential Score} \ge 65.0$.
4. **Data Storage & API/CLI**:
   - Saves ranked clips to `data/projects/<project_id>/analysis/ranked_clips.json`.
   - Sets project status to `READY_FOR_REVIEW`.
   - `cli_rank.py` for command-line ranking tests.
   - Endpoints: `POST /api/projects/{id}/rank` and `GET /api/projects/{id}/ranked`.

---

## 🧪 Testing

Run the automated test suite covering Phases 1, 2, 3, & 4:

```bash
# Activate virtual environment
source venv/bin/activate

# Run pytest
pytest -v
```
