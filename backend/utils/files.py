import json
import os
import uuid
from pathlib import Path
from typing import Dict, Any

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "projects"

def get_project_dir(project_id: str) -> Path:
    p_dir = DATA_DIR / project_id
    p_dir.mkdir(parents=True, exist_ok=True)
    for sub in ["source", "audio", "transcript", "analysis", "output"]:
        (p_dir / sub).mkdir(exist_ok=True)
    return p_dir

def create_project_id() -> str:
    return f"proj_{uuid.uuid4().hex[:8]}"

def save_project_metadata(project_id: str, data: Dict[str, Any]) -> Path:
    p_dir = get_project_dir(project_id)
    meta_path = p_dir / "metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return meta_path

def load_project_metadata(project_id: str) -> Dict[str, Any]:
    p_dir = get_project_dir(project_id)
    meta_path = p_dir / "metadata.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"No metadata found for project {project_id}")
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)
