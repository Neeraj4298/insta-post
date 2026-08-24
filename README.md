# ClipForge Local (`instassist`)

> Local-first AI-powered video clip extraction tool optimized for low-resource environments (8 GB RAM, CPU INT8 processing, zero paid APIs).

## 🚀 Overview

**ClipForge Local** ingests long-form video content (YouTube URLs or local MP4 files), transcribes audio locally using `faster-whisper`, extracts high-potential short-form moments via local LLM analysis, and renders captioned 9:16 vertical reels using FFmpeg.

---

## 💻 Running the Application

### 1. Start FastAPI Backend

```bash
# Activate virtual environment
source venv/bin/activate

# Start backend dev server
uvicorn backend.main:app --reload --port 8000
```

### 2. Start React Frontend Dashboard

```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🛠️ Repository Architecture & Phases

### 📦 Phase 1 - Video Ingestion & Audio Extraction
- Validates YouTube URLs / local files.
- Downloads video via `yt-dlp` to `data/projects/<id>/source/video.mp4`.
- Converts audio to 16kHz mono WAV (`data/projects/<id>/audio/audio.wav`).

### 🎙️ Phase 2 - Local Transcription Engine
- Transcribes audio using `faster-whisper` (CPU INT8 quantization).
- Unloads models and clears RAM after execution for 8 GB RAM systems.
- Saves `data/projects/<id>/transcript/transcript.json`.

### 🧠 Phase 3 - Clip Intelligence & Potential Scoring
- Groups transcript into 2–5 min semantic chunks.
- Runs local Ollama LLM (`http://localhost:11434`) or fallback NLP heuristic detector.
- Scores candidates out of 100 based on Hook (25%), Context (25%), Completeness (20%), Emotion (15%), Curiosity (10%), and Shareability (5%).

### 🏆 Phase 4 - Candidate Ranking & Deduplication
- Deduplicates overlapping timestamp ranges (retains higher score).
- Applies $\ge 60$s timeline diversity spacing.
- Saves top ranked clips to `data/projects/<id>/analysis/ranked_clips.json`.

### 💻 Phase 5 - Interactive Web UI Dashboard (`frontend/`)
- Built with React, Vite, and Lucide React icons.
- Features URL/path input bar, live status pipeline monitor, score breakdown sliders, and built-in reel preview player.

### 🎬 Phase 6 - FFmpeg 9:16 Video Renderer & Subtitle Burner
- Trims video to exact candidate timestamps `[start, end]`.
- Center crops 16:9 widescreen to 9:16 vertical reel ($1080 \times 1920$).
- Generates SRT subtitles and burns styled captions onto exported MP4 reels (`data/projects/<id>/output/`).

---

## 🧪 Automated Testing

Run the full pytest suite (22 unit & integration tests):

```bash
source venv/bin/activate
pytest -v
```
