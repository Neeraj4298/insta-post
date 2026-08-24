#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.services.clip_service import rank_project_candidates
from backend.utils.files import load_project_metadata

def main():
    parser = argparse.ArgumentParser(description="Phase 4: Candidate Ranking & Deduplication CLI")
    parser.add_argument("project_id", help="Project ID analyzed in Phase 3")
    parser.add_argument("--min_score", help="Minimum clip score threshold (default: 65.0)", type=float, default=65.0)
    parser.add_argument("--limit", help="Maximum top clips to return (default: 10)", type=int, default=10)

    args = parser.parse_args()

    print("==================================================")
    print("      ClipForge Local - Phase 4 Ranking          ")
    print("==================================================")
    print(f"Project ID: {args.project_id}")
    print(f"Min Score Filter: {args.min_score}")
    print(f"Max Limit: {args.limit}")

    try:
        meta = load_project_metadata(args.project_id)
        print(f"Candidates Path: {meta.get('candidates_path')}")

        print("\nDeduplicating, spacing out, and ranking candidates...")
        ranked = rank_project_candidates(args.project_id, min_score=args.min_score, limit=args.limit)

        print(f"\n✓ Ranking complete! Selected {len(ranked)} top ranked clips.")

        print("\n🏆 Top Ranked Reels Ready for Review:")
        for idx, clip in enumerate(ranked, start=1):
            scores = clip['scores']
            print(f"\nRANK #{idx} | Score: {clip['final_score']} / 100")
            print(f"  Title: {clip['title']}")
            print(f"  Timestamps: {clip['start']}s -> {clip['end']}s (Duration: {clip['duration']}s)")
            print(f"  Opening Hook: \"{clip['hook']}\"")
            print(f"  Reason: {clip['reason']}")
            print(f"  Score Breakdown -> Hook: {scores['hook']}, Context: {scores['standalone_context']}, "
                  f"Completeness: {scores['message_completeness']}, Emotion: {scores['emotional_impact']}")

        print("\n==================================================")
        print(" PHASE 4 COMPLETED SUCCESSFULLY!")
        print("==================================================")

    except Exception as e:
        print(f"\n❌ Error during candidate ranking: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
