#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.services.transcription_service import transcribe_project_audio
from backend.utils.files import load_project_metadata

def main():
    parser = argparse.ArgumentParser(description="Phase 2: Audio Transcription CLI")
    parser.add_argument("project_id", help="Project ID created in Phase 1 (e.g. proj_4b4bb86f)")
    parser.add_argument("--model", help="Whisper model size (tiny, base, small, medium)", default="base")
    parser.add_argument("--compute_type", help="Compute type (int8, float32)", default="int8")

    args = parser.parse_args()

    print("==================================================")
    print("      ClipForge Local - Phase 2 Transcription    ")
    print("==================================================")
    print(f"Project ID: {args.project_id}")
    print(f"Whisper Model: {args.model} ({args.compute_type})")

    try:
        meta = load_project_metadata(args.project_id)
        print(f"Audio Path: {meta.get('audio_path')}")

        print("\nStarting CPU INT8 transcription...")
        transcript_data = transcribe_project_audio(args.project_id, model_name=args.model, compute_type=args.compute_type)

        print(f"\n✓ Transcription complete!")
        print(f"  Detected Language: {transcript_data['language']}")
        print(f"  Duration: {transcript_data['duration_seconds']}s")
        print(f"  Segment count: {len(transcript_data['segments'])}")
        print("\nSample Segments:")
        for seg in transcript_data['segments'][:5]:
            print(f"  [{seg['start']}s -> {seg['end']}s] {seg['text']}")

        print("\n==================================================")
        print(" PHASE 2 COMPLETED SUCCESSFULLY!")
        print("==================================================")

    except Exception as e:
        print(f"\n❌ Error during transcription: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
