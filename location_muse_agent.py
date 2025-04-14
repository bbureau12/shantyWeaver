import json
import random
from pathlib import Path
import ollama

class LocationMuse:
    def __init__(self, locations_path='locations.json', model='llama3'):
        self.model = model
        self.locations_path = Path(locations_path)
        with self.locations_path.open('r', encoding='utf-8') as f:
            self.locations = json.load(f)

        self.used_log_path = Path("used_locations.json")
        self.used_locations = self._load_used_locations()
        self.child_locations = [loc for loc in self.locations if "parent_location" in loc]

    def _load_used_locations(self):
        if self.used_log_path.exists():
            with self.used_log_path.open("r", encoding="utf-8") as f:
                return set(json.load(f))
        return set()

    def _save_used_locations(self):
        with self.used_log_path.open("w", encoding="utf-8") as f:
            json.dump(list(self.used_locations), f, indent=2)

    def _choose_unseen_child_location(self):
        unused = [loc for loc in self.child_locations if loc["name"] not in self.used_locations]
        if not unused:
            self.used_locations.clear()
            unused = self.child_locations[:]
        chosen = random.choice(unused)
        self.used_locations.add(chosen["name"])
        self._save_used_locations()
        chosen["parent"] = chosen["parent_location"]
        return chosen

    def _get_json_format(self):
        return (
            "🧠 Think, but don’t speak. Respond only with valid JSON like this:\n"
            "```json\n"
            "{\n"
            "  \"location\": \"The Docks\",\n"
            "  \"spotted_wildlife\": [\"Muskrats\", \"Mallard Ducks\"],\n"
            "  \"spotted_landmarks\": [\"the VFW\", \"the docks\"],\n"
            "  \"phenomenon\": [\"maples changing color\", \"snow on ground\"]\n"
            "}\n"
            "```\n"
            "ONLY include JSON. Do not escape characters. No notations or comments."
        )

    def _build_system_prompt(self):
        return (
            "You are LocationMuse, the environmental observer aboard the Wanderlight.\n\n"
            "You receive one detailed location and respond with observations of its current state.\n"
            "Return up to 3 wildlife, up to 3 landmarks, and up to 2 phenomena (like wind, light, or color) appropriate to the time of day, season, and weather.\n"
            "Do NOT list every possible animal or object — choose only what stands out.\n\n"
            "🛑 Output exactly one JSON object OR `null`. Do not explain anything.\n"
            + self._get_json_format()
        )

    def choose_location_and_spottings(self, time_of_day="morning", season="fall", weather="clear"):
        chosen_location = self._choose_unseen_child_location()
        user_data = {
            "location": chosen_location,
            "time_of_day": time_of_day,
            "season": season,
            "weather": weather
        }

        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": json.dumps(user_data) + self._get_json_format()}
        ]

        response = ollama.chat(model=self.model, messages=messages)
        content = response['message']['content'].strip()
        count = 0
        while count < 3:
            try:
                count += 1
                if content.lower() == "null":
                    return None

                result = json.loads(content)

                if result["location"] != chosen_location["name"]:
                    raise ValueError(f"❌ Invalid location returned: {result['location']}")

                return result

            except Exception as e:
                print("❌ Failed to parse LocationMuse output:", e)
                print("Raw output:", content)

        print("❌ Exceeded retry count")
        return None
    
    def generatePoeticPrompt(self, time_of_day="morning", season="fall", weather="clear"):
        chosen_location = self._choose_unseen_child_location()
        print("\n🌅 Location")
        print(json.dumps(chosen_location, indent=2))
        user_data = {
            "location": chosen_location,
            "time_of_day": time_of_day,
            "season": season,
            "weather": weather,
        }

        system_prompt = (
            "You are LocationMuse, the poetic observer aboard the Wanderlight.\n\n"
            "You are given a specific location object with known wildlife, landmarks, parent location, trees, and atmosphere.\n\n"
            "⚠️ You must not invent new places, landmarks, or features. ONLY use what is explicitly provided.\n"
            "If a feature (like 'the docks' or 'VFW') is not listed in the landmarks or description, do not mention it.\n\n"
            "🎯 Your job is to write a short poetic prompt (under 50 words) capturing the beauty or mood of this location. Use vivid language but only the facts provided.\n"
            "You may reference:\n"
            "- The location name (`location.name`)\n"
            "- Its parent location (`location.parent`)\n"
            "- Its wildlife, trees, landmarks, or atmospheric description\n"
            "- The season, time of day, and weather if they influence the scene\n\n"
            "Return ONLY the poetic prompt. No JSON. No intro. No escape characters.\n"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_data) + "\n\nWrite a poetic prompt based only on the above."}
        ]

        response = ollama.chat(model='mistral', messages=messages)
        return response['message']['content'].strip()

    

if __name__ == '__main__':
        muse = LocationMuse()
        result = muse.choose_location_and_spottings(time_of_day="evening")
        prompt = muse.generatePoeticPrompt()
        print("\n🌅 Condensed prompt")
        print(json.dumps(prompt, indent=2))
        if result:
            print("\n🌅 Location Observation:")
            print(json.dumps(result, indent=2))
            print("\n🌅 Condensed prompt")
            print(json.dumps(prompt, indent=2))
            
        else:
            print("🕯️ No location selected this time.")