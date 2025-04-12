import os
import json
from datetime import datetime

class EvaluationLogger:
    def __init__(self, log_dir="log", filename="nyx_evaluations.jsonl"):
        self.log_dir = log_dir
        self.log_path = os.path.join(log_dir, filename)
        os.makedirs(log_dir, exist_ok=True)

    def log(self, song_title, evaluator_name, result, lyrics):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "song_title": song_title,
            "evaluator": evaluator_name,
            "score": result.get("score"),
            "reasons": result.get("reasons", []),
            "suggestions": result.get("suggestions", []),
            "lyrics_examined": lyrics
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
