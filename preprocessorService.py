import os
import json
import re
import ollama

class SemanticPreprocessorService:
    def __init__(self, preprocessor_dir="pre-processors", model="mistral"):
        self.preprocessor_dir = preprocessor_dir
        self.model = model
        self.preprocessors = self._load_preprocessors()

    def _load_preprocessors(self):
        loaded = []
        for file in os.listdir(self.preprocessor_dir):
            if file.endswith(".json"):
                path = os.path.join(self.preprocessor_dir, file)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["_file"] = os.path.splitext(file)[0]
                    loaded.append(data)
        return loaded

    def preprocess_song(self, song):
        results = {}
        for preprocessor in self.preprocessors:
            name = preprocessor.get("_file", "unnamed_preprocessor")
            result = self._apply_preprocessor(song, preprocessor)
            results[name] = result
        return results

    def _apply_preprocessor(self, song, preprocessor):
        instructions = preprocessor.get("instructions", "")
        output_format = json.dumps(preprocessor.get("output_format", {}), indent=2)
        name = preprocessor.get("name", "Semantic Evaluator")

        prompt = (
            f"{instructions}\n\n"
            f"Title: {song.get('title')}\n"
            f"Context: {song.get('context')}\n"
            f"Lyrics:\n{song.get('lines')}"
        )

        system_prompt = f"You are {name}. Only return a JSON object in this format:\n{output_format}"

        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        try:
            raw = response["message"]["content"]
            json_match = re.search(r"{.*}", raw, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {"error": "No JSON found"}
        except Exception as e:
            return {"error": str(e), "raw_response": response["message"]["content"]}

    def annotate_songbook(self, songbook_path="shanty_songbook.json"):
        with open(songbook_path, "r", encoding="utf-8") as f:
            songs = json.load(f)

        for song in songs:
            song["semantic_metadata"] = self.process_song(song)

        with open(songbook_path, "w", encoding="utf-8") as f:
            json.dump(songs, f, indent=2)

        print(f"✅ Semantic metadata added for {len(songs)} songs.")
