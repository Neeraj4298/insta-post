import gc
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from backend.utils.files import get_project_dir, load_project_metadata, save_project_metadata

def transcribe_audio_file(
    audio_path: str,
    model_name: str = "base",
    device: str = "cpu",
    compute_type: str = "int8",
    beam_size: int = 3
) -> Dict[str, Any]:
    """
    Transcribes audio file using faster-whisper on CPU INT8.
    Returns dictionary with language and list of segments with timestamps.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    from faster_whisper import WhisperModel  # type: ignore

    # Load model
    model = WhisperModel(model_name, device=device, compute_type=compute_type)

    try:
        segments_generator, info = model.transcribe(
            audio_path,
            beam_size=beam_size,
            word_timestamps=False
        )

        segments = []
        for i, segment in enumerate(segments_generator, start=1):
            segments.append({
                "id": i,
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip()
            })

        result = {
            "language": info.language,
            "duration_seconds": round(info.duration, 2),
            "segments": segments
        }
        return result

    finally:
        # Free memory (critical for 8 GB RAM laptop)
        del model
        gc.collect()

def transcribe_project_audio(
    project_id: str,
    model_name: str = "base",
    compute_type: str = "int8"
) -> Dict[str, Any]:
    """
    Transcribes project audio WAV file and saves transcript.json.
    Updates project metadata status to TRANSCRIBED.
    """
    meta = load_project_metadata(project_id)
    audio_path = meta.get("audio_path")

    if not audio_path or not os.path.exists(audio_path):
        meta["status"] = "FAILED"
        meta["error_message"] = "Audio file not found for transcription"
        save_project_metadata(project_id, meta)
        raise FileNotFoundError(f"Audio file for project {project_id} not found at {audio_path}")

    meta["status"] = "TRANSCRIBING"
    save_project_metadata(project_id, meta)

    try:
        res = transcribe_audio_file(audio_path, model_name=model_name, compute_type=compute_type)

        project_dir = get_project_dir(project_id)
        transcript_path = project_dir / "transcript" / "transcript.json"

        transcript_data = {
            "project_id": project_id,
            "language": res["language"],
            "duration_seconds": res["duration_seconds"],
            "segments": res["segments"]
        }

        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=2)

        meta["status"] = "TRANSCRIBED"
        meta["transcript_path"] = str(transcript_path)
        save_project_metadata(project_id, meta)

        return transcript_data

    except Exception as e:
        meta["status"] = "FAILED"
        meta["error_message"] = str(e)
        save_project_metadata(project_id, meta)
        raise e
