import json
import httpx
from typing import Dict, Any, Optional, List

OLLAMA_URL = "http://localhost:11434/api/generate"

def is_ollama_available() -> bool:
    try:
        res = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        return res.status_code == 200
    except Exception:
        return False

def analyze_chunk_with_ollama(
    chunk_text: str,
    start_time: float,
    end_time: float,
    model_name: str = "llama3"
) -> Optional[List[Dict[str, Any]]]:
    """
    Calls local Ollama instance if active to detect viral clip candidates.
    Returns parsed JSON candidate objects or None if unavailable/error.
    """
    if not is_ollama_available():
        return None

    prompt = f"""
System: You are an expert short-form video editor and content analyst specializing in podcasts, sermons, and educational videos.
Analyze the following transcript chunk starting at {start_time}s and ending at {end_time}s.

Identify 1 to 3 strong short-form clip candidates (duration between 15s and 90s) that make sense standalone.

Return ONLY a JSON array with no extra markdown or explanations, in this exact format:
[
  {{
    "start": 12.5,
    "end": 45.0,
    "title": "Catchy Reel Title",
    "hook": "Opening hook sentence",
    "reason": "Why this clip works standalone",
    "scores": {{
      "hook": 8.5,
      "standalone_context": 9.0,
      "message_completeness": 8.0,
      "emotional_impact": 7.5,
      "curiosity": 8.0,
      "shareability": 7.0
    }}
  }}
]

TRANSCRIPT CHUNK:
{chunk_text}
"""
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        response = httpx.post(OLLAMA_URL, json=payload, timeout=60.0)
        if response.status_code == 200:
            resp_json = response.json()
            raw_text = resp_json.get("response", "").strip()
            parsed = json.loads(raw_text)
            if isinstance(parsed, list):
                return parsed
    except Exception:
        pass

    return None
