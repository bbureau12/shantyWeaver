import json
import random
import ollama
from pathlib import Path

class LocationMuse:
    def __init__(self, locations_path='locations.json', model='llama3'):
        self.model = model
        self.locations_path = Path(locations_path)
        with self.locations_path.open('r', encoding='utf-8') as f:
            self.locations = json.load(f)

        # Shuffle wildlife/landmarks within each location
        for loc in self.locations:
            random.shuffle(loc.get("wildlife", []))
            random.shuffle(loc.get("visible_landmarks", []))

        random.shuffle(self.locations)
        self.locations=self._remove_one_third_randomly(self.locations)  # Shuffle location order for variety and randomly remove some to cut overhead

    def _get_json_format(self):
         return (
            "🧠 Think, but don’t speak. Respond only with valid JSON like this:\n"
            "```json\n"
            "{\n"
            "  \"location\": \"The Docks\",\n"
            "  \"spotted_wildlife\": [\"Muskrats\", \"Mallard Ducks\"],\n"
            "  \"spotted_landmarks\": [\"the VFW\", \"the docks\"]\n"
            "  \"phenomenon\": [\"maples changing color\", \"snow on ground\"]\n"
            "}\n"
            "ONLY include JSON.  Do not escape characters.  No notations or comments."
            "```\n\n"
        )
    def _build_system_prompt(self):
        return (
            "You are LocationMuse, the environmental observer aboard the Wanderlight.\n\n"
            "You receive a list of real places and choose ONE that currently stands out.\n"
            "For that place, return **up to 3 wildlife**, **up to 3 landmarks** and **up to 2 phenomenon** that feel appropriate for the current time of day (remember, bats are not out during the day), weather, and seaon.\n"
            "Do NOT list every possible animal or object — choose only the ones appropriate for the time of day.  Only list landmarks available in the CURRENT location.\n"
            "It's okay to return an empty list if nothing stands out.\n\n"
            "🛑 You must output exactly one JSON object OR `null`. Do not explain anything.\n"
            +self._get_json_format())
    
    def _remove_one_third_randomly(self, arr):
        n = len(arr)
        count_to_remove = n // 2
        indices_to_remove = set(random.sample(range(n), count_to_remove))
        return [item for i, item in enumerate(arr) if i not in indices_to_remove]

    def choose_location_and_spottings(self, time_of_day="morning", season="fall", weather="clear"):
        user_data = {
            "locations": self.locations,
            "time_of_day": time_of_day,
            "season":season,
            "weather":weather
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

                # Validate the selected location exists in the input list
                valid_names = {loc["name"] for loc in self.locations}
                if result["location"] not in valid_names:
                    raise ValueError(f"❌ Invalid location returned: {result['location']}")

                return result

            except Exception as e:
                print("❌ Failed to parse LocationMuse output:", e)
                print("Raw output:", content)

        print("❌ Exceeded retry count")
        return None
    
    def generatePoeticPrompt(self, prompt, time_of_day="morning", season="fall", weather="clear"):
        user_data = {
            "locations": self.locations,
            "time_of_day": time_of_day,
            "season":season,
            "weather":weather,
            "prompt":prompt
        }

        messages = [
            {"role": "system", "content": "You are LocationMuse, the environmental observer aboard the Wanderlight."},
            {"role": "user", "content": json.dumps(user_data) + self._get_json_format()+"\n\n\n\n Generate a single poetic inspiration prompt for the above location.  This prompt should be no more than 50 words.  Make this just a string.  No JSON."}
        ]

        response = ollama.chat(model='mistral', messages=messages)
        return response['message']['content'].strip()


# Optional standalone test
if __name__ == '__main__':
    muse = LocationMuse()
    result = muse.choose_location_and_spottings(time_of_day="evening")
    prompt = muse.generatePoeticPrompt(result)
    if result:
        print("\n🌅 Location Observation:")
        print(json.dumps(result, indent=2))
        print("\n🌅 Condensed prompt")
        print(json.dumps(prompt, indent=2))
        
    else:
        print("🕯️ No location selected this time.")
