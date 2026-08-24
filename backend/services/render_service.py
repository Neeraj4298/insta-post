import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.utils.files import get_project_dir, load_project_metadata, save_project_metadata
from backend.utils.ffmpeg import get_ffmpeg_path
from backend.utils.subtitles import generate_srt_subtitles

def render_single_clip(
    video_path: str,
    start: float,
    end: float,
    output_mp4_path: str,
    srt_path: Optional[str] = None,
    aspect_ratio: str = "9:16"
) -> str:
    """
    Renders a video clip with FFmpeg:
    - Cuts timestamps [start, end]
    - Center crops to 9:16 vertical (1080x1920) or maintains 16:9
    - Burns subtitles if srt_path is provided
    """
    ffmpeg_exe = get_ffmpeg_path()
    output_dir = os.path.dirname(output_mp4_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    filter_chains = []

    if aspect_ratio == "9:16":
        # 16:9 to 9:16 center crop filter
        filter_chains.append("crop=ih*9/16:ih:(iw-ow)/2:0,scale=1080:1920")

    if srt_path and os.path.exists(srt_path):
        # Escape path for FFmpeg subtitles filter on Linux
        escaped_srt = srt_path.replace(":", "\\:").replace("'", "\\'")
        sub_filter = (
            f"subtitles='{escaped_srt}':force_style="
            f"'Fontname=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=60'"
        )
        filter_chains.append(sub_filter)

    vf_argument = ",".join(filter_chains)

    cmd = [
        ffmpeg_exe, "-y",
        "-ss", str(start),
        "-to", str(end),
        "-i", video_path
    ]

    if vf_argument:
        cmd.extend(["-vf", vf_argument])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "128k",
        output_mp4_path
    ])

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg rendering failed: {res.stderr}")

    return output_mp4_path

def render_project_clips(
    project_id: str,
    clip_ids: Optional[List[str]] = None,
    aspect_ratio: str = "9:16"
) -> List[Dict[str, Any]]:
    """
    Renders selected or top ranked clips for a project.
    Generates subtitles, performs center cropping, and exports MP4 reels.
    """
    meta = load_project_metadata(project_id)
    video_path = meta.get("video_path")
    ranked_path = meta.get("ranked_clips_path")
    transcript_path = meta.get("transcript_path")

    if not video_path or not os.path.exists(video_path):
        raise FileNotFoundError(f"Source video file for project {project_id} not found.")

    if not ranked_path or not os.path.exists(ranked_path):
        raise FileNotFoundError(f"Ranked clips file for project {project_id} not found.")

    meta["status"] = "RENDERING"
    save_project_metadata(project_id, meta)

    try:
        with open(ranked_path, "r", encoding="utf-8") as f:
            ranked_clips = json.load(f)

        # Load transcript segments for subtitles if available
        segments = []
        if transcript_path and os.path.exists(transcript_path):
            with open(transcript_path, "r", encoding="utf-8") as f:
                tdata = json.load(f)
                segments = tdata.get("segments", [])

        # Filter by clip_ids if specified
        target_clips = ranked_clips
        if clip_ids:
            target_clips = [c for c in ranked_clips if c.get("candidate_id") in clip_ids]

        project_dir = get_project_dir(project_id)
        output_dir = project_dir / "output"
        rendered_results = []

        for idx, clip in enumerate(target_clips, start=1):
            cand_id = clip.get("candidate_id", f"clip_{idx}")
            start_t = clip["start"]
            end_t = clip["end"]

            out_mp4 = str(output_dir / f"{cand_id}.mp4")
            srt_path = str(output_dir / f"{cand_id}.srt")

            # Generate subtitles
            if segments:
                generate_srt_subtitles(segments, start_t, end_t, srt_path)

            # Render single clip
            render_single_clip(
                video_path=str(video_path),
                start=start_t,
                end=end_t,
                output_mp4_path=out_mp4,
                srt_path=srt_path if os.path.exists(srt_path) else None,
                aspect_ratio=aspect_ratio
            )

            rendered_results.append({
                "candidate_id": cand_id,
                "title": clip.get("title"),
                "output_path": out_mp4,
                "srt_path": srt_path if os.path.exists(srt_path) else None,
                "duration": clip.get("duration"),
                "final_score": clip.get("final_score")
            })

        meta["status"] = "COMPLETED"
        meta["rendered_clips"] = rendered_results
        save_project_metadata(project_id, meta)

        return rendered_results

    except Exception as e:
        meta["status"] = "FAILED"
        meta["error_message"] = str(e)
        save_project_metadata(project_id, meta)
        raise e
