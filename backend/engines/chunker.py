from typing import List, Dict, Any

def create_semantic_chunks(
    segments: List[Dict[str, Any]],
    target_duration: float = 180.0,  # 3 minutes target
    max_duration: float = 300.0     # 5 minutes maximum
) -> List[Dict[str, Any]]:
    """
    Groups transcript segments into coherent semantic chunks.
    Each chunk contains start, end, duration, and concatenated text.
    """
    if not segments:
        return []

    chunks = []
    current_chunk_segments = []
    current_start = segments[0]["start"]

    for i, seg in enumerate(segments):
        current_chunk_segments.append(seg)
        chunk_duration = seg["end"] - current_start

        # Check pause gap to next segment
        has_pause = False
        if i < len(segments) - 1:
            next_start = segments[i + 1]["start"]
            if (next_start - seg["end"]) >= 1.5:  # 1.5 second pause indicates thought boundary
                has_pause = True

        # Check sentence ending punctuation (. ? !)
        text = seg.get("text", "").strip()
        is_sentence_end = text.endswith(".") or text.endswith("?") or text.endswith("!")

        # Decide if we should end the current chunk
        should_split = (
            (chunk_duration >= target_duration and (is_sentence_end or has_pause)) or
            (chunk_duration >= max_duration)
        )

        if should_split:
            chunk_text = " ".join(s["text"].strip() for s in current_chunk_segments)
            chunks.append({
                "chunk_id": f"chunk_{len(chunks) + 1}",
                "start": round(current_start, 2),
                "end": round(seg["end"], 2),
                "duration": round(seg["end"] - current_start, 2),
                "segments": current_chunk_segments,
                "text": chunk_text
            })
            current_chunk_segments = []
            if i < len(segments) - 1:
                current_start = segments[i + 1]["start"]

    # Remainder segments
    if current_chunk_segments:
        chunk_text = " ".join(s["text"].strip() for s in current_chunk_segments)
        chunks.append({
            "chunk_id": f"chunk_{len(chunks) + 1}",
            "start": round(current_start, 2),
            "end": round(current_chunk_segments[-1]["end"], 2),
            "duration": round(current_chunk_segments[-1]["end"] - current_start, 2),
            "segments": current_chunk_segments,
            "text": chunk_text
        })

    return chunks
