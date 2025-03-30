import datetime
import json
import os
import re
import ollama
from songRepository import ShantyRepository

class ShantyComposerService:
    def __init__(self):
        self.songRepository = ShantyRepository()
    
    def compose_shanty(self, context="We're setting out from White Bear's Manitou Park.", model="mistral"):
        songs = self.songRepository.search_by_prompt(
            text="a windy day",
            tone="happy",
            k=3,
            add_random=True
        )
        new_song = self._compose_new_shanty(songs, context, model)
        if len(new_song) != 0:
            self._log_generated_shanty(new_song, context)

        return new_song

    def _build_shanty_prompt(self, seed_songs, context):
        prompt = "You are Shanty Weaver, an AI bard aboard a ship.\n"
        prompt += "Below are some traditional sea shanties:\n\n"
        
        for song in seed_songs:
            prompt += f"Title: {song['title']}\nTone: {song.get('tone')}\n"
            prompt += f"Lyrics:\n{song['lines']}\n\n"

        prompt += "---\n"
        prompt += f"Now write a new sea shanty inspired by these. Context: {context}\n"
        prompt += "Use a similar tone and structure.\n\n"
        prompt += "Feel free to add a chorus or sailor's chant if it fits the structure.\n"
        prompt += "Provide a JSON object describing the following:\n"
        prompt += "- title\n"
        prompt += "- tone (e.g. 'joyful', 'bittersweet')\n"
        prompt += "- lyrics (include full song as a single string, using literal '\\n' to represent line breaks; do not use real line breaks)\n"
        prompt += "- theme (e.g. 'loss', 'homecoming')\n"
        prompt += "- structure (e.g. 'verse-chorus')\n"
        prompt += "- tags (a list of useful descriptive keywords)\n"
        prompt += "Output only the JSON object. Do not include explanations or formatting outside the JSON.\n"
        prompt += 'example: {"title": "Song of the Sails", "tone": "bittersweet", "lyrics": "Oh the sails were torn\\nAs we left the bay...", "theme": "departure", "structure": "verse-chorus", "tags": ["farewell", "ocean", "crew"]}\n'
        return prompt
    
    def _compose_new_shanty(self, seed_songs, context, model):
        prompt = self._build_shanty_prompt(seed_songs, context)
        
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        raw_output = response['message']['content']

        # Try to extract the JSON using a regex block (in case markdown wrapping sneaks in)
        try:
            json_match = re.search(r'{.*}', raw_output, re.DOTALL)
            song_json = json.loads(json_match.group()) if json_match else json.loads(raw_output)
            return song_json
        except Exception as e:
            print("❌ Failed to parse LLM response:", e)
            print("Raw output:\n", raw_output)
            return None
        
    def _log_generated_shanty(self, song_data, context, model="mistral", log_path="shanty_songbook.json"):
        print("\n📜 Time to log this shanty.")

        # Add metadata
        song_data["context"] = context.strip()
        song_data["lines"] = song_data["lyrics"].replace("\\n", "\n").strip()
        song_data["human_rating"] = "None"
        song_data["ai_rating"] = "None"
        song_data["reviewed_by"] = "None"
        song_data["review_notes"] = "None"
        song_data["source"] = "ai_generated"
        song_data["model"] = model
        song_data["created_at"] = datetime.datetime.now().isoformat()
        song_data["approved_for_future_inspiration"] = "None"
        del song_data["lyrics"] 

        # Ensure the tag 'generated' is added
        tags = set(song_data.get("tags", []))
        tags.update(["ai", "generated"])
        song_data["tags"] = list(tags)

        # Load existing log
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        else:
            log_data = []

        # Append and save
        log_data.append(song_data)
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)

        print("✅ Shanty logged successfully\n")

# Test
composer = ShantyComposerService()
new_song = composer.compose_shanty()
print("\n🎶 Our Creation:\n")
print(new_song)
