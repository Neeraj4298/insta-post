#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.services.render_service import render_project_clips
from backend.utils.files import load_project_metadata

def main():
    parser = argparse.ArgumentParser(description="Phase 6: FFmpeg Video Renderer & Subtitle Burner CLI")
    parser.add_argument("project_id", help="Project ID with ranked clips (Phase 4)")
    parser.add_argument("--aspect_ratio", help="Target aspect ratio (9:16 or 16:9)", default="9:16")

    args = parser.parse_args()

    print("==================================================")
    print("      ClipForge Local - Phase 6 Rendering        ")
    print("==================================================")
    print(f"Project ID: {args.project_id}")
    print(f"Aspect Ratio: {args.aspect_ratio}")

    try:
        meta = load_project_metadata(args.project_id)
        print(f"Source Video: {meta.get('video_path')}")

        print("\nTrimming timestamps, cropping 9:16, generating & burning subtitles...")
        rendered = render_project_clips(args.project_id, aspect_ratio=args.aspect_ratio)

        print(f"\n✓ Rendering complete! Created {len(rendered)} MP4 reels.")

        print("\n🎬 Exported Reels:")
        for idx, reel in enumerate(rendered, start=1):
            print(f"\n[{idx}] Candidate ID: {reel['candidate_id']}")
            print(f"    Title: {reel['title']}")
            print(f"    MP4 Reel Path: {reel['output_path']}")
            print(f"    SRT Subtitles Path: {reel['srt_path']}")

        print("\n==================================================")
        print(" PHASE 6 COMPLETED SUCCESSFULLY!")
        print("==================================================")

    except Exception as e:
        print(f"\n❌ Error during video rendering: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
