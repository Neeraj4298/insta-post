#!/usr/bin/env python3
import sys
import os
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.services.video_service import ingest_video
from backend.services.audio_service import extract_project_audio

def main():
    parser = argparse.ArgumentParser(description="Phase 1: Video Ingestion & Audio Extraction CLI")
    parser.add_argument("url_or_path", help="YouTube URL or path to local video file")
    parser.add_argument("--title", help="Optional project title", default=None)

    args = parser.parse_args()

    print("==================================================")
    print("      ClipForge Local - Phase 1 Pipeline         ")
    print("==================================================")
    print(f"Input source: {args.url_or_path}")

    try:
        print("\nStep 1: Ingesting video...")
        meta = ingest_video(args.url_or_path, title=args.title)
        print(f"✓ Video saved to: {meta['video_path']}")
        print(f"  Duration: {meta.get('duration_seconds')} seconds")

        print("\nStep 2: Extracting 16kHz WAV audio...")
        meta_audio = extract_project_audio(meta['project_id'])
        print(f"✓ Audio saved to: {meta_audio['audio_path']}")
        print(f"  Project ID: {meta['project_id']}")
        print(f"  Status: {meta_audio['status']}")

        print("\n==================================================")
        print(" PHASE 1 COMPLETED SUCCESSFULLY!")
        print("==================================================")

    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
