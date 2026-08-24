from backend.models.clip import ClipScores

def calculate_final_score(scores: ClipScores) -> float:
    """
    Calculates deterministic Clip Potential score based on plan formula:
    Hook (25%) + Standalone Context (25%) + Message Completeness (20%) +
    Emotional Impact (15%) + Curiosity (10%) + Shareability (5%).
    Multiplied by 10 for a scale of 0 to 100.
    """
    raw_weighted_score = (
        (scores.hook * 0.25) +
        (scores.standalone_context * 0.25) +
        (scores.message_completeness * 0.20) +
        (scores.emotional_impact * 0.15) +
        (scores.curiosity * 0.10) +
        (scores.shareability * 0.05)
    )
    final_score = round(raw_weighted_score * 10, 1)
    return max(0.0, min(100.0, final_score))
