import os
from pathlib import Path
from typing import List, Dict, Any

def format_timestamp_srt(seconds: float) -> str:
    """Converts seconds float to SRT timestamp format 00:00:00,000."""
    millis = int(round((seconds - int(seconds)) * 1000))
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_srt_subtitles(
    segments: List[Dict[str, Any]],
    clip_start: float,
    clip_end: float,
    output_srt_path: str
) -> str:
    """
    Generates an SRT subtitle file for a clip, adjusting segment timestamps
    relative to the clip start time (00:00:00,000).
    """
    output_dir = os.path.dirname(output_srt_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    srt_entries = []
    entry_index = 1

    for seg in segments:
        seg_start = seg.get("start", 0.0)
        seg_end = seg.get("end", 0.0)
        text = seg.get("text", "").strip()

        # Check segment overlap with clip window
        if max(seg_start, clip_start) < min(seg_end, clip_end) and text:
            # Shift timestamps relative to clip start
            rel_start = max(0.0, seg_start - clip_start)
            rel_end = min(clip_end - clip_start, seg_end - clip_start)

            if rel_end > rel_start:
                srt_entries.append(
                    f"{entry_index}\n"
                    f"{format_timestamp_srt(rel_start)} --> {format_timestamp_srt(rel_end)}\n"
                    f"{text.upper()}\n"
                )
                entry_index += 1

    content = "\n".join(srt_entries)
    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_srt_path
