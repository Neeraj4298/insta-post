import re
import uuid
from typing import List, Dict, Any
from backend.models.clip import ClipCandidate, ClipScores
from backend.engines.scoring_engine import calculate_final_score
from backend.services.llm_service import analyze_chunk_with_ollama

EMOTIONAL_HOOK_KEYWORDS = [
    "never", "always", "secret", "truth", "remember", "stop", "don't", "reason",
    "because", "imagine", "listen", "key", "mistake", "change", "power", "god",
    "faith", "life", "future", "believe", "heart", "today", "understand"
]

def generate_heuristic_candidates(chunk: Dict[str, Any], project_id: str) -> List[ClipCandidate]:
    """
    Heuristic rule-engine to extract candidates when local LLM is unavailable.
    Scans segment sequences for 15s-90s standalone windows with strong hook openers.
    """
    segments = chunk.get("segments", [])
    if not segments:
        return []

    candidates = []
    num_segs = len(segments)

    for start_idx in range(num_segs):
        start_seg = segments[start_idx]
        start_time = start_seg["start"]
        hook_text = start_seg.get("text", "").strip()

        # Check hook strength
        text_lower = hook_text.lower()
        hook_score = 6.0
        if any(kw in text_lower for kw in EMOTIONAL_HOOK_KEYWORDS):
            hook_score += 2.0
        if hook_text.endswith("?") or text_lower.startswith(("why", "how", "what", "if", "when")):
            hook_score += 1.5

        hook_score = min(10.0, hook_score)

        for end_idx in range(start_idx, num_segs):
            end_seg = segments[end_idx]
            end_time = end_seg["end"]
            duration = end_time - start_time

            if 15.0 <= duration <= 90.0:
                clip_text_segs = [s["text"].strip() for s in segments[start_idx:end_idx + 1]]
                full_clip_text = " ".join(clip_text_segs)

                # Standalone Context & Completeness heuristics
                last_text = end_seg.get("text", "").strip()
                is_clean_end = last_text.endswith(".") or last_text.endswith("!") or last_text.endswith("?")

                completeness_score = 8.5 if is_clean_end else 6.0
                context_score = 7.5 + (0.5 if len(clip_text_segs) >= 3 else 0.0)
                emotion_score = 7.0 + min(2.5, sum(1 for kw in EMOTIONAL_HOOK_KEYWORDS if kw in full_clip_text.lower()) * 0.4)
                curiosity_score = min(10.0, hook_score * 0.9)
                shareability_score = min(10.0, (emotion_score + hook_score) / 2.0)

                scores = ClipScores(
                    hook=round(hook_score, 1),
                    standalone_context=round(min(10.0, context_score), 1),
                    message_completeness=round(min(10.0, completeness_score), 1),
                    emotional_impact=round(min(10.0, emotion_score), 1),
                    curiosity=round(curiosity_score, 1),
                    shareability=round(shareability_score, 1)
                )

                final_score = calculate_final_score(scores)

                # Only consider candidates with potential >= 50
                if final_score >= 50.0:
                    cand_id = f"cand_{uuid.uuid4().hex[:8]}"
                    first_words = hook_text.split()[:6]
                    generated_title = " ".join(first_words).title() or "Extracted Highlight Clip"

                    candidate = ClipCandidate(
                        candidate_id=cand_id,
                        project_id=project_id,
                        start=round(start_time, 2),
                        end=round(end_time, 2),
                        duration=round(duration, 2),
                        title=generated_title,
                        hook=hook_text,
                        reason="Identified standalone moment with strong hook and message resolution.",
                        scores=scores,
                        final_score=final_score
                    )
                    candidates.append(candidate)

                # Skip to avoid redundant adjacent sub-windows
                break

    return candidates

def detect_candidates_in_chunks(
    chunks: List[Dict[str, Any]],
    project_id: str,
    model_name: str = "llama3"
) -> List[ClipCandidate]:
    """
    Processes semantic transcript chunks to detect candidate reel moments.
    Uses local LLM (Ollama) if available, with heuristic fallback.
    """
    all_candidates = []

    for chunk in chunks:
        # Try local LLM first
        llm_raw_cands = analyze_chunk_with_ollama(
            chunk_text=chunk["text"],
            start_time=chunk["start"],
            end_time=chunk["end"],
            model_name=model_name
        )

        if llm_raw_cands:
            for item in llm_raw_cands:
                try:
                    start_t = float(item.get("start", chunk["start"]))
                    end_t = float(item.get("end", chunk["end"]))
                    duration = round(end_t - start_t, 2)
                    if 15.0 <= duration <= 90.0:
                        sc_raw = item.get("scores", {})
                        scores = ClipScores(
                            hook=float(sc_raw.get("hook", 7.0)),
                            standalone_context=float(sc_raw.get("standalone_context", 7.0)),
                            message_completeness=float(sc_raw.get("message_completeness", 7.0)),
                            emotional_impact=float(sc_raw.get("emotional_impact", 7.0)),
                            curiosity=float(sc_raw.get("curiosity", 7.0)),
                            shareability=float(sc_raw.get("shareability", 7.0))
                        )
                        final_score = calculate_final_score(scores)
                        all_candidates.append(
                            ClipCandidate(
                                candidate_id=f"cand_{uuid.uuid4().hex[:8]}",
                                project_id=project_id,
                                start=round(start_t, 2),
                                end=round(end_t, 2),
                                duration=duration,
                                title=item.get("title", "AI Selected Clip"),
                                hook=item.get("hook", ""),
                                reason=item.get("reason", "Selected by local LLM analysis."),
                                scores=scores,
                                final_score=final_score
                            )
                        )
                except Exception:
                    pass
        else:
            # Fallback heuristic engine
            h_cands = generate_heuristic_candidates(chunk, project_id)
            all_candidates.extend(h_cands)

    return all_candidates
