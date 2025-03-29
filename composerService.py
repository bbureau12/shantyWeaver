import json
import os
import ollama
from songRepository import ShantyRepository

class ShantyComposerService:
    def __init__(self):
        self.songRepository = ShantyRepository()
    
    def compose_shanty(self, context="The wind has died. I feel alone under a sky of stars.", model="mistral"):
        songs = self.songRepository.search_by_prompt(
            text="calm seas and a weary crew under twilight",
            tone="bittersweet",
            k=3,
            add_random=True
        )
        return self._compose_new_shanty(songs, context, model)

    def _build_shanty_prompt(self, seed_songs, context):
        prompt = "You are Shanty Weaver, an AI bard aboard a ship.\n"
        prompt += "Below are some traditional sea shanties:\n\n"
        
        for song in seed_songs:
            prompt += f"Title: {song['title']}\nTone: {song.get('tone')}\n"
            prompt += f"Lyrics:\n{song['lines']}\n\n"

        prompt += "---\n"
        prompt += f"Now write a new sea shanty inspired by these. Context: {context}\n"
        prompt += "Use a similar tone and structure.\n\n"
        prompt += "Title: [Give it a title]\nLyrics:\n"
        return prompt
    
    def _compose_new_shanty(self, seed_songs, context, model):
        prompt = self._build_shanty_prompt(seed_songs, context)
        
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']
    
    def log_generated_shanty(self, title, lyrics, context, model="mistral", log_path="shanty_songbook.json"):
        print("\n📜 Time to log this shanty.")
        rating = int(input("🌟 How would you rate this shanty (1–5)? "))
        notes = input("📝 Any comments or feedback? (optional): ")

        new_entry = {
            "title": title.strip(),
            "context": context.strip(),
            "lines": lyrics.strip(),
            "human_rating": rating,
            "ai_rating": "None",
            "reviewed_by": "None",
            "review_notes": notes,
            "source": "ai_generated",
            "model": model,
            "tags": ["ai", "generated"],
            "approved_for_future_inspiration": rating >= 4
        }

        # Load existing log
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = []

        # Append and save
        log_data.append(new_entry)
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        print("✅ Shanty logged successfully\n")

# Test
composer = ShantyComposerService()
new_song = composer.compose_shanty()
print("\n🎶 Our Creation:\n")
print(new_song)
