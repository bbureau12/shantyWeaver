import os
import json

class DependencyService:
    def __init__(self, facts_path="facts"):
        self.facts_path = facts_path
        self._cache = {}

    def _load_file(self, name):
        if name in self._cache:
            return self._cache[name]

        file_path = os.path.join(self.facts_path, f"{name}.json")
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._cache[name] = data
                return data
        except Exception as e:
            print(f"❌ Failed to load '{file_path}': {e}")
            return None

    def resolve(self, reference):
        """
        Resolves a reference string like:
        - "ship_data" → loads facts/ship_data.json
        - "ship_data:ship:masts" → loads a nested value from the JSON
        """
        if ":" not in reference:
            return self._load_file(reference)

        parts = reference.split(":")
        base = self._load_file(parts[0])
        if base is None:
            return None

        # Navigate down into the structure
        for key in parts[1:]:
            if isinstance(base, dict) and key in base:
                base = base[key]
            else:
                print(f"⚠️ Path not found in {reference}")
                return None

        return base
