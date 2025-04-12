import json
import random
import ollama
from pathlib import Path

class LocationMuse:
    def __init__(self, locations_path='locations.json', model='mistral'):
        self.model = model
        self.locations_path = Path(locations_path)
        with self.locations_path.open('r', encoding='utf-8') as f:
            self.locations = json.load(f)
        random.shuffle(self.locations)  # Shuffle for natural variety

    def _build_system_prompt(self):
        return (
            "You are LocationMuse, the environmental observer aboard the Wanderlight.\n\n"
            "You are given a list of known locations, each with its wildlife, landmarks, and lore.\n"
            "Your job is to select one location that stands out as most vivid or meaningful in this moment.\n\n"
            "Then, based on the provided time of day, list no more than three wildlife and visible landmarks that would realistically be spotted at the present season and time, and only those included for that location.\n"
            "Choose details that feel atmospheric or meaningful — or return empty lists if nothing stands out.\n\n"
            "Only return valid JSON in this format:\n"
            "{\n"
            "  \"location\": \"exact name from the list\",\n"
            "  \"spotted_wildlife\": [string],\n"
            "  \"spotted_landmarks\": [string]\n"
            "}\n\n"
            "Do not include commentary or lists. List no more than three wildlife and visible landmarks.\n"
        )

    def choose_location_and_spottings(self, time_of_day="morning"):
        user_data = {
            "locations": self.locations,
            "time_of_day": time_of_day
        }

        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": json.dumps(user_data)}
        ]

        response = ollama.chat(model=self.model, messages=messages)
        content = response['message']['content'].strip()

        try:
            if content.lower() == "null":
                return None

            result = json.loads(content)

            # Validate location name
            valid_names = {loc["name"] for loc in self.locations}
            if result["location"] not in valid_names:
                raise ValueError(f"❌ Invalid location returned: {result['location']}")

            return result

        except Exception as e:
            print("❌ Failed to parse LocationMuse output:", e)
            print("Raw output:", content)
            return None


# Optional test runner
if __name__ == '__main__':
    muse = LocationMuse()
    result = muse.choose_location_and_spottings(time_of_day="evening")
    if result:
        print("\n🌅 Location Observation:")
        print(json.dumps(result, indent=2))
    else:
        print("🕯️ No location selected this time.")
