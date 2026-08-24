#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.services.analysis_service import analyze_project_transcript
from backend.utils.files import load_project_metadata

def main():
    parser = argparse.ArgumentParser(description="Phase 3: Clip Intelligence & Candidate Detection CLI")
    parser.add_argument("project_id", help="Project ID created in Phase 1 & transcribed in Phase 2")
    parser.add_argument("--model", help="Local LLM model name if Ollama is running", default="llama3")

    args = parser.parse_args()

    print("==================================================")
    print("      ClipForge Local - Phase 3 Intelligence     ")
    print("==================================================")
    print(f"Project ID: {args.project_id}")

    try:
        meta = load_project_metadata(args.project_id)
        print(f"Transcript Path: {meta.get('transcript_path')}")

        print("\nAnalyzing transcript chunks & scoring candidate moments...")
        candidates = analyze_project_transcript(args.project_id, model_name=args.model)

        print(f"\n✓ Analysis complete! Found {len(candidates)} candidates.")

        print("\nTop Candidate Clips:")
        for idx, cand in enumerate(candidates[:5], start=1):
            scores = cand['scores']
            print(f"\n[{idx}] Candidate ID: {cand['candidate_id']}")
            print(f"    Title: {cand['title']}")
            print(f"    Timestamps: {cand['start']}s -> {cand['end']}s (Duration: {cand['duration']}s)")
            print(f"    Opening Hook: \"{cand['hook']}\"")
            print(f"    Clip Potential Score: {cand['final_score']} / 100")
            print(f"    Breakdown -> Hook: {scores['hook']}, Context: {scores['standalone_context']}, "
                  f"Completeness: {scores['message_completeness']}, Emotion: {scores['emotional_impact']}")

        print("\n==================================================")
        print(" PHASE 3 COMPLETED SUCCESSFULLY!")
        print("==================================================")

    except Exception as e:
        print(f"\n❌ Error during intelligence analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
