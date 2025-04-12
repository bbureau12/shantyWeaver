import json
import ollama
from pathlib import Path

class LocationMuse:
    def __init__(self, locations_path='locations.json', model='mistral'):
        self.model = model
        with open(locations_path, 'r', encoding='utf-8') as f:
            self.locations = json.load(f)
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self):
        return (
            "You are LocationMuse, the poetic mind of the Wanderlight ship's crew.\n"
            "You receive a list of locations with rich details and decide whether one of them inspires a poetic spark.\n\n"
            "Only choose from the locations provided. Do not invent or hallucinate new locations.\n"
            "If none seem especially poetic at this moment, return null.\n\n"
            "If one stands out due to its landmarks, sounds, lore, or setting, select it and describe a poetic inspiration (called a 'spark').\n\n"
            "Respond ONLY with a strict JSON object, or null if nothing stands out.\n\n"
            "Format:\n"
            +"{"
            +"  \"location\": \"name from list\","
            +"  \"spark\": {"
            +"    \"inspiration\": \"A poetic line or image derived from the place.\""
            "  }"+
            "}\n"+
            "or null."
        )

    def choose_location_and_spark(self):
        user_input = {
            "locations": self.locations
        }
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": json.dumps(user_input)}
        ]

        response = ollama.chat(model=self.model, messages=messages)
        content = response['message']['content']

        try:
            if content.strip().lower() == "null":
                return None
            return json.loads(content)
        except Exception as e:
            print("❌ Failed to parse LocationMuse output:", e)
            print("Raw output:", content)
            return None


if __name__ == '__main__':
    muse = LocationMuse()
    result = muse.choose_location_and_spark()
    if result:
        print("\n🎇 Location Spark:")
        print(json.dumps(result, indent=2))
    else:
        print("🕯️ No location spark this time.")
