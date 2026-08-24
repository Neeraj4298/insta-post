from typing import List, Dict, Any

def check_overlap(clip_a: Dict[str, Any], clip_b: Dict[str, Any]) -> bool:
    """Checks if two clip timestamp intervals [start, end] overlap."""
    start_a, end_a = clip_a["start"], clip_a["end"]
    start_b, end_b = clip_b["start"], clip_b["end"]

    # Intervals overlap if start_a < end_b and start_b < end_a
    return max(start_a, start_b) < min(end_a, end_b)

def remove_overlapping_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rule 3: Remove overlapping candidates.
    Sorts candidates descending by final_score, then greedily selects non-overlapping clips.
    """
    sorted_cands = sorted(candidates, key=lambda c: c.get("final_score", 0), reverse=True)
    selected = []

    for cand in sorted_cands:
        has_overlap = False
        for existing in selected:
            if check_overlap(cand, existing):
                has_overlap = True
                break
        if not has_overlap:
            selected.append(cand)

    return selected

def apply_diversity_spacing(
    candidates: List[Dict[str, Any]],
    min_gap_seconds: float = 60.0
) -> List[Dict[str, Any]]:
    """
    Rule 5: Ensure candidate clips are spaced out across the video timeline.
    Prevents multiple clips from clustering within the exact same minute.
    """
    if not candidates:
        return []

    # Sort chronologically by start timestamp for spacing filter
    chrono = sorted(candidates, key=lambda c: c.get("start", 0))
    spaced = []

    for cand in chrono:
        if not spaced:
            spaced.append(cand)
        else:
            prev_start = spaced[-1]["start"]
            if (cand["start"] - prev_start) >= min_gap_seconds:
                spaced.append(cand)

    return spaced

def rank_and_filter_candidates(
    candidates: List[Dict[str, Any]],
    min_duration: float = 15.0,
    max_duration: float = 90.0,
    min_score: float = 65.0,
    min_gap_seconds: float = 60.0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Applies complete Phase 4 Candidate Ranking Engine pipeline:
    1. Duration filtering (15s - 90s)
    2. Minimum score filtering (>= 65.0, with fallback if few pass)
    3. Overlap removal (keep highest scoring)
    4. Diversity spacing (>= 60s gap)
    5. Top N selection sorted by final_score descending
    """
    if not candidates:
        return []

    # 1. Filter duration
    valid_dur = [
        c for c in candidates
        if min_duration <= (c.get("duration") or (c["end"] - c["start"])) <= max_duration
    ]

    if not valid_dur:
        valid_dur = candidates

    # 2. Score threshold filter (fallback to top candidates if none pass >= min_score)
    passed_score = [c for c in valid_dur if c.get("final_score", 0) >= min_score]
    if len(passed_score) < 3:
        # Fallback to top scored candidates if threshold is too strict for video
        passed_score = sorted(valid_dur, key=lambda c: c.get("final_score", 0), reverse=True)[:15]

    # 3. Overlap removal (prioritizes highest score)
    deduped = remove_overlapping_candidates(passed_score)

    # 4. Diversity spacing
    spaced = apply_diversity_spacing(deduped, min_gap_seconds=min_gap_seconds)
    if len(spaced) < 3 and len(deduped) >= 3:
        # If spacing is too aggressive, keep deduped list
        spaced = deduped

    # 5. Sort descending by final_score & cap to limit
    ranked = sorted(spaced, key=lambda c: c.get("final_score", 0), reverse=True)[:limit]

    return ranked
